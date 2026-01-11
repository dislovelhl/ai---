"""
Chat Router with Multi-Agent Optimizations

Optimizations Applied:
- Semantic skill selection (loads only relevant skills)
- Skill selector initialization on first request
- Memory context integration with caching
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import uuid
import logging

from sqlalchemy import select
from shared.database import get_async_session
from shared.models import AgentWorkflow, AgentExecution, Skill, User
from ..schemas import ExecutionResponse, ExecutionSummary
from ..core.agentic_executor import AgenticExecutor
from ..core.memory_service import memory_service
from ..core.cache_service import skill_selector

from sse_starlette.sse import EventSourceResponse
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Track if skill selector is initialized
_skill_selector_initialized = False


async def ensure_skill_selector_initialized(db: AsyncSession):
    """Initialize skill selector with all skills on first request."""
    global _skill_selector_initialized
    if _skill_selector_initialized:
        return

    skills_result = await db.execute(
        select(Skill).where(Skill.is_active == True)
    )
    skills = skills_result.scalars().all()

    # Convert to dict format
    skill_dicts = [
        {
            "id": str(s.id),
            "name": s.name,
            "slug": s.slug,
            "description": s.description or "",
            "skill_obj": s  # Keep reference to actual Skill object
        }
        for s in skills
    ]

    # Initialize with batch embedding
    async def embed_fn(texts):
        return await memory_service.batch_embed(texts)

    await skill_selector.initialize(skill_dicts, embed_fn)
    _skill_selector_initialized = True
    logger.info(f"Skill selector initialized with {len(skill_dicts)} skills")

@router.post("/{workflow_id}/stream")
async def stream_agent(
    workflow_id: str,
    message: Dict[str, str],
    request: Request,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Stream agent execution events using Server-Sent Events (SSE).

    Optimizations:
    - Uses semantic skill selection (only loads relevant skills)
    - Memory context retrieved with cached embeddings
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    workflow = await db.get(AgentWorkflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Ensure skill selector is initialized
    await ensure_skill_selector_initialized(db)

    # Get relevant context from memory
    context_memories = await memory_service.search_memory(db, workflow_id, message["content"])
    context_str = "\n".join([m["content"] for m in context_memories])

    # Get query embedding for skill selection
    query_embedding = await memory_service._get_embedding_async(message["content"])

    # Select relevant skills (top 5 most relevant)
    relevant_skill_dicts = await skill_selector.select_relevant(
        message["content"],
        query_embedding,
        top_k=5
    )
    # Extract actual Skill objects
    skills = [s["skill_obj"] for s in relevant_skill_dicts if "skill_obj" in s]

    logger.info(f"Selected {len(skills)} relevant skills for query")

    executor = AgenticExecutor(
        workflow_id=workflow_id,
        session_id=session_id,
        llm_config={
            "model": workflow.llm_model,
            "temperature": workflow.temperature,
            "system_prompt": f"{workflow.system_prompt}\n\nRelevant Context:\n{context_str}"
        }
    )

    async def event_generator():
        async for event in executor.stream_run(message["content"], list(skills)):
            if await request.is_disconnected():
                break
            yield {
                "event": event["type"],
                "data": json.dumps(event)
            }

    return EventSourceResponse(event_generator())



@router.post("/{workflow_id}/chat")
async def chat_with_agent(
    workflow_id: str,
    message: Dict[str, str],
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Chat with an agent using dynamic skill selection.

    Optimizations:
    - Semantic skill selection (Phase 3.2 implemented!)
    - Embedding caching for repeated queries
    - Skill result caching
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    # 1. Look up the workflow
    workflow = await db.get(AgentWorkflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # 2. Ensure skill selector is initialized
    await ensure_skill_selector_initialized(db)

    # 3. Retrieve chat history
    history = await memory_service.get_chat_history(workflow_id, session_id)

    # 4. Integrate RAG - Search memory for relevant context
    context_memories = await memory_service.search_memory(db, workflow_id, message["content"])
    context_str = "\n".join([m["content"] for m in context_memories])

    # 5. Semantic skill selection (optimized - only loads relevant skills)
    query_embedding = await memory_service._get_embedding_async(message["content"])
    relevant_skill_dicts = await skill_selector.select_relevant(
        message["content"],
        query_embedding,
        top_k=5
    )
    skills = [s["skill_obj"] for s in relevant_skill_dicts if "skill_obj" in s]
    logger.info(f"Selected {len(skills)} relevant skills for chat")

    # 6. Execute Agentic Loop
    executor = AgenticExecutor(
        workflow_id=workflow_id,
        session_id=session_id,
        llm_config={
            "model": workflow.llm_model,
            "temperature": workflow.temperature,
            "system_prompt": f"{workflow.system_prompt}\n\nRelevant Context:\n{context_str}"
        }
    )

    result = await executor.run(message["content"], list(skills))

    # 7. Store in memories/logs
    await memory_service.add_chat_message(workflow_id, session_id, "user", message["content"])
    await memory_service.add_chat_message(workflow_id, session_id, "assistant", result["output"])

    # 8. Create an execution record for history
    execution = AgentExecution(
        workflow_id=workflow.id,
        user_id=workflow.user_id,
        status="completed",
        input_data={"message": message["content"]},
        output_data={"response": result["output"]},
        execution_log=result["history"],
        token_usage=result["token_usage"],
        total_api_calls=result["api_calls"],
        trigger_type="chat"
    )
    db.add(execution)
    await db.commit()

    return {
        "session_id": session_id,
        "response": result["output"],
        "token_usage": result["token_usage"],
        "skills_used": len(skills)  # Added for monitoring
    }

@router.get("/{workflow_id}/history/{session_id}")
async def get_chat_session_history(
    workflow_id: str,
    session_id: str
):
    """Get chat history for a session."""
    history = await memory_service.get_chat_history(workflow_id, session_id)
    return {"history": history}

@router.delete("/{workflow_id}/session/{session_id}")
async def clear_session(
    workflow_id: str,
    session_id: str
):
    """Clear chat history for a session."""
    await memory_service.clear_chat_history(workflow_id, session_id)
    return {"status": "success"}


@router.get("/stats/cache")
async def get_cache_stats():
    """
    Get cache statistics for monitoring and optimization.

    Returns stats for:
    - Embedding cache (local + Redis)
    - Skill cache
    - LLM response cache
    - Skill selector
    """
    from ..core.cache_service import skill_cache, llm_cache, skill_selector

    return {
        "embedding_cache": memory_service.get_cache_stats(),
        "llm_cache": llm_cache.get_stats(),
        "skill_selector": {
            "initialized": _skill_selector_initialized,
            "indexed_skills": len(skill_selector.skill_embeddings)
        }
    }
