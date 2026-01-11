"""
LangGraph-based Workflow Engine (Optimized)

Translates React Flow graph definitions into executable LangGraph state machines.
This provides a robust, industry-standard approach to agent orchestration.

Optimizations Applied:
1. Parallel node execution for independent branches
2. Workflow graph caching to avoid recompilation
3. Performance metrics tracking per node
4. Async skill execution with caching
5. Topological layer detection for parallelism
"""
import operator
import asyncio
import hashlib
import time
from typing import Annotated, Any, TypedDict, List, Set, Dict, Optional
from datetime import datetime, timezone
from collections import defaultdict
import logging
import httpx

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Optional: Production-grade PostgresSaver
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    POSTGRES_SAVER_AVAILABLE = True
except ImportError:
    POSTGRES_SAVER_AVAILABLE = False
    AsyncPostgresSaver = None

from app.core.guardrails import guardrails
from app.core.cache_service import skill_cache
from shared.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# STATE DEFINITION
# =============================================================================

class AgentState(TypedDict):
    """State that flows through the LangGraph workflow."""
    messages: Annotated[list[BaseMessage], operator.add]
    current_node: str
    results: dict[str, Any]
    token_usage: int
    api_calls: int
    # Performance tracking
    node_timings: dict[str, float]
    parallel_groups: list[list[str]]


class NodeMetrics(TypedDict):
    """Performance metrics for a single node execution."""
    node_id: str
    node_type: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    error: Optional[str]


# =============================================================================
# WORKFLOW GRAPH CACHE
# =============================================================================

class WorkflowGraphCache:
    """
    Cache compiled LangGraph workflows to avoid recompilation.

    Caches based on workflow config hash for fast lookup.
    """

    _cache: Dict[str, StateGraph] = {}
    _max_size: int = 100

    @classmethod
    def _compute_hash(cls, workflow_config: dict) -> str:
        """Compute deterministic hash of workflow config."""
        import json
        config_str = json.dumps(workflow_config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    @classmethod
    def get(cls, workflow_config: dict) -> Optional[StateGraph]:
        """Get cached compiled graph if available."""
        config_hash = cls._compute_hash(workflow_config)
        return cls._cache.get(config_hash)

    @classmethod
    def set(cls, workflow_config: dict, graph: StateGraph) -> None:
        """Cache compiled graph."""
        if len(cls._cache) >= cls._max_size:
            # Evict oldest entry
            oldest = next(iter(cls._cache))
            del cls._cache[oldest]

        config_hash = cls._compute_hash(workflow_config)
        cls._cache[config_hash] = graph
        logger.debug(f"Cached workflow graph: {config_hash[:8]}...")

    @classmethod
    def get_stats(cls) -> dict:
        """Get cache statistics."""
        return {
            "cached_workflows": len(cls._cache),
            "max_size": cls._max_size
        }


# =============================================================================
# LANGGRAPH WORKFLOW ENGINE (OPTIMIZED)
# =============================================================================

class LangGraphWorkflowEngine:
    """
    Compiles React Flow graph configurations into executable LangGraph workflows.

    Supports node types:
    - input: Entry point, initializes state
    - output: Exit point, returns final results
    - llm: DeepSeek LLM call with prompt template
    - tool/skill: External API call
    - transform: Data transformation
    - parallel: Fan-out to multiple nodes (NEW)

    Optimizations:
    - Parallel execution of independent nodes
    - Workflow graph caching
    - Skill result caching
    - Performance metrics tracking
    """

    def __init__(self, workflow_config: dict, llm_config: dict = None):
        self.config = workflow_config
        self.llm_config = llm_config or {}

        # Initialize LLM (DeepSeek via OpenAI-compatible API)
        self.llm = ChatOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL.replace("/chat/completions", ""),
            model=self.llm_config.get("model", "deepseek-chat"),
            temperature=self.llm_config.get("temperature", 0.7),
        )

        # Parse nodes and edges
        self.nodes = {n["id"]: n for n in workflow_config.get("nodes", [])}
        self.edges = workflow_config.get("edges", [])

        # Build adjacency lists
        self.outgoing: dict[str, list[str]] = defaultdict(list)
        self.incoming: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            self.outgoing[src].append(tgt)
            self.incoming[tgt].append(src)

        # Compute parallel execution groups
        self.parallel_layers = self._compute_parallel_layers()

        # Metrics collection
        self.node_metrics: List[NodeMetrics] = []

    def _compute_parallel_layers(self) -> List[Set[str]]:
        """
        Compute topological layers for parallel execution.

        Nodes in the same layer have no dependencies on each other
        and can be executed in parallel.

        Returns:
            List of sets, where each set contains node IDs that can run in parallel
        """
        if not self.nodes:
            return []

        # Find all node IDs
        all_nodes = set(self.nodes.keys())

        # Track remaining nodes and their dependencies
        remaining = all_nodes.copy()
        in_degree = {node: len(self.incoming[node]) for node in all_nodes}

        layers = []

        while remaining:
            # Find nodes with no remaining dependencies
            ready = {n for n in remaining if in_degree[n] == 0}

            if not ready:
                # Cycle detected, break with remaining nodes in single layer
                logger.warning("Cycle detected in workflow graph")
                layers.append(remaining)
                break

            layers.append(ready)
            remaining -= ready

            # Update in-degrees for remaining nodes
            for node in ready:
                for successor in self.outgoing[node]:
                    if successor in remaining:
                        in_degree[successor] -= 1

        logger.info(f"Computed {len(layers)} parallel layers: {[len(l) for l in layers]}")
        return layers

    def _create_node_function(self, node_id: str, node_type: str, node_data: dict):
        """Factory to create executable functions for each visual node."""

        async def node_executor(state: AgentState) -> dict:
            start_time = time.perf_counter()
            logger.info(f"Executing Node: {node_id} ({node_type})")

            error_msg = None
            try:
                if node_type == "input":
                    result = self._handle_input(state, node_id, node_data)
                elif node_type == "llm":
                    result = await self._handle_llm(state, node_id, node_data)
                elif node_type in ("tool", "skill"):
                    result = await self._handle_skill(state, node_id, node_data)
                elif node_type == "transform":
                    result = self._handle_transform(state, node_id, node_data)
                elif node_type == "output":
                    result = self._handle_output(state, node_id, node_data)
                else:
                    logger.warning(f"Unknown node type: {node_type}")
                    result = {"current_node": node_id}

            except Exception as e:
                logger.exception(f"Error in node {node_id}: {e}")
                error_msg = str(e)
                result = {
                    "current_node": node_id,
                    "results": {node_id: {"error": str(e)}}
                }

            # Record timing
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            # Update node timings in state
            node_timings = state.get("node_timings", {}).copy()
            node_timings[node_id] = duration_ms
            result["node_timings"] = node_timings

            # Record metrics
            self.node_metrics.append({
                "node_id": node_id,
                "node_type": node_type,
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": duration_ms,
                "success": error_msg is None,
                "error": error_msg
            })

            return result

        return node_executor

    def _handle_input(self, state: AgentState, node_id: str, node_data: dict) -> dict:
        """Handle input node - initialize or pass through data."""
        raw_content = state.get("messages", [])[-1].content if state.get("messages") else None

        # Apply Input Guardrails
        safe_content = guardrails.validate_input(str(raw_content)) if raw_content else None

        return {
            "current_node": node_id,
            "results": {node_id: safe_content}
        }

    async def _handle_llm(self, state: AgentState, node_id: str, node_data: dict) -> dict:
        """Handle LLM node - call DeepSeek."""
        # Build prompt from template
        prompt_template = node_data.get("prompt", "{{input}}")

        # Get context from previous results
        context = ""
        for result_id, result_value in state.get("results", {}).items():
            if isinstance(result_value, str):
                context += f"\n{result_value}"
            elif isinstance(result_value, dict) and "content" in result_value:
                context += f"\n{result_value['content']}"

        # Interpolate template
        prompt = prompt_template.replace("{{input}}", context.strip())
        prompt = prompt.replace("{{context}}", context.strip())

        # Build messages
        messages = []
        system_prompt = node_data.get("system_prompt") or self.llm_config.get("system_prompt")
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.extend(state.get("messages", []))
        messages.append(HumanMessage(content=prompt))

        # Call LLM
        response = await self.llm.ainvoke(messages)
        content = response.content

        # Apply Output Guardrails
        if isinstance(content, str):
            content = guardrails.sanitize_output(content)

        return {
            "messages": [AIMessage(content=content)],
            "current_node": node_id,
            "results": {node_id: content},
            "token_usage": state.get("token_usage", 0) + (response.response_metadata.get("token_usage", {}).get("total_tokens", 0) if hasattr(response, "response_metadata") else 0),
            "api_calls": state.get("api_calls", 0) + 1,
        }

    async def _handle_skill(self, state: AgentState, node_id: str, node_data: dict) -> dict:
        """Handle skill/tool node - call external API with caching."""
        skill_config = node_data.get("skill", {})
        tool_config = node_data.get("tool", {})

        endpoint = skill_config.get("api_endpoint") or tool_config.get("url")
        method = skill_config.get("http_method", "GET").upper()
        skill_slug = skill_config.get("slug", node_id)

        if not endpoint:
            return {
                "current_node": node_id,
                "results": {node_id: {"error": "No API endpoint configured"}}
            }

        # Get context from previous results
        context = ""
        for result_value in state.get("results", {}).values():
            if isinstance(result_value, str):
                context = result_value
                break

        # Prepare request args for caching
        request_args = {"query": context} if context else {}

        # Check cache first
        cached_result = await skill_cache.get(skill_slug, request_args)
        if cached_result is not None:
            logger.info(f"Skill cache hit for node {node_id}")
            return {
                "messages": [AIMessage(content=str(cached_result))],
                "current_node": node_id,
                "results": {node_id: cached_result},
                "api_calls": state.get("api_calls", 0),  # No API call made
            }

        # Build request
        headers = skill_config.get("headers_template", {}).copy()

        async with httpx.AsyncClient() as client:
            try:
                if method in ("POST", "PUT", "PATCH"):
                    response = await client.request(
                        method=method,
                        url=endpoint,
                        json=request_args,
                        headers=headers,
                        timeout=30.0
                    )
                else:
                    response = await client.request(
                        method=method,
                        url=endpoint,
                        params={"q": context} if context else {},
                        headers=headers,
                        timeout=30.0
                    )

                result = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text

                # Cache successful results
                if response.is_success:
                    await skill_cache.set(skill_slug, request_args, result)

            except Exception as e:
                result = {"error": str(e)}

        return {
            "messages": [AIMessage(content=str(result))],
            "current_node": node_id,
            "results": {node_id: result},
            "api_calls": state.get("api_calls", 0) + 1,
        }

    def _handle_transform(self, state: AgentState, node_id: str, node_data: dict) -> dict:
        """Handle transform node - data manipulation."""
        from app.core.sandbox import sandbox, SandboxError
        
        transform_type = node_data.get("transform_type", "passthrough")

        # Get last result
        last_result = None
        for result_value in state.get("results", {}).values():
            last_result = result_value

        if transform_type == "extract":
            field_path = node_data.get("field", "")
            output = self._extract_field(last_result, field_path)
        elif transform_type == "template":
            template = node_data.get("template", "{{input}}")
            output = template.replace("{{input}}", str(last_result) if last_result else "")
        elif transform_type == "script":
            # Execute user code in sandbox
            code = node_data.get("code", "result = input_data")
            try:
                exec_result = sandbox.execute(code, context={
                    'input_data': last_result,
                    'data': last_result,
                })
                output = exec_result.get('result') or exec_result.get('output') or last_result
                logger.debug(f"Sandbox execution output: {output}")
            except SandboxError as e:
                logger.warning(f"Sandbox error in node {node_id}: {e}")
                output = f"[Script Error: {e}]"
        else:
            output = last_result

        return {
            "current_node": node_id,
            "results": {node_id: output}
        }

    def _handle_output(self, state: AgentState, node_id: str, node_data: dict) -> dict:
        """Handle output node - final result."""
        # Collect all results
        all_results = state.get("results", {})

        # Get the last meaningful result
        final_output = None
        for result in all_results.values():
            if result is not None:
                final_output = result

        return {
            "current_node": node_id,
            "results": {node_id: final_output, "_final": final_output}
        }

    def _extract_field(self, data: Any, field_path: str) -> Any:
        """Extract field using dot notation."""
        if not field_path or data is None:
            return data

        parts = field_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None

        return current

    def build_graph(self, checkpointer: Any = None) -> StateGraph:
        """Compiles the JSON config into a LangGraph."""
        # Check cache first
        cached = WorkflowGraphCache.get(self.config)
        if cached:
            logger.debug("Using cached workflow graph")
            return cached

        workflow = StateGraph(AgentState)

        # Add all nodes
        for node_id, node in self.nodes.items():
            node_func = self._create_node_function(
                node_id,
                node.get("type", "unknown"),
                node.get("data", {})
            )
            workflow.add_node(node_id, node_func)

        # Add edges
        for edge in self.edges:
            workflow.add_edge(edge["source"], edge["target"])

        # Determine entry point (nodes with no incoming edges)
        targets = {e["target"] for e in self.edges}
        starts = [nid for nid in self.nodes if nid not in targets]

        if starts:
            workflow.set_entry_point(starts[0])
        elif self.nodes:
            # Fallback to first node
            workflow.set_entry_point(list(self.nodes.keys())[0])

        # Set finish point (nodes with no outgoing edges)
        sources = {e["source"] for e in self.edges}
        ends = [nid for nid in self.nodes if nid not in sources]

        for end_node in ends:
            workflow.add_edge(end_node, END)

        compiled = workflow.compile(checkpointer=checkpointer)

        # Cache the compiled graph
        WorkflowGraphCache.set(self.config, compiled)

        return compiled

    async def _get_checkpointer(self, use_persistent: bool = True):
        """Get appropriate checkpointer based on environment.
        
        In production with DATABASE_URL set, uses AsyncPostgresSaver.
        Falls back to MemorySaver for development or if PostgresSaver unavailable.
        """
        if use_persistent and POSTGRES_SAVER_AVAILABLE and hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
            try:
                # Use async postgres checkpointer for production
                checkpointer = AsyncPostgresSaver.from_conn_string(str(settings.DATABASE_URL))
                await checkpointer.setup()  # Create tables if needed
                logger.info("Using PostgresSaver for workflow persistence")
                return checkpointer
            except Exception as e:
                logger.warning(f"Failed to initialize PostgresSaver, falling back to MemorySaver: {e}")
        
        logger.debug("Using MemorySaver for workflow persistence")
        return MemorySaver()

    async def run(self, initial_input: str, thread_id: str = "default-thread", use_persistent_checkpointer: bool = True) -> dict:
        """Execute the workflow with initial input and persistent state.
        
        Args:
            initial_input: The user's input message
            thread_id: Unique identifier for this conversation thread
            use_persistent_checkpointer: If True, uses PostgresSaver when available
        """
        # Reset metrics
        self.node_metrics = []
        start_time = time.perf_counter()

        # Choose checkpointer based on environment
        checkpointer = await self._get_checkpointer(use_persistent_checkpointer)
        app = self.build_graph(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": thread_id}}

        initial_state: AgentState = {
            "messages": [HumanMessage(content=initial_input)],
            "current_node": "",
            "results": {},
            "token_usage": 0,
            "api_calls": 0,
            "node_timings": {},
            "parallel_groups": [list(layer) for layer in self.parallel_layers],
        }

        final_state = await app.ainvoke(initial_state, config=config)

        end_time = time.perf_counter()
        total_duration_ms = (end_time - start_time) * 1000

        return {
            "output": final_state.get("results", {}).get("_final") or (
                final_state["messages"][-1].content if final_state.get("messages") else None
            ),
            "trace": final_state.get("results", {}),
            "token_usage": final_state.get("token_usage", 0),
            "api_calls": final_state.get("api_calls", 0),
            # Performance metrics
            "metrics": {
                "total_duration_ms": total_duration_ms,
                "node_timings": final_state.get("node_timings", {}),
                "node_count": len(self.nodes),
                "parallel_layers": len(self.parallel_layers),
                "node_metrics": self.node_metrics,
            }
        }

    async def run_with_parallel_execution(self, initial_input: str) -> dict:
        """
        Execute workflow with explicit parallel execution of independent nodes.

        This method manually orchestrates parallel execution based on
        computed topological layers, providing more control than default
        LangGraph execution.
        """
        self.node_metrics = []
        start_time = time.perf_counter()

        # Initialize state
        state: AgentState = {
            "messages": [HumanMessage(content=initial_input)],
            "current_node": "",
            "results": {},
            "token_usage": 0,
            "api_calls": 0,
            "node_timings": {},
            "parallel_groups": [list(layer) for layer in self.parallel_layers],
        }

        # Execute each layer in parallel
        for layer_idx, layer in enumerate(self.parallel_layers):
            logger.info(f"Executing layer {layer_idx + 1}/{len(self.parallel_layers)} with {len(layer)} nodes")

            # Create tasks for all nodes in this layer
            tasks = []
            for node_id in layer:
                node = self.nodes[node_id]
                node_func = self._create_node_function(
                    node_id,
                    node.get("type", "unknown"),
                    node.get("data", {})
                )
                tasks.append(node_func(state))

            # Execute all nodes in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Merge results into state
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Node execution failed: {result}")
                        continue

                    if isinstance(result, dict):
                        # Merge results
                        if "results" in result:
                            state["results"].update(result["results"])
                        if "messages" in result:
                            state["messages"].extend(result["messages"])
                        if "token_usage" in result:
                            state["token_usage"] = result["token_usage"]
                        if "api_calls" in result:
                            state["api_calls"] = result["api_calls"]
                        if "node_timings" in result:
                            state["node_timings"].update(result["node_timings"])
                        if "current_node" in result:
                            state["current_node"] = result["current_node"]

        end_time = time.perf_counter()
        total_duration_ms = (end_time - start_time) * 1000

        return {
            "output": state.get("results", {}).get("_final") or (
                state["messages"][-1].content if state.get("messages") else None
            ),
            "trace": state.get("results", {}),
            "token_usage": state.get("token_usage", 0),
            "api_calls": state.get("api_calls", 0),
            "metrics": {
                "total_duration_ms": total_duration_ms,
                "node_timings": state.get("node_timings", {}),
                "node_count": len(self.nodes),
                "parallel_layers": len(self.parallel_layers),
                "execution_mode": "parallel",
                "node_metrics": self.node_metrics,
            }
        }

    def get_optimization_report(self) -> dict:
        """
        Generate optimization report based on node metrics.

        Identifies:
        - Slowest nodes
        - Parallelization opportunities
        - Cache hit rates
        - Recommendations
        """
        if not self.node_metrics:
            return {"error": "No metrics available. Run workflow first."}

        # Compute statistics
        total_time = sum(m["duration_ms"] for m in self.node_metrics)
        slowest_nodes = sorted(self.node_metrics, key=lambda x: x["duration_ms"], reverse=True)[:5]

        # Identify bottlenecks
        bottlenecks = [m for m in self.node_metrics if m["duration_ms"] > total_time * 0.3]

        # Compute potential parallel speedup
        sequential_time = total_time
        parallel_time = sum(
            max(m["duration_ms"] for m in self.node_metrics if m["node_id"] in layer)
            for layer in self.parallel_layers
            if any(m["node_id"] in layer for m in self.node_metrics)
        ) if self.parallel_layers else total_time

        return {
            "total_execution_time_ms": total_time,
            "node_count": len(self.node_metrics),
            "parallel_layers": len(self.parallel_layers),
            "slowest_nodes": [
                {"node_id": m["node_id"], "type": m["node_type"], "duration_ms": m["duration_ms"]}
                for m in slowest_nodes
            ],
            "bottlenecks": [
                {"node_id": m["node_id"], "type": m["node_type"], "duration_ms": m["duration_ms"]}
                for m in bottlenecks
            ],
            "potential_speedup": {
                "sequential_time_ms": sequential_time,
                "parallel_time_ms": parallel_time,
                "speedup_factor": sequential_time / parallel_time if parallel_time > 0 else 1.0
            },
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []

        if not self.node_metrics:
            return ["Run workflow to collect metrics"]

        # Check for slow LLM nodes
        llm_nodes = [m for m in self.node_metrics if m["node_type"] == "llm"]
        if llm_nodes:
            avg_llm_time = sum(m["duration_ms"] for m in llm_nodes) / len(llm_nodes)
            if avg_llm_time > 2000:
                recommendations.append("Consider using a faster LLM model or reducing prompt complexity")

        # Check for slow skill nodes
        skill_nodes = [m for m in self.node_metrics if m["node_type"] in ("tool", "skill")]
        if skill_nodes:
            slow_skills = [m for m in skill_nodes if m["duration_ms"] > 1000]
            if slow_skills:
                recommendations.append(f"Optimize {len(slow_skills)} slow skill nodes with caching or timeouts")

        # Check parallel efficiency
        if len(self.parallel_layers) < len(self.nodes) // 2:
            recommendations.append("Workflow has limited parallelization opportunity - consider restructuring")

        # Check for failed nodes
        failed_nodes = [m for m in self.node_metrics if not m["success"]]
        if failed_nodes:
            recommendations.append(f"Fix {len(failed_nodes)} failed nodes to improve reliability")

        if not recommendations:
            recommendations.append("Workflow performance is optimal")

        return recommendations
