# C4 Code Level: Agent Service Core Application

## Overview

- **Name**: Agent Service Core Application
- **Description**: FastAPI application serving as the core entry point for LangGraph-based agent workflow orchestration, providing APIs for skill management, workflow creation/execution, agent chat interactions, and analytics
- **Location**: `/home/dislove/document/ai 导航/ainav-backend/services/agent_service/app/`
- **Language**: Python (3.11+)
- **Purpose**: Central orchestration service for managing AI agent workflows with visual workflow builder support, autonomous agent execution, skill/tool management, and execution analytics

## Module Structure

The agent service application is organized into the following modules:

### Root Module: `main.py`
- **Purpose**: FastAPI application initialization and router inclusion
- **Location**: `main.py:1-49`
- **Key Responsibilities**:
  - Initialize FastAPI application instance
  - Configure CORS middleware for frontend access
  - Include all service routers with appropriate API versioning and documentation

### Router Modules
The service exposes 5 main router modules that handle different aspects of agent management:

1. **Skills Router** (`routers/skills.py`)
   - Purpose: CRUD operations for AI tool skills (API capabilities)
   - Endpoints: `/v1/skills` prefix
   - Operations: List, create, read, update, delete skills with pagination and filtering

2. **Workflows Router** (`routers/workflows.py`)
   - Purpose: CRUD operations for agent workflows
   - Endpoints: `/v1/workflows` prefix
   - Operations: List, create, read, update, delete workflows; manage templates and sharing

3. **Executions Router** (`routers/executions.py`)
   - Purpose: Run workflows and track execution history
   - Endpoints: `/v1/executions` prefix
   - Operations: Execute workflows, retrieve execution history, stream execution logs

4. **Chat Router** (`routers/chat.py`)
   - Purpose: Agent chat interactions with dynamic skill selection
   - Endpoints: `/v1/agents` prefix
   - Operations: Chat with agent workflows using autonomous function calling

5. **Analytics Router** (`routers/analytics.py`)
   - Purpose: Usage statistics and performance analytics for workflows
   - Endpoints: `/v1/analytics` prefix
   - Operations: Get workflow usage stats, execution analytics, performance metrics

### Core Execution Modules
The application relies on two main execution engines:

1. **Workflow Executor** (`core/executor.py`)
   - Purpose: Core engine for executing agent workflows from React Flow graph definitions
   - Key Class: `WorkflowExecutor`
   - Capabilities: Node execution, result aggregation, logging, error handling

2. **LangGraph Engine** (`engine/langgraph_engine.py`)
   - Purpose: Industry-standard LangGraph state machine implementation for workflow compilation
   - Key Class: `LangGraphWorkflowEngine`
   - Capabilities: React Flow to LangGraph compilation, message-based state management

3. **Agentic Executor** (`core/agentic_executor.py`)
   - Purpose: Autonomous agent execution with function calling
   - Key Class: `AgenticExecutor`
   - Capabilities: Dynamic skill selection, tool invocation, state management

4. **Memory Service** (`core/memory_service.py`)
   - Purpose: Short-term (Redis) and long-term (pgvector) memory management
   - Key Class: `MemoryService`
   - Capabilities: Chat history storage, vector embeddings, semantic search

## Code Elements

### FastAPI Application Configuration

#### `FastAPI` Instance Creation
- **Location**: `main.py:12-18`
- **Configuration**:
  ```python
  app = FastAPI(
      title="AI Navigator - Agent Service",
      description="Agent workflow builder and execution service",
      version="1.0.0",
      docs_url="/docs",
      redoc_url="/redoc",
  )
  ```
- **Purpose**: Initialize FastAPI application with metadata for OpenAPI documentation
- **Dependencies**: `fastapi.FastAPI`

#### CORS Middleware Configuration
- **Location**: `main.py:20-27`
- **Configuration**:
  - Allowed origins: `http://localhost:3000` (development frontend)
  - Credentials: Enabled
  - Methods: All HTTP methods allowed
  - Headers: All custom headers allowed
- **Purpose**: Enable cross-origin requests from frontend application
- **Dependencies**: `fastapi.middleware.cors.CORSMiddleware`

### Router Inclusions

| Router | Prefix | Tags | Location |
|--------|--------|------|----------|
| Skills Router | `/v1/skills` | `["Skills"]` | `routers/skills.py:19` |
| Workflows Router | `/v1/workflows` | `["Workflows"]` | `routers/workflows.py:20` |
| Executions Router | `/v1/executions` | `["Executions"]` | `routers/executions.py:28` |
| Chat Router | `/v1/agents` | `["Agent Chat"]` | `routers/chat.py:13` |
| Analytics Router | `/v1/analytics` | `["Analytics"]` | `routers/analytics.py:14` |

- **Location**: `main.py:29-34`
- **Pattern**: Each router is included with versioned prefix `/v1/` and appropriate tags for OpenAPI grouping
- **Dependencies**: All routers from `routers` module

### Health Check & Root Endpoints

#### Root Endpoint
- **Path**: `GET /`
- **Location**: `main.py:37-43`
- **Purpose**: Service health indicator and version information
- **Response**:
  ```python
  {
      "service": "agent-service",
      "version": "1.0.0",
      "description": "Agent workflow builder and execution service",
  }
  ```

#### Health Check Endpoint
- **Path**: `GET /health`
- **Location**: `main.py:46-48`
- **Purpose**: Container/load-balancer health probe
- **Response**:
  ```python
  {"status": "healthy", "service": "agent-service"}
  ```

## Schemas & Data Models

### Request/Response Schemas (from `schemas/__init__.py`)

#### Skill Schemas
- `SkillBase`: Base skill attributes (name, slug, description, API endpoint, auth config)
- `SkillCreate`: Extends SkillBase, includes tool_id
- `SkillUpdate`: Optional skill attributes for partial updates
- `SkillResponse`: Complete skill data with metadata (ID, usage_count, avg_latency_ms, timestamps)
- `PaginatedSkillsResponse`: Paginated list of skills

#### Workflow Schemas
- `ReactFlowNode`: Single node in React Flow graph (id, type, position, data)
- `ReactFlowEdge`: Edge connecting nodes (id, source, target, handles)
- `ReactFlowGraph`: Complete React Flow graph definition (nodes, edges)
- `WorkflowCreate`: Workflow creation request
- `WorkflowUpdate`: Workflow update request
- `WorkflowResponse`: Complete workflow data with metadata
- `WorkflowSummary`: Lightweight workflow summary
- `PaginatedWorkflowsResponse`: Paginated list of workflows

#### Execution Schemas
- `ExecutionCreate`: Execution request with input parameters
- `ExecutionResponse`: Execution result with output, logs, metrics
- `ExecutionSummary`: Lightweight execution summary
- `PaginatedExecutionsResponse`: Paginated list of executions
- `DirectExecutionRequest`: Request for direct workflow execution without saving
- `DirectExecutionResponse`: Response from direct execution

### Data Classes (from `core/executor.py`)

#### `NodeResult`
- **Location**: `core/executor.py:19-41`
- **Purpose**: Encapsulates result of executing a single workflow node
- **Attributes**:
  - `node_id: str` - Unique node identifier
  - `node_type: str` - Node type (input, llm, skill, output, condition)
  - `status: str` - Execution status (success, error, skipped)
  - `input_data: Any` - Data passed to node
  - `output_data: Any` - Data produced by node
  - `error_message: Optional[str]` - Error details if failed
  - `duration_ms: int` - Node execution time
  - `timestamp: datetime` - When execution occurred

#### `ExecutionResult`
- **Location**: `core/executor.py:44-52`
- **Purpose**: Complete execution result aggregation
- **Attributes**:
  - `output: Any` - Final workflow output
  - `logs: list[dict]` - Execution trace logs
  - `token_usage: int` - LLM tokens consumed
  - `api_calls: int` - External API calls made
  - `success: bool` - Overall success status
  - `error_message: Optional[str]` - Error details

#### `AgentState` (from `engine/langgraph_engine.py`)
- **Location**: `engine/langgraph_engine.py:26-33`
- **Purpose**: LangGraph state dictionary for message-based workflow
- **Attributes**:
  - `messages: Annotated[list[BaseMessage], operator.add]` - Message history
  - `current_node: str` - Currently executing node ID
  - `results: dict[str, Any]` - Node execution results cache
  - `token_usage: int` - Cumulative token usage
  - `api_calls: int` - Cumulative API call count

#### `AgentState` (from `core/agentic_executor.py`)
- **Location**: `core/agentic_executor.py:25-33`
- **Purpose**: Agentic loop state with autonomous tool selection
- **Attributes**:
  - `messages: Annotated[List[BaseMessage], operator.add]` - Conversation history
  - `workflow_id: str` - Associated workflow ID
  - `session_id: str` - Chat session ID
  - `available_tools: List[Dict[str, Any]]` - Available skills in OpenAI format
  - `execution_result: Optional[Dict[str, Any]]` - Result of tool execution
  - `token_usage: int` - LLM tokens consumed
  - `api_calls: int` - Tool API calls made

## Execution Engines

### WorkflowExecutor Class
- **Location**: `core/executor.py:55-`
- **Purpose**: Execute React Flow graph definitions in topological order
- **Key Methods**:
  - `execute(nodes, edges, input_data) -> ExecutionResult` - Execute workflow
  - Execute node types: input, llm, skill, output, condition, transform
  - Handle execution traces and error propagation

### LangGraphWorkflowEngine Class
- **Location**: `engine/langgraph_engine.py:39-`
- **Purpose**: Compile React Flow graphs into LangGraph state machines
- **Constructor Parameters**:
  - `workflow_config: dict` - React Flow graph configuration
  - `llm_config: dict = None` - LLM settings (model, temperature)
- **LLM Configuration**:
  - Provider: DeepSeek (OpenAI-compatible API)
  - API Key: `settings.DEEPSEEK_API_KEY`
  - Base URL: `settings.DEEPSEEK_API_URL`
  - Default Model: `deepseek-chat`
  - Default Temperature: 0.7

### AgenticExecutor Class
- **Location**: `core/agentic_executor.py:35-`
- **Purpose**: Autonomous agent execution with function calling
- **Constructor Parameters**:
  - `workflow_id: str` - Associated workflow UUID
  - `session_id: str` - Chat session identifier
  - `llm_config: dict = None` - LLM configuration
- **Key Methods**:
  - `_get_openai_tools(skills) -> List[Dict]` - Convert Skills to OpenAI tool format
  - Function calling support via DeepSeek LLM
- **LLM**: ChatOpenAI with DeepSeek backend

### MemoryService Class
- **Location**: `core/memory_service.py:14-`
- **Purpose**: Dual-layer memory management (Redis + pgvector)
- **Constructor Parameters**: None (uses `settings.REDIS_URL`)
- **Key Methods**:
  - `add_chat_message(workflow_id, session_id, role, content)` - Store message in Redis
  - `get_chat_history(workflow_id, session_id, limit) -> List[Dict]` - Retrieve Redis messages
  - `clear_chat_history(workflow_id, session_id)` - Delete Redis chat
  - `store_long_term_memory(...)` - Persist embeddings to pgvector
  - `search_long_term_memory(...)` - Semantic search via pgvector
- **Components**:
  - Redis: Short-term chat history with 7-day TTL
  - SentenceTransformer: Multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`)
  - PostgreSQL pgvector: Long-term memory storage

## Dependencies

### Internal Dependencies

#### Modules
- `routers.skills` - Skill CRUD operations
- `routers.workflows` - Workflow CRUD operations
- `routers.executions` - Workflow execution management
- `routers.chat` - Agent chat interactions
- `routers.analytics` - Workflow analytics

#### Core Modules
- `core.executor.WorkflowExecutor` - React Flow graph execution
- `core.agentic_executor.AgenticExecutor` - Autonomous agent execution
- `core.memory_service.MemoryService` - Dual-layer memory management

#### Engine Modules
- `engine.langgraph_engine.LangGraphWorkflowEngine` - LangGraph compilation

#### Shared (Monorepo)
- `shared.database.get_async_session` - Async database session dependency
- `shared.models` - SQLAlchemy ORM models:
  - `Skill` - Tool capability definition
  - `Tool` - AI tool metadata
  - `AgentWorkflow` - User-created workflow blueprint
  - `AgentExecution` - Execution history record
  - `User` - User account data
  - `AgentMemory` - Vector embeddings for RAG
- `shared.config.settings` - Application configuration (DeepSeek API keys, REDIS_URL)

### External Dependencies

#### Core Framework
- `fastapi>=0.104.0` - Web framework
- `fastapi.middleware.cors.CORSMiddleware` - CORS support
- `uvicorn` - ASGI server (runtime, not imported in code)

#### Database & Caching
- `sqlalchemy>=2.0` - ORM and async support
- `sqlalchemy.ext.asyncio.AsyncSession` - Async database session
- `redis.asyncio` - Async Redis client
- `asyncpg` - PostgreSQL async driver (via DATABASE_URL)

#### LLM & Agent Orchestration
- `langchain_core` - LLM integration library
  - `langchain_core.messages.*` - Message types (HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage)
- `langchain_openai.ChatOpenAI` - OpenAI-compatible LLM interface
- `langgraph>=0.1` - Graph-based workflow orchestration
  - `langgraph.graph.StateGraph` - State machine definition
  - `langgraph.graph.END` - Graph termination sentinel
  - `langgraph.prebuilt.ToolNode` - Autonomous tool invocation node

#### ML & Embeddings
- `sentence_transformers` - Multilingual embeddings
  - Model: `paraphrase-multilingual-MiniLM-L12-v2`

#### Utilities
- `pydantic>=2.0` - Data validation and serialization
- `httpx` - HTTP client for external API calls
- `python-dateutil` - Date and timezone handling
- `typing` - Type hints (Annotated, Optional, etc.)

### Configuration Sources

- **DeepSeek API**: `settings.DEEPSEEK_API_KEY`, `settings.DEEPSEEK_API_URL`
- **Database**: `settings.DATABASE_URL` (PostgreSQL with pgvector)
- **Redis**: `settings.REDIS_URL`
- **Frontend URL**: `settings.FRONTEND_URL` (CORS origin in production)

## API Specification

### OpenAPI Documentation
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

### API Endpoints Structure

All API routes follow REST conventions under `/v1/` prefix:

```
/                          # Root service info
/health                    # Health check
/docs                      # Swagger UI
/redoc                     # ReDoc documentation
/openapi.json             # OpenAPI schema

/v1/skills                # Skill CRUD
/v1/workflows             # Workflow CRUD
/v1/executions            # Execution management
/v1/agents                # Agent chat interactions
/v1/analytics             # Workflow analytics
```

## Code Relationships & Call Graph

### Application Initialization Flow

```
main.py:12-18
    |
    v
FastAPI Instance Created
    |
    v
main.py:20-27
    |
    v
CORS Middleware Applied
    |
    v
main.py:29-34
    |
    v
5 Routers Included with Prefixes:
    ├─> skills.router -> /v1/skills
    ├─> workflows.router -> /v1/workflows
    ├─> executions.router -> /v1/executions
    ├─> chat.router -> /v1/agents
    └─> analytics.router -> /v1/analytics
    |
    v
Health Endpoints Registered:
    ├─> GET / (root)
    └─> GET /health
```

### Request Processing Flow (Skill Creation Example)

```
POST /v1/skills (SkillCreate)
    |
    v
skills.router.create_skill()
    |
    v
Depends: get_async_session -> AsyncSession
    |
    v
Create Skill Model
    |
    v
Session.add() + commit()
    |
    v
Return SkillResponse (UUID, timestamps, usage metrics)
```

### Workflow Execution Flow

```
POST /v1/executions
    |
    v
executions.router.create_execution()
    |
    v
[Lookup AgentWorkflow + get_async_session]
    |
    v
BackgroundTasks.add_task(execute_workflow)
    |
    v
execute_workflow() runs either:
    ├─> WorkflowExecutor.execute() [standard execution]
    └─> LangGraphWorkflowEngine.compile().invoke() [LangGraph mode]
    |
    v
[Write AgentExecution record]
    |
    v
NodeResult aggregation -> ExecutionResult
```

### Agent Chat Flow

```
POST /v1/agents/{workflow_id}/chat
    |
    v
chat.router.chat_with_agent()
    |
    v
[Lookup AgentWorkflow + get_async_session]
    |
    v
[Fetch active Skills from database]
    |
    v
AgenticExecutor.__init__(workflow_id, session_id)
    |
    v
MemoryService:
    ├─> get_chat_history() [retrieve from Redis]
    └─> add_chat_message() [store user message]
    |
    v
AgenticExecutor._get_openai_tools(skills) -> Function definitions
    |
    v
ChatOpenAI.invoke() with function_choice="auto"
    |
    v
[Autonomous loop: if function_calls -> execute tools -> loop]
    |
    v
MemoryService.store_long_term_memory() [vector embeddings via pgvector]
    |
    v
Return ExecutionResponse with trace
```

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Web Framework** | FastAPI | >=0.104.0 | REST API + async request handling |
| **ASGI Server** | Uvicorn | Latest | HTTP server (runtime) |
| **Database ORM** | SQLAlchemy | >=2.0 | Async database operations |
| **Database** | PostgreSQL + pgvector | 16+ | Primary data store + embeddings |
| **Cache** | Redis | 7+ | Chat history + session data |
| **LLM Framework** | LangChain Core | Latest | LLM interface abstraction |
| **LLM Backend** | DeepSeek Chat | OpenAI API compatible | Agentic LLM |
| **Workflow Engine** | LangGraph | >=0.1 | Stateful workflow orchestration |
| **Embeddings** | SentenceTransformers | Latest | Multilingual semantic search |
| **Data Validation** | Pydantic | >=2.0 | Request/response validation |
| **HTTP Client** | httpx | Latest | External API calls |

## Security Considerations

### CORS Configuration
- **Current**: Only `http://localhost:3000` allowed (development)
- **Production**: Must be updated to actual frontend domain via `settings.FRONTEND_URL`
- **Credentials**: Enabled for session-based operations

### Database Access
- All database operations use `Depends(get_async_session)`
- Async sessions ensure connection pooling and resource cleanup
- Row-level security should be enforced at the SQLAlchemy model level

### External API Calls
- DeepSeek API key stored in `settings.DEEPSEEK_API_KEY`
- API calls made via `httpx` from `WorkflowExecutor` and `AgenticExecutor`
- Tool/skill API calls may require authentication (auth_config in Skill model)

## Notes

- The application uses **API versioning** via `/v1/` prefix for future compatibility
- **Dual execution engines**: Standard React Flow traversal + LangGraph state machines
- **Autonomous agent support**: Function calling enabled via DeepSeek's OpenAI-compatible API
- **Dual-layer memory**: Redis (temporary) + PostgreSQL pgvector (persistent semantic search)
- **Multilingual support**: Schemas and embeddings support both English and Chinese
- **CORS development mode**: Frontend CORS origin hardcoded for localhost; requires environment variable in production
- **Health endpoints**: Both `GET /` and `GET /health` available for container orchestration
- **OpenAPI docs**: Auto-generated via FastAPI at `/docs` and `/redoc`
- **Async throughout**: All endpoints, database operations, and external calls are async-first
- **Background tasks**: Execution can be run in background via `BackgroundTasks` for long-running workflows
