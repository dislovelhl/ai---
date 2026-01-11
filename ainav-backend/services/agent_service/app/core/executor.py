"""
Workflow Executor - Core engine for executing agent workflows.

Executes React Flow graph definitions by traversing nodes in topological order,
executing LLM calls, skill invocations, and data transformations.
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone
from uuid import UUID
import httpx
import json
import logging
import gzip
import base64

from shared.config import settings

logger = logging.getLogger(__name__)


@dataclass
class NodeResult:
    """Result of executing a single node."""
    node_id: str
    node_type: str
    status: str  # 'success', 'error', 'skipped'
    input_data: Any = None
    output_data: Any = None
    error_message: Optional[str] = None
    duration_ms: int = 0
    token_usage: Optional[dict] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    checkpoint: Optional[str] = None  # Compressed state snapshot for replay

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "token_usage": self.token_usage,
            "timestamp": self.timestamp.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "checkpoint": self.checkpoint,
        }

    def to_execution_step(self) -> dict:
        """Convert to execution_steps format for database storage."""
        return {
            "node_id": self.node_id,
            "status": "completed" if self.status == "success" else self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "token_usage": self.token_usage or {"input": 0, "output": 0, "total": 0},
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "checkpoint": self.checkpoint,
        }


@dataclass
class ExecutionResult:
    """Complete execution result."""
    output: Any
    logs: list[dict]
    execution_steps: list[dict] = field(default_factory=list)
    token_usage: int = 0
    api_calls: int = 0
    success: bool = True
    error_message: Optional[str] = None


class WorkflowExecutor:
    """
    Executes Agent Workflows from React Flow graph definitions.

    Supports node types:
    - input: Starting point, receives initial data
    - output: Ending point, returns final data
    - llm: Calls DeepSeek API with configured prompt
    - skill: Calls external API (tool skill)
    - transform: JavaScript-like data transformation
    - condition: Branching based on conditions
    """

    def __init__(self, graph_json: dict, llm_config: dict = None, execution_id: Optional[UUID] = None):
        self.nodes = {n["id"]: n for n in graph_json.get("nodes", [])}
        self.edges = graph_json.get("edges", [])
        self.llm_config = llm_config or {}
        self.execution_id = execution_id

        # Build adjacency for traversal
        self.outgoing: dict[str, list[str]] = {}
        self.incoming: dict[str, list[str]] = {}

        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]

            if src not in self.outgoing:
                self.outgoing[src] = []
            self.outgoing[src].append(tgt)

            if tgt not in self.incoming:
                self.incoming[tgt] = []
            self.incoming[tgt].append(src)

        # Execution state
        self.results: dict[str, NodeResult] = {}
        self.token_usage = 0
        self.api_calls = 0
        self.execution_steps: list[dict] = []
        self.initial_input = None  # Store for checkpoint replay

    def _create_checkpoint(self) -> str:
        """
        Create a compressed state snapshot for replay capability.

        Captures the current workflow state including:
        - All node results executed so far
        - Current execution context (token usage, API calls)
        - Graph structure for validation

        Returns:
            Base64-encoded gzip-compressed JSON string
        """
        try:
            # Build state snapshot
            state_snapshot = {
                "graph": {
                    "nodes": list(self.nodes.keys()),
                    "edges": self.edges,
                },
                "results": {
                    node_id: {
                        "node_id": result.node_id,
                        "node_type": result.node_type,
                        "status": result.status,
                        "input_data": result.input_data,
                        "output_data": result.output_data,
                        "error_message": result.error_message,
                        "token_usage": result.token_usage,
                    }
                    for node_id, result in self.results.items()
                },
                "context": {
                    "token_usage": self.token_usage,
                    "api_calls": self.api_calls,
                    "initial_input": self.initial_input,
                },
                "metadata": {
                    "checkpoint_at": datetime.now(timezone.utc).isoformat(),
                    "nodes_executed": len(self.results),
                }
            }

            # Serialize to JSON
            json_data = json.dumps(state_snapshot, ensure_ascii=False)

            # Compress using gzip
            compressed = gzip.compress(json_data.encode('utf-8'))

            # Encode to base64 for safe storage in JSON
            checkpoint = base64.b64encode(compressed).decode('ascii')

            return checkpoint

        except Exception as e:
            logger.warning(f"Failed to create checkpoint: {e}")
            return None

    @staticmethod
    def _decompress_checkpoint(checkpoint: str) -> dict:
        """
        Decompress a checkpoint to restore workflow state.

        Args:
            checkpoint: Base64-encoded gzip-compressed JSON string

        Returns:
            Deserialized state snapshot dictionary
        """
        try:
            # Decode from base64
            compressed = base64.b64decode(checkpoint.encode('ascii'))

            # Decompress
            json_data = gzip.decompress(compressed).decode('utf-8')

            # Parse JSON
            state_snapshot = json.loads(json_data)

            return state_snapshot

        except Exception as e:
            logger.error(f"Failed to decompress checkpoint: {e}")
            raise ValueError(f"Invalid checkpoint data: {e}")

    async def execute(self, initial_input: Any) -> ExecutionResult:
        """
        Execute the workflow in topological order.
        """
        try:
            # Store initial input for checkpoint replay
            self.initial_input = initial_input

            # Find input nodes (no incoming edges)
            start_nodes = [
                nid for nid, node in self.nodes.items()
                if nid not in self.incoming or len(self.incoming[nid]) == 0
            ]

            if not start_nodes:
                # Fallback: find nodes labeled as 'input' type
                start_nodes = [
                    nid for nid, node in self.nodes.items()
                    if node.get("type") == "input"
                ]

            if not start_nodes:
                return ExecutionResult(
                    output=None,
                    logs=[],
                    success=False,
                    error_message="No starting nodes found in workflow"
                )
            
            # Execute starting nodes with initial input
            for node_id in start_nodes:
                await self._execute_node(node_id, initial_input)
            
            # Execute remaining nodes in order
            executed = set(start_nodes)
            to_execute = self._get_ready_nodes(executed)
            
            while to_execute:
                for node_id in to_execute:
                    # Gather inputs from predecessor nodes
                    input_data = self._gather_inputs(node_id)
                    await self._execute_node(node_id, input_data)
                    executed.add(node_id)
                
                to_execute = self._get_ready_nodes(executed)
            
            # Find output nodes and gather final result
            output_nodes = [
                nid for nid, node in self.nodes.items()
                if node.get("type") == "output"
            ]
            
            if output_nodes:
                final_output = self.results[output_nodes[0]].output_data
            else:
                # Use last executed node's output
                last_executed = list(executed)[-1] if executed else None
                final_output = self.results.get(last_executed, NodeResult("", "", "")).output_data
            
            return ExecutionResult(
                output=final_output,
                logs=[r.to_dict() for r in self.results.values()],
                execution_steps=self.execution_steps,
                token_usage=self.token_usage,
                api_calls=self.api_calls,
                success=True,
            )

        except Exception as e:
            logger.exception(f"Workflow execution failed: {e}")
            return ExecutionResult(
                output=None,
                logs=[r.to_dict() for r in self.results.values()],
                execution_steps=self.execution_steps,
                token_usage=self.token_usage,
                api_calls=self.api_calls,
                success=False,
                error_message=str(e),
            )
    
    def _get_ready_nodes(self, executed: set[str]) -> list[str]:
        """Get nodes whose all predecessors have been executed."""
        ready = []
        for node_id in self.nodes:
            if node_id in executed:
                continue
            
            predecessors = self.incoming.get(node_id, [])
            if all(p in executed for p in predecessors):
                ready.append(node_id)
        
        return ready
    
    def _gather_inputs(self, node_id: str) -> Any:
        """Gather outputs from predecessor nodes as input."""
        predecessors = self.incoming.get(node_id, [])
        
        if len(predecessors) == 0:
            return None
        elif len(predecessors) == 1:
            return self.results[predecessors[0]].output_data
        else:
            # Multiple inputs: merge into dict
            return {
                pred: self.results[pred].output_data
                for pred in predecessors
                if pred in self.results
            }
    
    async def _execute_node(self, node_id: str, input_data: Any) -> NodeResult:
        """Execute a single node based on its type."""
        import time

        node = self.nodes[node_id]
        node_type = node.get("type", "unknown")
        start_time = time.time()
        started_at = datetime.now(timezone.utc)

        # Emit event: Node execution started
        if self.execution_id:
            await self._emit_step_event(
                node_id=node_id,
                status="running",
                input_data=input_data,
                started_at=started_at,
            )

        try:
            if node_type == "input":
                result = self._handle_input_node(node, input_data)
            elif node_type == "output":
                result = self._handle_output_node(node, input_data)
            elif node_type == "llm":
                result = await self._handle_llm_node(node, input_data)
            elif node_type == "skill":
                result = await self._handle_skill_node(node, input_data)
            elif node_type == "transform":
                result = self._handle_transform_node(node, input_data)
            elif node_type == "condition":
                result = self._handle_condition_node(node, input_data)
            else:
                result = NodeResult(
                    node_id=node_id,
                    node_type=node_type,
                    status="error",
                    error_message=f"Unknown node type: {node_type}"
                )

            result.duration_ms = int((time.time() - start_time) * 1000)
            result.started_at = started_at
            result.completed_at = datetime.now(timezone.utc)

            # Emit event: Node execution completed successfully
            if self.execution_id:
                await self._emit_step_event(
                    node_id=node_id,
                    status="completed",
                    input_data=input_data,
                    output_data=result.output_data,
                    token_usage=result.token_usage,
                    started_at=started_at,
                    completed_at=result.completed_at,
                )

        except Exception as e:
            logger.exception(f"Error executing node {node_id}: {e}")
            completed_at = datetime.now(timezone.utc)
            result = NodeResult(
                node_id=node_id,
                node_type=node_type,
                status="error",
                input_data=input_data,
                error_message=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                started_at=started_at,
                completed_at=completed_at,
            )

            # Emit event: Node execution failed
            if self.execution_id:
                await self._emit_step_event(
                    node_id=node_id,
                    status="failed",
                    input_data=input_data,
                    error_message=str(e),
                    started_at=started_at,
                    completed_at=completed_at,
                )

        # Store result
        self.results[node_id] = result

        # Create checkpoint after successful execution for replay capability
        # Only create checkpoint on success to save storage space
        if result.status == "success":
            checkpoint = self._create_checkpoint()
            result.checkpoint = checkpoint

        self.execution_steps.append(result.to_execution_step())
        return result

    async def _emit_step_event(
        self,
        node_id: str,
        status: str,
        input_data: Any = None,
        output_data: Any = None,
        error_message: str = None,
        token_usage: dict = None,
        started_at: datetime = None,
        completed_at: datetime = None,
    ):
        """Emit WebSocket event for step update."""
        if not self.execution_id:
            return

        try:
            from ..websocket import manager

            await manager.send_step_update(
                execution_id=str(self.execution_id),
                node_id=node_id,
                status=status,
                input_data=input_data,
                output_data=output_data,
                error_message=error_message,
                token_usage=token_usage,
                started_at=started_at.isoformat() if started_at else None,
                completed_at=completed_at.isoformat() if completed_at else None,
            )
        except Exception as e:
            logger.warning(f"Failed to emit WebSocket event: {e}")
    
    def _handle_input_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle input node - pass through initial data."""
        node_data = node.get("data", {})
        
        # If node has default value and no input provided, use default
        if input_data is None and "default" in node_data:
            input_data = node_data["default"]
        
        return NodeResult(
            node_id=node["id"],
            node_type="input",
            status="success",
            input_data=input_data,
            output_data=input_data,
        )
    
    def _handle_output_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle output node - format and return final result."""
        node_data = node.get("data", {})
        
        # Apply output format if specified
        output_format = node_data.get("format")
        if output_format == "json":
            output = json.dumps(input_data) if not isinstance(input_data, str) else input_data
        elif output_format == "text":
            output = str(input_data)
        else:
            output = input_data
        
        return NodeResult(
            node_id=node["id"],
            node_type="output",
            status="success",
            input_data=input_data,
            output_data=output,
        )
    
    async def _handle_llm_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle LLM node - call DeepSeek API."""
        node_data = node.get("data", {})
        
        # Build prompt
        prompt_template = node_data.get("prompt", "{{input}}")
        prompt = self._interpolate_template(prompt_template, input_data)
        
        # Get system prompt
        system_prompt = node_data.get("system_prompt") or self.llm_config.get("system_prompt") or "You are a helpful assistant."
        
        # Make API call
        model = node_data.get("model") or self.llm_config.get("model", "deepseek-chat")
        temperature = node_data.get("temperature") or self.llm_config.get("temperature", 0.7)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
        }
        
        # Check for JSON output mode
        if node_data.get("json_output"):
            payload["response_format"] = {"type": "json_object"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.DEEPSEEK_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Extract content
        content = result["choices"][0]["message"]["content"]
        
        # Track usage
        if "usage" in result:
            self.token_usage += result["usage"].get("total_tokens", 0)
        self.api_calls += 1
        
        # Parse JSON if expected
        if node_data.get("json_output"):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                pass
        
        return NodeResult(
            node_id=node["id"],
            node_type="llm",
            status="success",
            input_data={"prompt": prompt},
            output_data=content,
        )
    
    async def _handle_skill_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle skill node - call external API."""
        node_data = node.get("data", {})
        skill_config = node_data.get("skill", {})
        
        # Build request
        method = skill_config.get("http_method", "GET").upper()
        endpoint = skill_config.get("api_endpoint")
        
        if not endpoint:
            return NodeResult(
                node_id=node["id"],
                node_type="skill",
                status="error",
                error_message="No API endpoint configured"
            )
        
        # Map input to API parameters
        input_schema = skill_config.get("input_schema", {})
        request_body = self._map_input_to_schema(input_data, input_schema)
        
        # Build headers
        headers = skill_config.get("headers_template", {}).copy()
        
        # Handle authentication
        auth_type = skill_config.get("auth_type", "none")
        auth_config = skill_config.get("auth_config", {})
        
        if auth_type == "bearer" and "env_var" in auth_config:
            import os
            token = os.getenv(auth_config["env_var"])
            if token:
                header_name = auth_config.get("header", "Authorization")
                prefix = auth_config.get("prefix", "Bearer")
                headers[header_name] = f"{prefix} {token}"
        elif auth_type == "api_key" and "env_var" in auth_config:
            import os
            api_key = os.getenv(auth_config["env_var"])
            if api_key:
                header_name = auth_config.get("header", "X-API-Key")
                headers[header_name] = api_key
        
        # Make request
        async with httpx.AsyncClient() as client:
            if method in ["POST", "PUT", "PATCH"]:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=request_body,
                    headers=headers,
                    timeout=30.0
                )
            else:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    params=request_body if isinstance(request_body, dict) else None,
                    headers=headers,
                    timeout=30.0
                )
        
        self.api_calls += 1
        
        # Parse response
        try:
            output = response.json()
        except json.JSONDecodeError:
            output = response.text
        
        if response.is_success:
            return NodeResult(
                node_id=node["id"],
                node_type="skill",
                status="success",
                input_data=request_body,
                output_data=output,
            )
        else:
            return NodeResult(
                node_id=node["id"],
                node_type="skill",
                status="error",
                input_data=request_body,
                output_data=output,
                error_message=f"API returned status {response.status_code}"
            )
    
    def _handle_transform_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle transform node - apply data transformation."""
        node_data = node.get("data", {})
        transform_type = node_data.get("transform_type", "passthrough")
        
        try:
            if transform_type == "passthrough":
                output = input_data
            elif transform_type == "extract":
                # Extract a specific field
                field_path = node_data.get("field", "")
                output = self._extract_field(input_data, field_path)
            elif transform_type == "template":
                # Apply string template
                template = node_data.get("template", "{{input}}")
                output = self._interpolate_template(template, input_data)
            elif transform_type == "json_parse":
                output = json.loads(input_data) if isinstance(input_data, str) else input_data
            elif transform_type == "json_stringify":
                output = json.dumps(input_data)
            elif transform_type == "array_join":
                separator = node_data.get("separator", ", ")
                output = separator.join(str(x) for x in input_data) if isinstance(input_data, list) else str(input_data)
            else:
                output = input_data
            
            return NodeResult(
                node_id=node["id"],
                node_type="transform",
                status="success",
                input_data=input_data,
                output_data=output,
            )
        except Exception as e:
            return NodeResult(
                node_id=node["id"],
                node_type="transform",
                status="error",
                input_data=input_data,
                error_message=str(e)
            )
    
    def _handle_condition_node(self, node: dict, input_data: Any) -> NodeResult:
        """Handle condition node - evaluate condition for branching."""
        node_data = node.get("data", {})
        condition_type = node_data.get("condition_type", "equals")
        field = node_data.get("field", "")
        value = node_data.get("value")
        
        # Extract field value
        actual_value = self._extract_field(input_data, field) if field else input_data
        
        # Evaluate condition
        if condition_type == "equals":
            result = actual_value == value
        elif condition_type == "not_equals":
            result = actual_value != value
        elif condition_type == "contains":
            result = value in str(actual_value)
        elif condition_type == "greater_than":
            result = float(actual_value) > float(value)
        elif condition_type == "less_than":
            result = float(actual_value) < float(value)
        elif condition_type == "is_empty":
            result = not actual_value
        elif condition_type == "is_not_empty":
            result = bool(actual_value)
        else:
            result = True
        
        return NodeResult(
            node_id=node["id"],
            node_type="condition",
            status="success",
            input_data=input_data,
            output_data={"result": result, "value": actual_value},
        )
    
    def _interpolate_template(self, template: str, data: Any) -> str:
        """Interpolate {{variable}} placeholders in template."""
        if not isinstance(template, str):
            return str(template)
        
        result = template
        
        # Simple {{input}} replacement
        if isinstance(data, str):
            result = result.replace("{{input}}", data)
        elif isinstance(data, dict):
            result = result.replace("{{input}}", json.dumps(data))
            # Replace {{field.path}} patterns
            for key, value in self._flatten_dict(data).items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
        else:
            result = result.replace("{{input}}", str(data))
        
        return result
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten nested dict for template interpolation."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _extract_field(self, data: Any, field_path: str) -> Any:
        """Extract a field from nested data using dot notation."""
        if not field_path:
            return data
        
        parts = field_path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    idx = int(part)
                    current = current[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        
        return current
    
    def _map_input_to_schema(self, input_data: Any, schema: dict) -> dict:
        """Map input data to API request schema."""
        if not schema or not isinstance(schema, dict):
            return input_data if isinstance(input_data, dict) else {"input": input_data}
        
        properties = schema.get("properties", {})
        result = {}
        
        for prop_name, prop_config in properties.items():
            # Check for mapping configuration
            mapping = prop_config.get("x-mapping")
            if mapping:
                result[prop_name] = self._extract_field(input_data, mapping)
            elif isinstance(input_data, dict) and prop_name in input_data:
                result[prop_name] = input_data[prop_name]
        
        return result
