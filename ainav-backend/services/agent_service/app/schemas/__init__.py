"""
Pydantic schemas for Skills, Workflows, and Executions.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


# =============================================================================
# SKILL SCHEMAS
# =============================================================================

class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    api_endpoint: Optional[str] = Field(None, max_length=512)
    http_method: Optional[str] = Field(None, max_length=10)
    input_schema: Optional[dict[str, Any]] = None
    output_schema: Optional[dict[str, Any]] = None
    headers_template: Optional[dict[str, Any]] = None
    auth_type: str = Field(default="none", max_length=50)
    auth_config: Optional[dict[str, Any]] = None
    # Documentation fields
    rate_limit: Optional[dict[str, Any]] = None
    pricing_tier: Optional[str] = Field(None, max_length=50)
    pricing_details: Optional[dict[str, Any]] = None
    code_examples: Optional[dict[str, Any]] = None
    sample_request: Optional[dict[str, Any]] = None
    sample_response: Optional[dict[str, Any]] = None


class SkillCreate(SkillBase):
    tool_id: UUID


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    api_endpoint: Optional[str] = Field(None, max_length=512)
    http_method: Optional[str] = Field(None, max_length=10)
    input_schema: Optional[dict[str, Any]] = None
    output_schema: Optional[dict[str, Any]] = None
    headers_template: Optional[dict[str, Any]] = None
    auth_type: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    # Documentation fields
    rate_limit: Optional[dict[str, Any]] = None
    pricing_tier: Optional[str] = Field(None, max_length=50)
    pricing_details: Optional[dict[str, Any]] = None
    code_examples: Optional[dict[str, Any]] = None
    sample_request: Optional[dict[str, Any]] = None
    sample_response: Optional[dict[str, Any]] = None


class SkillResponse(SkillBase):
    id: UUID
    tool_id: UUID
    is_active: bool
    usage_count: int
    avg_latency_ms: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# WORKFLOW SCHEMAS
# =============================================================================

class ReactFlowNode(BaseModel):
    id: str
    type: str  # 'input', 'llm', 'skill', 'output', 'condition'
    position: dict[str, float]  # {x: number, y: number}
    data: dict[str, Any]


class ReactFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class ReactFlowGraph(BaseModel):
    nodes: list[ReactFlowNode]
    edges: list[ReactFlowEdge]
    viewport: Optional[dict[str, float]] = None  # {x, y, zoom}


class WorkflowBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_zh: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)


class WorkflowCreate(WorkflowBase):
    graph_json: ReactFlowGraph
    trigger_type: str = Field(default="manual", max_length=50)
    trigger_config: Optional[dict[str, Any]] = None
    input_schema: Optional[dict[str, Any]] = None
    llm_model: str = Field(default="deepseek-chat", max_length=100)
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    is_public: bool = False
    is_template: bool = False


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    name_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    graph_json: Optional[ReactFlowGraph] = None
    trigger_type: Optional[str] = Field(None, max_length=50)
    trigger_config: Optional[dict[str, Any]] = None
    input_schema: Optional[dict[str, Any]] = None
    llm_model: Optional[str] = Field(None, max_length=100)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    is_public: Optional[bool] = None
    is_template: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    id: UUID
    user_id: UUID
    graph_json: dict[str, Any]
    trigger_type: str
    trigger_config: Optional[dict[str, Any]]
    input_schema: Optional[dict[str, Any]]
    llm_model: str
    system_prompt: Optional[str]
    temperature: float
    is_public: bool
    is_template: bool
    forked_from_id: Optional[UUID]
    fork_count: int
    run_count: int
    star_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowSummary(BaseModel):
    """Lightweight workflow for listings."""
    id: UUID
    name: str
    name_zh: Optional[str]
    slug: str
    description: Optional[str]
    icon: Optional[str]
    trigger_type: str
    is_public: bool
    fork_count: int
    run_count: int
    star_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# EXECUTION SCHEMAS
# =============================================================================

class NodeExecutionLog(BaseModel):
    node_id: str
    node_type: str
    status: str  # 'pending', 'running', 'success', 'error', 'skipped'
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: datetime


class ExecutionCreate(BaseModel):
    workflow_id: UUID
    input_data: Optional[dict[str, Any]] = None
    trigger_type: str = Field(default="manual", max_length=50)
    trigger_metadata: Optional[dict[str, Any]] = None


class ExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    user_id: UUID
    status: str
    input_data: Optional[dict[str, Any]]
    output_data: Optional[dict[str, Any]]
    error_message: Optional[str]
    execution_log: Optional[list[dict[str, Any]]]
    token_usage: int
    total_api_calls: int
    duration_ms: Optional[int]
    trigger_type: Optional[str]
    trigger_metadata: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecutionSummary(BaseModel):
    """Lightweight execution for listings."""
    id: UUID
    workflow_id: UUID
    status: str
    duration_ms: Optional[int]
    token_usage: int
    trigger_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PAGINATED RESPONSES
# =============================================================================

class PaginatedSkillsResponse(BaseModel):
    items: list[SkillResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedWorkflowsResponse(BaseModel):
    items: list[WorkflowSummary]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedExecutionsResponse(BaseModel):
    items: list[ExecutionSummary]
    total: int
    page: int
    page_size: int
    pages: int
