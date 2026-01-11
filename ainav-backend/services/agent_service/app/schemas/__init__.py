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


class SkillTestRequest(BaseModel):
    """Request to test a skill with sample data."""
    test_data: Optional[dict[str, Any]] = None


class SkillTestResponse(BaseModel):
    """Response from testing a skill."""
    success: bool
    status_code: int
    response_data: Optional[Any] = None
    execution_time_ms: int
    error_message: Optional[str] = None


class ToolInfo(BaseModel):
    """Basic tool information for documentation."""
    id: UUID
    name: str
    name_zh: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class SkillDocumentationResponse(SkillBase):
    """Comprehensive skill documentation with tool information."""
    id: UUID
    tool_id: UUID
    is_active: bool
    usage_count: int
    avg_latency_ms: float
    created_at: datetime
    updated_at: datetime
    tool: Optional[ToolInfo] = None

    class Config:
        from_attributes = True


class SkillCodeExamplesResponse(BaseModel):
    """Code examples for a skill in multiple languages."""
    python: str
    javascript: str




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
    # Template-specific metadata
    category: Optional[str] = Field(None, max_length=100)
    use_case: Optional[str] = Field(None, max_length=255)
    usage_instructions_zh: Optional[str] = None
    tags: Optional[list[str]] = None


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
    # Template-specific metadata
    category: Optional[str] = Field(None, max_length=100)
    use_case: Optional[str] = Field(None, max_length=255)
    usage_instructions_zh: Optional[str] = None
    tags: Optional[list[str]] = None


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
    # Template-specific metadata
    category: Optional[str]
    use_case: Optional[str]
    usage_instructions_zh: Optional[str]
    tags: Optional[list[str]]
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
    is_template: bool
    fork_count: int
    run_count: int
    star_count: int
    # Template-specific metadata
    category: Optional[str]
    use_case: Optional[str]
    tags: Optional[list[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowRevert(BaseModel):
    """Request to revert a workflow to a previous version."""
    target_version: int = Field(..., ge=1, description="Version number to revert to")


class VersionSnapshot(BaseModel):
    """Version snapshot with metadata."""
    version: int
    timestamp: str
    notes: str
    graph_json: dict[str, Any]
    user_id: str


class NodeDiff(BaseModel):
    """Node difference information."""
    node_id: str
    change_type: str  # 'added', 'removed', 'modified'
    old_data: Optional[dict[str, Any]] = None
    new_data: Optional[dict[str, Any]] = None


class EdgeDiff(BaseModel):
    """Edge difference information."""
    edge_id: str
    change_type: str  # 'added', 'removed', 'modified'
    old_data: Optional[dict[str, Any]] = None
    new_data: Optional[dict[str, Any]] = None


class VersionComparison(BaseModel):
    """Comparison between two workflow versions."""
    workflow_id: str
    version1: VersionSnapshot
    version2: VersionSnapshot
    nodes_added: list[NodeDiff]
    nodes_removed: list[NodeDiff]
    nodes_modified: list[NodeDiff]
    edges_added: list[EdgeDiff]
    edges_removed: list[EdgeDiff]
    edges_modified: list[EdgeDiff]


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


# =============================================================================
# TEMPLATE CATEGORY SCHEMAS
# =============================================================================

class TemplateCategoryCount(BaseModel):
    """Category with template count for discovery."""
    category: str
    count: int

    class Config:
        from_attributes = True


# =============================================================================
# WORKFLOW CATEGORY SCHEMAS
# =============================================================================

class WorkflowCategoryBase(BaseModel):
    """Base schema for workflow categories."""
    name: str = Field(..., max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    order: int = 0


class WorkflowCategoryCreate(WorkflowCategoryBase):
    """Schema for creating a workflow category."""
    pass


class WorkflowCategoryUpdate(BaseModel):
    """Schema for updating a workflow category."""
    name: Optional[str] = Field(None, max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    order: Optional[int] = None


class WorkflowCategoryResponse(WorkflowCategoryBase):
    """Response schema for workflow categories."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedWorkflowCategoriesResponse(BaseModel):
    """Paginated response for workflow categories."""
    items: list[WorkflowCategoryResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# WORKFLOW TAG SCHEMAS
# =============================================================================

class WorkflowTagBase(BaseModel):
    """Base schema for workflow tags."""
    name: str = Field(..., max_length=50)
    name_zh: Optional[str] = Field(None, max_length=50)
    slug: str = Field(..., max_length=50)


class WorkflowTagCreate(WorkflowTagBase):
    """Schema for creating a workflow tag."""
    pass


class WorkflowTagUpdate(BaseModel):
    """Schema for updating a workflow tag."""
    name: Optional[str] = Field(None, max_length=50)
    name_zh: Optional[str] = Field(None, max_length=50)
    slug: Optional[str] = Field(None, max_length=50)


class WorkflowTagResponse(WorkflowTagBase):
    """Response schema for workflow tags."""
    id: UUID
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedWorkflowTagsResponse(BaseModel):
    """Paginated response for workflow tags."""
    items: list[WorkflowTagResponse]
    total: int
    page: int
    page_size: int
    pages: int

