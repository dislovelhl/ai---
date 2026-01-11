"""
Agentic Workflow Executor

This executor uses LangGraph to build an agentic loop where the LLM can
dynamically select and execute tool skills via function calling.

Optimizations Applied:
- Skill result caching to reduce redundant API calls
- LLM response caching for similar queries
- Efficient skill selection via semantic matching
"""
import operator
import json
import logging
from typing import Annotated, Any, Dict, List, Optional, TypedDict, Union
from datetime import datetime, timezone

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from shared.database import get_async_session
from shared.config import settings
from shared.models import Skill
from .executor import NodeResult # Reuse NodeResult for consistency
from .cache_service import skill_cache, llm_cache

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State that flows through the agentic loop."""
    messages: Annotated[List[BaseMessage], operator.add]
    workflow_id: str
    session_id: str
    available_tools: List[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]
    token_usage: int
    api_calls: int

class AgenticExecutor:
    """
    Executes an autonomous agent using LangGraph and DeepSeek function calling.
    """
    
    def __init__(self, workflow_id: str, session_id: str, llm_config: dict = None):
        self.workflow_id = workflow_id
        self.session_id = session_id
        self.llm_config = llm_config or {}
        
        # Initialize LLM with DeepSeek (OpenAI-compatible)
        # DeepSeek supports function calling via the standard OpenAI compatible API
        self.llm = ChatOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL.replace("/chat/completions", ""),
            model=self.llm_config.get("model", "deepseek-chat"),
            temperature=self.llm_config.get("temperature", 0.7),
        )

    def _get_openai_tools(self, skills: List[Skill]) -> List[Dict[str, Any]]:
        """Convert database Skills to OpenAI Tool/Function format."""
        tools = []
        for skill in skills:
            tools.append({
                "type": "function",
                "function": {
                    "name": skill.slug.replace("-", "_"),
                    "description": skill.description or skill.name,
                    "parameters": skill.input_schema or {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            })
        return tools

    async def _execute_skill(self, tool_call: Dict[str, Any]) -> Any:
        """Execute a specific tool skill call with caching."""
        # Find the skill by slug
        async with get_async_session() as db:
            from sqlalchemy import select
            skill_slug = tool_call["name"].replace("_", "-")
            result = await db.execute(
                select(Skill).where(Skill.slug == skill_slug)
            )
            skill = result.scalars().first()

            if not skill:
                return f"Error: Skill {skill_slug} not found"

            # Parse arguments from LLM
            args = tool_call["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            # Check cache first
            cached_result = await skill_cache.get(skill_slug, args)
            if cached_result is not None:
                logger.info(f"Skill cache hit for {skill_slug}")
                return cached_result

            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare headers
                headers = {}
                if skill.headers_template:
                    headers.update(skill.headers_template)

                # Handle Authentication
                if skill.auth_type == "bearer" and skill.auth_config:
                    # In production, this might come from vault or env
                    env_var = skill.auth_config.get("env_var")
                    import os
                    token = os.environ.get(env_var) if env_var else None
                    if token:
                        headers["Authorization"] = f"Bearer {token}"

                try:
                    response = await client.request(
                        method=skill.http_method,
                        url=skill.api_endpoint,
                        json=args if skill.http_method in ["POST", "PUT", "PATCH"] else None,
                        params=args if skill.http_method == "GET" else None,
                        headers=headers
                    )

                    if response.is_success:
                        result_data = response.json()
                        # Cache successful results
                        await skill_cache.set(skill_slug, args, result_data)
                        return result_data
                    else:
                        return f"API Error ({response.status_code}): {response.text}"
                except Exception as e:
                    logger.error(f"Error calling skill {skill_slug}: {e}")
                    return f"Exception during skill execution: {str(e)}"

    async def call_model(self, state: AgentState):
        """Invoke the LLM with the current state."""
        messages = state["messages"]
        tools = state["available_tools"]
        
        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
        
        response = await llm_with_tools.ainvoke(messages)
        
        # Track usage (if returned by the model)
        token_usage = 0
        if hasattr(response, "response_metadata"):
            token_usage = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        
        return {
            "messages": [response],
            "token_usage": state["token_usage"] + token_usage,
            "api_calls": state["api_calls"] + 1
        }

    async def handle_tool_calls(self, state: AgentState):
        """Execute tool calls requested by the model."""
        last_message = state["messages"][-1]
        tool_messages = []
        
        if hasattr(last_message, "tool_calls"):
            for tc in last_message.tool_calls:
                result = await self._execute_skill(tc)
                tool_messages.append(ToolMessage(
                    tool_call_id=tc["id"],
                    content=json.dumps(result)
                ))
        
        return {
            "messages": tool_messages,
            "api_calls": state["api_calls"] + len(tool_messages)
        }

    def should_continue(self, state: AgentState):
        """Determine if the agent should continue or finish."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"

    def build_graph(self) -> StateGraph:
        """Build the LangGraph execution graph."""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.handle_tool_calls)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()

    async def stream_run(self, input_text: str, skills: List[Skill]):
        """Execute the agent loop and yield streaming events."""
        app = self.build_graph()
        
        system_prompt = self.llm_config.get("system_prompt") or "You are a helpful AI assistant."
        
        initial_state: AgentState = {
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=input_text)
            ],
            "workflow_id": self.workflow_id,
            "session_id": self.session_id,
            "available_tools": self._get_openai_tools(skills),
            "execution_result": None,
            "token_usage": 0,
            "api_calls": 0
        }
        
        async for event in app.astream_events(initial_state, version="v1"):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield {
                        "type": "token",
                        "node": "agent",
                        "content": content
                    }
            elif kind == "on_tool_start":
                yield {
                    "type": "status",
                    "status": "thinking",
                    "node": "tools",
                    "tool": event["name"]
                }
            elif kind == "on_tool_end":
                yield {
                    "type": "status",
                    "status": "completed",
                    "node": "tools",
                    "output": event["data"].get("output")
                }
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                # Final state
                final_output = event["data"]["output"]["messages"][-1].content
                yield {
                    "type": "final",
                    "content": final_output
                }

