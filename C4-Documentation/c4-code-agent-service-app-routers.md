# C4 Code Level: Agent Service Routers

## Overview

- **Name**: Agent Service Routers - API Endpoint Handlers for Agentic Platform
- **Description**: FastAPI router modules that provide REST API endpoints for managing AI agent skills, workflows, executions, and analytics in the AI Navigation platform. Handles CRUD operations, workflow execution orchestration, agent chat interactions, and usage analytics.
- **Location**: `/home/dislove/document/ai 导航/ainav-backend/services/agent_service/app/routers`
- **Language**: Python 3.12+
- **Purpose**: Exposes the core agentic platform functionality through REST API endpoints prefixed with `/v1/`. Manages the full lifecycle of agent workflows from creation to execution tracking and analytics reporting.

## Code Elements

### Router Modules

#### **1. skills.py** - Skill CRUD Operations
Route prefix: `/v1/skills`

**Functions:**

- `list_skills(page: int, page_size: int, tool_id: Optional[UUID], is_active: Optional[bool], search: Optional[str], db: AsyncSession) -> PaginatedSkillsResponse`
  - HTTP: `GET /` (response_model=PaginatedSkillsResponse)
  - Purpose: List all skills with pagination, filtering by tool, status, or search term
  - Dependencies: SQLAlchemy async queries with ILIKE text search
  - Location: skills.py:22-76

- `get_skills_by_tool(tool_id: UUID, active_only: bool, db: AsyncSession) -> list[SkillResponse]`
  - HTTP: `GET /by-tool/{tool_id}` (response_model=list[SkillResponse])
  - Purpose: Retrieve all skills for a specific tool, optionally filtering active only
  - Location: skills.py:79-97

- `get_skill(skill_id: UUID, db: AsyncSession) -> SkillResponse`
  - HTTP: `GET /{skill_id}` (response_model=SkillResponse)
  - Purpose: Get a specific skill by ID with full details
  - Location: skills.py:100-114

- `create_skill(skill_data: SkillCreate, db: AsyncSession) -> SkillResponse`
  - HTTP: `POST /` (response_model=SkillResponse, status_code=201)
  - Purpose: Create a new skill for a tool, validates tool existence and slug uniqueness within tool
  - Side Effects: Updates Tool.has_api flag to True when first skill created
  - Location: skills.py:117-151

- `update_skill(skill_id: UUID, skill_data: SkillUpdate, db: AsyncSession) -> SkillResponse`
  - HTTP: `PUT /{skill_id}` (response_model=SkillResponse)
  - Purpose: Update skill details with partial updates support (exclude_unset=True)
  - Location: skills.py:154-177

- `delete_skill(skill_id: UUID, db: AsyncSession) -> None`
  - HTTP: `DELETE /{skill_id}` (status_code=204)
  - Purpose: Delete a skill and update Tool.has_api flag if no skills remain
  - Location: skills.py:180-207

#### **2. workflows.py** - Agent Workflow Management
Route prefix: `/v1/workflows`

**Helper Functions:**

- `generate_slug(name: str) -> str`
  - Purpose: Convert workflow name to URL-friendly slug (lowercase, special chars removed, max 200 chars)
  - Location: workflows.py:23-28

**Endpoint Functions:**

- `list_workflows(page: int, page_size: int, user_id: Optional[UUID], is_public: Optional[bool], is_template: Optional[bool], search: Optional[str], db: AsyncSession) -> PaginatedWorkflowsResponse`
  - HTTP: `GET /` (response_model=PaginatedWorkflowsResponse)
  - Purpose: List workflows with multi-criteria filtering (user, public status, template flag, full-text search). Orders by popularity (run_count + star_count)
  - Note: TODO indicates auth integration needed for user_id filtering
  - Location: workflows.py:31-102

- `list_my_workflows(page: int, page_size: int, db: AsyncSession) -> PaginatedWorkflowsResponse`
  - HTTP: `GET /my` (response_model=PaginatedWorkflowsResponse)
  - Purpose: List current user's workflows (placeholder implementation, awaits auth integration)
  - TODO: Integrate with auth token to get actual user_id
  - Location: workflows.py:105-135

- `list_public_workflows(page: int, page_size: int, search: Optional[str], is_template: Optional[bool], db: AsyncSession) -> PaginatedWorkflowsResponse`
  - HTTP: `GET /public` (response_model=PaginatedWorkflowsResponse)
  - Purpose: List public/community workflows, filterable by template status and search
  - Location: workflows.py:138-187

- `get_workflow(workflow_id: UUID, db: AsyncSession) -> WorkflowResponse`
  - HTTP: `GET /{workflow_id}` (response_model=WorkflowResponse)
  - Purpose: Get full workflow details by ID (includes graph_json and all metadata)
  - TODO: Permission check needed
  - Location: workflows.py:190-208

- `get_workflow_by_slug(slug: str, db: AsyncSession) -> WorkflowResponse`
  - HTTP: `GET /by-slug/{slug}` (response_model=WorkflowResponse)
  - Purpose: Get workflow by human-readable slug instead of UUID
  - Location: workflows.py:211-227

- `create_workflow(workflow_data: WorkflowCreate, db: AsyncSession) -> WorkflowResponse`
  - HTTP: `POST /` (response_model=WorkflowResponse, status_code=201)
  - Purpose: Create new agent workflow, handles slug uniqueness with UUID suffix fallback
  - Converts ReactFlowGraph Pydantic model to dict before storage
  - TODO: Integrate auth to get actual user_id
  - Location: workflows.py:230-265

- `update_workflow(workflow_id: UUID, workflow_data: WorkflowUpdate, db: AsyncSession) -> WorkflowResponse`
  - HTTP: `PUT /{workflow_id}` (response_model=WorkflowResponse)
  - Purpose: Update workflow with automatic version tracking and history recording
  - Special Logic: Increments version, records changes in version_history when graph_json changes
  - TODO: Ownership check needed
  - Location: workflows.py:268-313

- `delete_workflow(workflow_id: UUID, db: AsyncSession) -> None`
  - HTTP: `DELETE /{workflow_id}` (status_code=204)
  - Purpose: Delete a workflow (cascades to related executions)
  - TODO: Ownership check needed
  - Location: workflows.py:316-335

- `fork_workflow(workflow_id: UUID, db: AsyncSession) -> WorkflowResponse`
  - HTTP: `POST /{workflow_id}/fork` (response_model=WorkflowResponse, status_code=201)
  - Purpose: Clone a public workflow to user's collection with "Fork" suffix
  - Validation: Rejects forking private workflows, increments fork_count on original
  - TODO: Get user_id from auth
  - Location: workflows.py:338-394

- `star_workflow(workflow_id: UUID, db: AsyncSession) -> dict`
  - HTTP: `POST /{workflow_id}/star` (status_code=200)
  - Purpose: Upvote/star a workflow to increase visibility (no deduplication yet)
  - TODO: Prevent duplicate starring per user
  - Location: workflows.py:397-417

- `get_workflow_versions(workflow_id: UUID, db: AsyncSession) -> dict`
  - HTTP: `GET /{workflow_id}/versions` (response_model=dict)
  - Purpose: Get version history for a workflow showing all past changes
  - Location: workflows.py:420-440

#### **3. executions.py** - Workflow Execution and Run Management
Route prefix: `/v1/executions`

**Data Classes:**

- `DirectExecutionRequest(BaseModel)`
  - Fields: nodes (list[dict]), edges (list[dict]), input (str="Start workflow"), use_langgraph (bool=False)
  - Purpose: Request body for direct workflow execution without saving to database
  - Location: executions.py:32-37

- `DirectExecutionResponse(BaseModel)`
  - Fields: status (str), output (Any), trace (dict), token_usage (int=0), api_calls (int=0), duration_ms (int=0)
  - Purpose: Response from direct execution endpoint
  - Location: executions.py:40-47

**Endpoint Functions:**

- `list_executions(page: int, page_size: int, workflow_id: Optional[UUID], status: Optional[str], db: AsyncSession) -> PaginatedExecutionsResponse`
  - HTTP: `GET /` (response_model=PaginatedExecutionsResponse)
  - Purpose: List execution history with pagination and filters for workflow and status
  - TODO: Filter by user_id from auth
  - Location: executions.py:50-90

- `get_execution(execution_id: UUID, db: AsyncSession) -> ExecutionResponse`
  - HTTP: `GET /{execution_id}` (response_model=ExecutionResponse)
  - Purpose: Get detailed execution with full logs and metrics
  - Location: executions.py:93-109

- `run_workflow(execution_data: ExecutionCreate, background_tasks: BackgroundTasks, db: AsyncSession) -> ExecutionResponse`
  - HTTP: `POST /run` (response_model=ExecutionResponse, status_code=201)
  - Purpose: Asynchronously execute workflow, returns immediately with execution record
  - Processing: Creates execution record, runs `execute_workflow_background` as background task
  - TODO: Get user_id from auth
  - Location: executions.py:112-163

**Background Task:**

- `execute_workflow_background(execution_id: UUID, workflow_graph: dict, input_data: dict|None, llm_model: str, system_prompt: str|None, temperature: float) -> None`
  - Purpose: Asynchronous background task that executes workflow and updates execution record
  - Process:
    1. Updates status to "running"
    2. Creates WorkflowExecutor with config
    3. On success: Updates status to "completed", stores output, increments workflow.run_count
    4. On failure: Updates status to "failed", stores error_message
  - Location: executions.py:166-243

- `cancel_execution(execution_id: UUID, db: AsyncSession) -> dict`
  - HTTP: `POST /{execution_id}/cancel` (status_code=200)
  - Purpose: Cancel a pending or running execution
  - Validation: Only allows cancellation of pending/running executions
  - Location: executions.py:246-271

- `run_workflow_sync(execution_data: ExecutionCreate, db: AsyncSession) -> ExecutionResponse`
  - HTTP: `POST /run-sync` (response_model=ExecutionResponse)
  - Purpose: Synchronously execute workflow and wait for completion (useful for testing)
  - Processing: Inline execution without background task, captures full result
  - TODO: Get user_id from auth
  - Location: executions.py:274-357

- `run_workflow_direct(request: DirectExecutionRequest) -> DirectExecutionResponse`
  - HTTP: `POST /run-direct` (response_model=DirectExecutionResponse)
  - Purpose: Execute workflow from JSON without saving to database (test/integration use)
  - Engines: Supports both custom WorkflowExecutor (default) and LangGraph engine (if available)
  - Error Handling: Catches exceptions and returns failed status with error trace
  - Location: executions.py:360-426

- `list_engines() -> dict`
  - HTTP: `GET /engines` (response_model=dict)
  - Purpose: List available execution engines with availability status
  - Engines Listed:
    - "default": Custom WorkflowExecutor (always available)
    - "langgraph": LangGraph engine (if import successful)
  - Location: executions.py:429-451

#### **4. chat.py** - Agent Chat Interactions with Agentic Loop
Route prefix: `/v1/agents`

**Endpoint Functions:**

- `chat_with_agent(workflow_id: str, message: Dict[str, str], session_id: Optional[str], db: AsyncSession) -> dict`
  - HTTP: `POST /{workflow_id}/chat`
  - Purpose: Interactive chat with agent using dynamic skill selection and RAG
  - Processing Pipeline:
    1. Look up workflow by ID
    2. Retrieve available active skills
    3. Fetch chat history for session
    4. Search AgentMemory for relevant context (RAG)
    5. Execute agentic loop with AgenticExecutor
    6. Store chat message and create execution record
  - Session Management: Auto-generates session_id if not provided (UUID)
  - Memory Integration: Uses memory_service for RAG retrieval and history
  - Location: chat.py:15-85

- `get_chat_session_history(workflow_id: str, session_id: str) -> dict`
  - HTTP: `GET /{workflow_id}/history/{session_id}`
  - Purpose: Retrieve chat history for a specific session
  - Location: chat.py:87-94

- `clear_session(workflow_id: str, session_id: str) -> dict`
  - HTTP: `DELETE /{workflow_id}/session/{session_id}`
  - Purpose: Clear chat history and memory for a session
  - Location: chat.py:96-103

#### **5. analytics.py** - Usage Statistics and Performance Metrics
Route prefix: `/v1/analytics`

**Endpoint Functions:**

- `get_workflow_analytics(workflow_id: UUID, days: int = Query(30), db: AsyncSession) -> dict`
  - HTTP: `GET /workflow/{workflow_id}`
  - Purpose: Get usage analytics for a specific workflow over time period
  - Metrics Calculated:
    - total_runs, successful_runs, failed_runs
    - success_rate (percentage)
    - total_tokens, avg_duration_ms
    - stars, forks, current_version
  - Date Range: Configurable 1-365 days
  - Location: analytics.py:17-79

- `get_workflow_run_history(workflow_id: UUID, days: int = Query(30), db: AsyncSession) -> dict`
  - HTTP: `GET /workflow/{workflow_id}/runs`
  - Purpose: Get daily breakdown of workflow runs over time
  - Data Points: Date, total runs, successful runs per day
  - Use Case: Visualizing usage trends
  - Location: analytics.py:82-131

- `get_top_workflows(limit: int = Query(10), db: AsyncSession) -> dict`
  - HTTP: `GET /top`
  - Purpose: List top public workflows ranked by popularity score
  - Scoring: run_count + (star_count * 2)
  - Limit: 1-50 workflows
  - Location: analytics.py:134-166

### Router Module (Aggregator)

#### **__init__.py** - Router Aggregation
- **Purpose**: Imports all router modules for easy inclusion in main FastAPI app
- **Imports**: skills, workflows, executions, chat, analytics
- **Location**: __init__.py:1-4

## Dependencies

### Internal Dependencies

**Core Modules:**
- `shared.database.get_async_session`: FastAPI dependency injection for async database sessions
- `shared.database.async_session_factory`: Factory for creating new database sessions in background tasks
- `shared.models`: SQLAlchemy ORM models
  - User
  - Skill
  - Tool
  - AgentWorkflow
  - AgentExecution
  - AgentMemory

**Service Schemas:**
- `services.agent_service.app.schemas`: Pydantic validation models
  - SkillCreate, SkillUpdate, SkillResponse
  - WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowSummary
  - ReactFlowNode, ReactFlowEdge, ReactFlowGraph
  - ExecutionCreate, ExecutionResponse, ExecutionSummary
  - DirectExecutionRequest, DirectExecutionResponse
  - PaginatedSkillsResponse, PaginatedWorkflowsResponse, PaginatedExecutionsResponse

**Core Services:**
- `services.agent_service.app.core.executor.WorkflowExecutor`: Custom workflow execution engine
- `services.agent_service.app.core.agentic_executor.AgenticExecutor`: Agentic loop for chat interactions
- `services.agent_service.app.core.memory_service.memory_service`: RAG memory management service

**Engine (Optional):**
- `services.agent_service.app.engine.langgraph_engine.LangGraphWorkflowEngine`: LangGraph-based executor (optional import)

### External Dependencies

**Web Framework:**
- `fastapi`: APIRouter, Depends, HTTPException, Query, BackgroundTasks
- `fastapi.middleware.cors`: CORSMiddleware

**Database/ORM:**
- `sqlalchemy`: select, func, update (SQL construction)
- `sqlalchemy.ext.asyncio`: AsyncSession (async database context)
- `sqlalchemy.orm`: selectinload (eager loading)

**Data Validation:**
- `pydantic`: BaseModel, Field, ConfigDict

**Standard Library:**
- `typing`: Optional, Any, List, Dict
- `uuid`: UUID, uuid4
- `datetime`: datetime, timezone, timedelta
- `math`: ceil
- `re`: sub (regex for slug generation)

## Relationships

### Architecture Pattern: Layered REST API with Background Tasks

The routers implement a layered architecture with clear separation of concerns:

1. **HTTP Layer**: FastAPI routers handle request/response serialization
2. **Service Layer**: Core executors (WorkflowExecutor, AgenticExecutor) handle business logic
3. **Data Access Layer**: SQLAlchemy ORM with async sessions
4. **Background Processing**: Long-running tasks execute asynchronously via BackgroundTasks

### Router Dependency Graph

**Skills Router** depends on:
- Database (Tool, Skill models)
- Schemas (SkillCreate, SkillUpdate, SkillResponse)

**Workflows Router** depends on:
- Database (AgentWorkflow, User models)
- Schemas (WorkflowCreate, WorkflowUpdate, WorkflowResponse)
- Helper: generate_slug() for URL-friendly names

**Executions Router** depends on:
- Database (AgentExecution, AgentWorkflow, User models)
- Schemas (ExecutionCreate, ExecutionResponse)
- WorkflowExecutor (core business logic)
- LangGraphEngine (optional, conditional import)
- BackgroundTasks (async execution)

**Chat Router** depends on:
- Database (AgentWorkflow, Skill, User models)
- Schemas (ExecutionResponse, ExecutionSummary)
- AgenticExecutor (agentic loop with tool use)
- MemoryService (RAG and chat history)

**Analytics Router** depends on:
- Database (AgentWorkflow, AgentExecution models)
- No external services

## API Endpoints Summary

| Method | Route | Handler | Purpose | Authentication |
|--------|-------|---------|---------|-----------------|
| GET | /v1/skills | list_skills | List all skills | No |
| GET | /v1/skills/{skill_id} | get_skill | Get skill details | No |
| GET | /v1/skills/by-tool/{tool_id} | get_skills_by_tool | Get skills for tool | No |
| POST | /v1/skills | create_skill | Create new skill | TODO: Auth |
| PUT | /v1/skills/{skill_id} | update_skill | Update skill | TODO: Auth |
| DELETE | /v1/skills/{skill_id} | delete_skill | Delete skill | TODO: Auth |
| GET | /v1/workflows | list_workflows | List workflows | No |
| GET | /v1/workflows/public | list_public_workflows | List public workflows | No |
| GET | /v1/workflows/my | list_my_workflows | List user's workflows | TODO: Auth |
| GET | /v1/workflows/{workflow_id} | get_workflow | Get workflow details | No |
| GET | /v1/workflows/by-slug/{slug} | get_workflow_by_slug | Get by slug | No |
| GET | /v1/workflows/{workflow_id}/versions | get_workflow_versions | Get version history | No |
| POST | /v1/workflows | create_workflow | Create workflow | TODO: Auth |
| PUT | /v1/workflows/{workflow_id} | update_workflow | Update workflow | TODO: Auth |
| DELETE | /v1/workflows/{workflow_id} | delete_workflow | Delete workflow | TODO: Auth |
| POST | /v1/workflows/{workflow_id}/fork | fork_workflow | Fork workflow | TODO: Auth |
| POST | /v1/workflows/{workflow_id}/star | star_workflow | Star workflow | TODO: Auth |
| GET | /v1/executions | list_executions | List executions | No |
| GET | /v1/executions/{execution_id} | get_execution | Get execution details | No |
| POST | /v1/executions/run | run_workflow | Run workflow async | No |
| POST | /v1/executions/run-sync | run_workflow_sync | Run workflow sync | No |
| POST | /v1/executions/run-direct | run_workflow_direct | Run without saving | No |
| GET | /v1/executions/engines | list_engines | List engines | No |
| POST | /v1/executions/{execution_id}/cancel | cancel_execution | Cancel execution | No |
| POST | /v1/agents/{workflow_id}/chat | chat_with_agent | Chat with agent | TODO: Auth |
| GET | /v1/agents/{workflow_id}/history/{session_id} | get_chat_session_history | Get history | No |
| DELETE | /v1/agents/{workflow_id}/session/{session_id} | clear_session | Clear history | No |
| GET | /v1/analytics/workflow/{workflow_id} | get_workflow_analytics | Get analytics | No |
| GET | /v1/analytics/workflow/{workflow_id}/runs | get_workflow_run_history | Get run history | No |
| GET | /v1/analytics/top | get_top_workflows | Get top workflows | No |

## Technical Patterns

### 1. Pagination Pattern
All list endpoints follow standard pagination:
- Query parameters: `page` (default=1), `page_size` (default=20, max=100)
- Response includes: `items`, `total`, `page`, `page_size`, `pages`
- Calculation: `pages = ceil(total / page_size)`

### 2. Async Database Access
- Uses SQLAlchemy async driver (asyncpg)
- All endpoints accept `db: AsyncSession = Depends(get_async_session)`
- Background tasks use `async_session_factory()` for new sessions

### 3. Filtering Strategy
- ILIKE search for text fields (case-insensitive pattern matching)
- Multiple filter conditions combined with OR/AND logic
- Separate count query for pagination accuracy

### 4. Version Tracking (Workflows Only)
- Increments `version` number on graph_json updates
- Records changes in `version_history` array with timestamp
- Enables workflow versioning and rollback capability

### 5. Popularity Ranking
- Workflows ordered by: `(run_count + star_count)` descending
- Public workflows: `(star_count * 2 + run_count)` for higher star weight
- Enables community-driven discovery

### 6. Background Task Execution
- Uses FastAPI's `BackgroundTasks` for async workflow runs
- Creates execution record immediately, processes asynchronously
- Provides immediate response with execution_id for polling

## Notes

### Authentication TODOs
Multiple endpoints require authentication integration:
- Skill/Workflow/Chat operations need `get_current_user_id` dependency
- User filtering in workflow listings needs auth context
- Fork, star, and "my workflows" endpoints are user-specific

### Engine Support
- Default WorkflowExecutor is always available
- LangGraph engine is optional (graceful fallback if import fails)
- Direct execution endpoint supports both engines for flexibility

### Memory and RAG (Phase 3 Integration)
- Chat endpoint uses memory_service for:
  - Chat history retrieval and storage
  - RAG context search using vector embeddings
  - Session management across multiple turns
- AgentMemory table uses pgvector for 384-dimensional embeddings

### Performance Considerations
- Pagination essential for large result sets
- Separate count queries enable accurate pagination
- Eager loading (selectinload) available but not currently used
- Background execution prevents blocking on long-running workflows
- Version history grows with each update (no archival implemented)

### Error Handling
- HTTPException for not found (404) and validation errors (400)
- Execution background task catches and logs exceptions
- Direct execution returns failed status with error trace rather than raising

### Design Patterns Observed
1. **Dependency Injection**: FastAPI's Depends() for database sessions
2. **Async/Await**: Throughout for non-blocking I/O
3. **Repository Pattern**: Model-agnostic CRUD operations
4. **Service Layer**: Executor and Memory service abstractions
5. **Task Queue**: Background task for long-running operations
6. **Event Logging**: Execution logs capture node-by-node progress
