# C4 Code Level: Frontend Core Library

## Overview

- **Name**: Frontend Core Library (ainav-web/src/lib)
- **Description**: Shared TypeScript utilities, type definitions, and API client for the AI Navigation Platform frontend. Provides centralized API communication layer, type-safe interfaces for all backend services, and utility functions for common frontend operations.
- **Location**: `/home/dislove/document/ai 导航/ainav-web/src/lib/`
- **Language**: TypeScript 5+
- **Purpose**: Central hub for API communication, type definitions, and utility functions that all frontend components and pages depend on. Acts as the contract between frontend and four backend microservices (Content, Search, User, Agent).

## Code Elements

### Type Definitions Module (`types.ts`)

#### Content Management Types

**`Category`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:3-13`
- **Purpose**: Represents a tool category in the platform
- **Properties**:
  - `id: string` - Unique identifier (UUID)
  - `name: string` - Display name
  - `slug: string` - URL-friendly identifier
  - `description?: string` - Optional category description
  - `icon?: string` - Optional icon URL or SVG
  - `order: number` - Sort order in UI
  - `created_at: string` - ISO 8601 timestamp
  - `updated_at: string` - ISO 8601 timestamp
  - `tool_count?: number` - Optional count of tools in category
- **Usage**: Used by content service API for category listing and filtering
- **Dependencies**: None (base type)

**`Scenario`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:15-22`
- **Purpose**: Represents a usage scenario or use case for tools
- **Properties**:
  - `id: string` - Unique identifier
  - `name: string` - Scenario name
  - `slug: string` - URL-friendly identifier
  - `icon?: string` - Optional icon
  - `created_at: string` - ISO 8601 timestamp
  - `updated_at: string` - ISO 8601 timestamp
- **Usage**: Associated with tools to show relevant use cases
- **Dependencies**: None (base type)

#### Skill Types (Tool Capabilities)

**`Skill`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:28-48`
- **Purpose**: Represents an API capability or endpoint of a tool (OpenAPI-style skill definition)
- **Properties**:
  - `id: string` - Unique identifier
  - `tool_id: string` - Reference to parent tool
  - `name: string` - English skill name
  - `name_zh?: string` - Chinese skill name
  - `slug: string` - URL-friendly identifier
  - `description?: string` - English description
  - `description_zh?: string` - Chinese description
  - `api_endpoint?: string` - API URL or path
  - `http_method?: string` - HTTP method (GET, POST, etc.)
  - `input_schema?: Record<string, unknown>` - JSON Schema for inputs
  - `output_schema?: Record<string, unknown>` - JSON Schema for outputs
  - `headers_template?: Record<string, string>` - Template headers for requests
  - `auth_type: "api_key" | "oauth2" | "bearer" | "none"` - Authentication method
  - `auth_config?: Record<string, unknown>` - Auth configuration
  - `is_active: boolean` - Whether skill is currently available
  - `usage_count: number` - Number of times used
  - `avg_latency_ms: number` - Average response time
  - `created_at: string` - ISO 8601 timestamp
  - `updated_at: string` - ISO 8601 timestamp
- **Usage**: Used by agent service to understand tool capabilities for workflow building
- **Dependencies**: None (base type)

#### Tool Types

**`Tool`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:54-75`
- **Purpose**: Represents an AI tool in the platform directory
- **Properties**:
  - `id: string` - Unique identifier
  - `name: string` - English tool name
  - `name_zh?: string` - Chinese tool name
  - `slug: string` - URL-friendly identifier
  - `description?: string` - English description
  - `description_zh?: string` - Chinese description
  - `url: string` - Tool homepage URL
  - `logo_url?: string` - Logo image URL
  - `pricing_type?: "free" | "freemium" | "paid" | "beta_free" | "open_source"` - Pricing model
  - `is_china_accessible: boolean` - Whether accessible from mainland China
  - `requires_vpn: boolean` - Whether VPN required in China
  - `avg_rating: number` - Average user rating (0-5)
  - `review_count: number` - Number of reviews
  - `github_stars?: number` - GitHub stars if applicable
  - `has_api?: boolean` - Whether tool has API
  - `category?: Category` - Reference to parent category
  - `scenarios: Scenario[]` - Array of scenarios this tool supports
  - `skills?: Skill[]` - Array of available skills/capabilities
  - `created_at: string` - ISO 8601 timestamp
  - `updated_at: string` - ISO 8601 timestamp
- **Usage**: Core domain model for tool directory pages and search results
- **Dependencies**: `Category`, `Scenario`, `Skill`

**`ToolCreate`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:77-88`
- **Purpose**: Input DTO for creating new tools
- **Properties**:
  - `name: string` - Tool name (required)
  - `slug: string` - URL-friendly identifier (required)
  - `description?: string` - Tool description
  - `url: string` - Tool URL (required)
  - `logo_url?: string` - Logo URL
  - `pricing_type?: string` - Pricing model
  - `is_china_accessible?: boolean` - China accessibility flag
  - `requires_vpn?: boolean` - VPN requirement
  - `category_id?: string` - Parent category ID
  - `scenario_ids?: string[]` - Associated scenario IDs
- **Usage**: Used by createTool() API function
- **Dependencies**: None (base type)

#### Agent Workflow Types

**`ReactFlowNode`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:94-99`
- **Purpose**: Represents a single node in a workflow graph (for @xyflow/react visualization)
- **Properties**:
  - `id: string` - Unique node identifier
  - `type: "input" | "output" | "llm" | "skill" | "transform" | "condition"` - Node type
  - `position: { x: number; y: number }` - Canvas position
  - `data: Record<string, unknown>` - Node configuration data
- **Usage**: Building block for visual workflow graphs
- **Dependencies**: None (base type)

**`ReactFlowEdge`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:101-107`
- **Purpose**: Represents a connection between two workflow nodes
- **Properties**:
  - `id: string` - Unique edge identifier
  - `source: string` - Source node ID
  - `target: string` - Target node ID
  - `sourceHandle?: string` - Output port identifier
  - `targetHandle?: string` - Input port identifier
- **Usage**: Defines data flow in workflow graphs
- **Dependencies**: None (base type)

**`ReactFlowGraph`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:109-113`
- **Purpose**: Complete workflow graph structure (for React Flow canvas state)
- **Properties**:
  - `nodes: ReactFlowNode[]` - Array of all nodes in graph
  - `edges: ReactFlowEdge[]` - Array of all edges in graph
  - `viewport?: { x: number; y: number; zoom: number }` - Canvas viewport state
- **Usage**: Serialized representation of workflow visual state
- **Dependencies**: `ReactFlowNode`, `ReactFlowEdge`

**`AgentWorkflow`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:115-139`
- **Purpose**: Complete agent workflow definition with execution config
- **Properties**:
  - `id: string` - Unique workflow identifier
  - `user_id: string` - Owner user ID
  - `name: string` - English workflow name
  - `name_zh?: string` - Chinese workflow name
  - `slug: string` - URL-friendly identifier
  - `description?: string` - English description
  - `description_zh?: string` - Chinese description
  - `icon?: string` - Icon URL or emoji
  - `graph_json: ReactFlowGraph` - Visual workflow graph
  - `trigger_type: "manual" | "schedule" | "webhook"` - Execution trigger type
  - `trigger_config?: Record<string, unknown>` - Trigger-specific configuration
  - `input_schema?: Record<string, unknown>` - JSON Schema for workflow inputs
  - `llm_model: string` - LLM model to use (e.g., "deepseek-chat")
  - `system_prompt?: string` - System prompt for LLM
  - `temperature: number` - LLM temperature (0-2)
  - `is_public: boolean` - Whether publicly discoverable
  - `is_template: boolean` - Whether can be used as template
  - `forked_from_id?: string` - ID of original if forked
  - `fork_count: number` - Number of times forked
  - `run_count: number` - Total executions
  - `star_count: number` - Number of stars/favorites
  - `created_at: string` - ISO 8601 timestamp
  - `updated_at: string` - ISO 8601 timestamp
- **Usage**: Full workflow data returned from agent service
- **Dependencies**: `ReactFlowGraph`

**`AgentWorkflowCreate`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:141-154`
- **Purpose**: Input DTO for creating new workflows
- **Properties**: Same as `AgentWorkflow` but all optional except required fields
- **Usage**: Used by createWorkflow() API function
- **Dependencies**: `ReactFlowGraph`

**`AgentWorkflowSummary`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:156-169`
- **Purpose**: Lightweight workflow representation for listings
- **Properties**:
  - `id: string` - Workflow ID
  - `name: string` - English name
  - `name_zh?: string` - Chinese name
  - `slug: string` - URL-friendly identifier
  - `description?: string` - Description
  - `icon?: string` - Icon
  - `trigger_type: string` - Trigger type
  - `is_public: boolean` - Public flag
  - `fork_count: number` - Fork count
  - `run_count: number` - Execution count
  - `star_count: number` - Star count
  - `created_at: string` - Creation timestamp
- **Usage**: In paginated workflow lists and discovery pages
- **Dependencies**: None (base type)

#### Agent Execution Types

**`NodeExecutionLog`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:175-184`
- **Purpose**: Step-by-step execution trace for a single workflow node
- **Properties**:
  - `node_id: string` - Which node executed
  - `node_type: string` - Type of node
  - `status: "pending" | "running" | "success" | "error" | "skipped"` - Execution status
  - `input_data?: unknown` - Input passed to node
  - `output_data?: unknown` - Output from node
  - `error_message?: string` - Error details if failed
  - `duration_ms?: number` - Execution time
  - `timestamp: string` - When executed
- **Usage**: Building execution detail pages with traces
- **Dependencies**: None (base type)

**`AgentExecution`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:186-202`
- **Purpose**: Complete workflow execution record
- **Properties**:
  - `id: string` - Execution ID
  - `workflow_id: string` - Which workflow executed
  - `user_id: string` - Who triggered execution
  - `status: "pending" | "running" | "completed" | "failed" | "cancelled"` - Overall status
  - `input_data?: Record<string, unknown>` - Execution inputs
  - `output_data?: unknown` - Final output
  - `error_message?: string` - Error if failed
  - `execution_log?: NodeExecutionLog[]` - Step-by-step trace
  - `token_usage: number` - LLM tokens consumed
  - `total_api_calls: number` - Number of external API calls
  - `duration_ms?: number` - Total execution time
  - `trigger_type?: string` - How execution was triggered
  - `trigger_metadata?: Record<string, unknown>` - Trigger details
  - `created_at: string` - Start timestamp
  - `updated_at: string` - Last update timestamp
- **Usage**: Execution history and monitoring pages
- **Dependencies**: `NodeExecutionLog`

**`AgentExecutionSummary`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:204-212`
- **Purpose**: Lightweight execution info for listings
- **Properties**: Summary of key execution fields
- **Usage**: In execution history lists
- **Dependencies**: None (base type)

#### Common Response Types

**`PaginatedResponse<T>`** (Generic Interface)
- **Path**: `ainav-web/src/lib/types.ts:218-224`
- **Purpose**: Generic pagination wrapper for list responses
- **Type Parameters**: `T` - Item type
- **Properties**:
  - `items: T[]` - Page of items
  - `total: number` - Total item count
  - `page: number` - Current page (1-indexed)
  - `page_size: number` - Items per page
  - `pages: number` - Total page count
- **Usage**: API responses for all paginated endpoints
- **Dependencies**: Generic type parameter

**`SearchResult`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:226-230`
- **Purpose**: Search API response structure
- **Properties**:
  - `tools: Tool[]` - Search result tools
  - `total: number` - Total matches
  - `query: string` - Original search query
- **Usage**: Search results page display
- **Dependencies**: `Tool`

#### Chat Types

**`ChatMessage`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:236-243`
- **Purpose**: Single message in a chat session
- **Properties**:
  - `id: string` - Message ID
  - `session_id: string` - Chat session ID
  - `role: "user" | "assistant" | "system"` - Message sender role
  - `content: string` - Message text
  - `metadata?: Record<string, unknown>` - Additional data (tool calls, etc.)
  - `created_at: string` - Timestamp
- **Usage**: Chat interface and session history
- **Dependencies**: None (base type)

**`ChatResponse`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:245-250`
- **Purpose**: Response from agent chat endpoint
- **Properties**:
  - `session_id: string` - Chat session ID
  - `message: ChatMessage` - Agent's response message
  - `workflow_id: string` - Associated workflow
  - `tokens_used?: number` - Tokens consumed
- **Usage**: Chat interaction responses
- **Dependencies**: `ChatMessage`

#### Workflow API Types

**`WorkflowListResponse`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:256-262`
- **Purpose**: Paginated workflow list response
- **Properties**: Extends pagination with workflow summaries
- **Usage**: getWorkflows() and getPublicWorkflows() responses
- **Dependencies**: `PaginatedResponse`, `AgentWorkflowSummary`

**`WorkflowCreate`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:264-280`
- **Purpose**: Input DTO for creating workflows with full schema
- **Properties**: Detailed workflow creation fields
- **Usage**: createWorkflow() API function
- **Dependencies**: `ReactFlowGraph`

**`WorkflowUpdate`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:282-297`
- **Purpose**: Input DTO for updating workflows (all fields optional)
- **Properties**: Same fields as WorkflowCreate but all optional
- **Usage**: updateWorkflow() API function
- **Dependencies**: `ReactFlowGraph`

**`ExecutionCreate`** (Interface)
- **Path**: `ainav-web/src/lib/types.ts:299-303`
- **Purpose**: Input DTO for triggering workflow execution
- **Properties**:
  - `input_data?: Record<string, unknown>` - Execution inputs
  - `trigger_type?: string` - Trigger method
  - `trigger_metadata?: Record<string, unknown>` - Trigger details
- **Usage**: runWorkflow() API function
- **Dependencies**: None (base type)

### API Client Module (`api.ts`)

#### API Configuration

**Constants**:
- `CONTENT_API` - Base URL for content service (default: `http://localhost:8001/v1`)
- `SEARCH_API` - Base URL for search service (default: `http://localhost:8002/v1`)
- `USER_API` - Base URL for user service (default: `http://localhost:8003/v1`)
- `AGENT_API` - Base URL for agent service (default: `http://localhost:8005/v1`)

**Location**: `ainav-web/src/lib/api.ts:20-27`

**Environment Variables**:
- `NEXT_PUBLIC_API_URL` - Content API endpoint
- `NEXT_PUBLIC_SEARCH_API` - Search API endpoint
- `NEXT_PUBLIC_USER_API` - User API endpoint
- `NEXT_PUBLIC_AGENT_API` - Agent API endpoint

#### Authentication Helpers

**`getAuthToken(): string | null`**
- **Path**: `ainav-web/src/lib/api.ts:36-39`
- **Purpose**: Retrieve stored JWT access token from localStorage
- **Parameters**: None
- **Returns**: JWT token string or null if not authenticated
- **Side Effects**: Checks if running on client side (typeof window)
- **Dependencies**: None (browser API)

**`buildAuthHeaders(): HeadersInit`**
- **Path**: `ainav-web/src/lib/api.ts:44-52`
- **Purpose**: Build HTTP headers with Bearer token authentication
- **Parameters**: None
- **Returns**: Headers object with Authorization header (if token present)
- **Dependencies**: `getAuthToken()`

#### Fetch Wrappers

**`fetchAPI<T>(baseUrl: string, endpoint: string, options?: RequestInit): Promise<T>`**
- **Path**: `ainav-web/src/lib/api.ts:61-82`
- **Purpose**: Generic fetch wrapper with error handling and JSON parsing
- **Type Parameters**: `T` - Response type
- **Parameters**:
  - `baseUrl: string` - Base URL (e.g., CONTENT_API)
  - `endpoint: string` - Relative endpoint path
  - `options?: RequestInit` - Fetch options (method, body, headers, etc.)
- **Returns**: Parsed response as type T
- **Error Handling**: Throws Error with detail message from response or status code
- **Side Effects**: Constructs full URL, sets Content-Type header
- **Dependencies**: Native fetch API

**`fetchAuthAPI<T>(baseUrl: string, endpoint: string, options?: RequestInit): Promise<T>`**
- **Path**: `ainav-web/src/lib/api.ts:87-99`
- **Purpose**: Fetch wrapper that automatically includes authentication
- **Type Parameters**: `T` - Response type
- **Parameters**: Same as fetchAPI
- **Returns**: Parsed response as type T
- **Side Effects**: Merges auth headers with request headers
- **Dependencies**: `fetchAPI()`, `buildAuthHeaders()`

#### Categories API

**`getCategories(): Promise<Category[]>`**
- **Path**: `ainav-web/src/lib/api.ts:105-107`
- **Purpose**: Fetch all tool categories
- **Returns**: Array of Category objects
- **HTTP**: GET /categories
- **Dependencies**: `fetchAPI()`, `Category` type

**`getCategoryBySlug(slug: string): Promise<Category>`**
- **Path**: `ainav-web/src/lib/api.ts:109-111`
- **Purpose**: Fetch single category by URL slug
- **Parameters**: `slug: string` - Category slug
- **Returns**: Category object
- **HTTP**: GET /categories/{slug}
- **Dependencies**: `fetchAPI()`, `Category` type

#### Scenarios API

**`getScenarios(): Promise<Scenario[]>`**
- **Path**: `ainav-web/src/lib/api.ts:117-119`
- **Purpose**: Fetch all usage scenarios
- **Returns**: Array of Scenario objects
- **HTTP**: GET /scenarios
- **Dependencies**: `fetchAPI()`, `Scenario` type

**`getScenarioBySlug(slug: string): Promise<Scenario>`**
- **Path**: `ainav-web/src/lib/api.ts:121-123`
- **Purpose**: Fetch single scenario by slug
- **Parameters**: `slug: string` - Scenario slug
- **Returns**: Scenario object
- **HTTP**: GET /scenarios/{slug}
- **Dependencies**: `fetchAPI()`, `Scenario` type

**`getToolsByScenario(slug: string): Promise<Tool[]>`**
- **Path**: `ainav-web/src/lib/api.ts:125-127`
- **Purpose**: Fetch tools associated with a scenario
- **Parameters**: `slug: string` - Scenario slug
- **Returns**: Array of Tool objects
- **HTTP**: GET /scenarios/{slug}/tools
- **Dependencies**: `fetchAPI()`, `Tool` type

#### Tools API

**`getTools(params?: { skip?: number; limit?: number; category_slug?: string; scenario_slug?: string }): Promise<Tool[]>`**
- **Path**: `ainav-web/src/lib/api.ts:133-149`
- **Purpose**: Fetch tools with optional filtering and pagination
- **Parameters**:
  - `params.skip?: number` - Offset for pagination
  - `params.limit?: number` - Number of results
  - `params.category_slug?: string` - Filter by category
  - `params.scenario_slug?: string` - Filter by scenario
- **Returns**: Array of Tool objects
- **HTTP**: GET /tools?[filters]
- **Dependencies**: `fetchAPI()`, `Tool` type

**`getToolBySlug(slug: string): Promise<Tool>`**
- **Path**: `ainav-web/src/lib/api.ts:151-153`
- **Purpose**: Fetch single tool by slug
- **Parameters**: `slug: string` - Tool slug
- **Returns**: Tool object with full details
- **HTTP**: GET /tools/{slug}
- **Dependencies**: `fetchAPI()`, `Tool` type

**`createTool(tool: ToolCreate): Promise<Tool>`**
- **Path**: `ainav-web/src/lib/api.ts:155-160`
- **Purpose**: Create new tool in directory
- **Parameters**: `tool: ToolCreate` - Tool creation data
- **Returns**: Created Tool object with ID
- **HTTP**: POST /tools with JSON body
- **Authentication**: Not explicitly authenticated (public endpoint)
- **Dependencies**: `fetchAPI()`, `Tool`, `ToolCreate` types

#### Search API

**`searchTools(query: string, category?: string, scenario?: string): Promise<Tool[]>`**
- **Path**: `ainav-web/src/lib/api.ts:166-176`
- **Purpose**: Full-text search tools using Meilisearch
- **Parameters**:
  - `query: string` - Search query text
  - `category?: string` - Optional category filter
  - `scenario?: string` - Optional scenario filter
- **Returns**: Array of Tool objects matching search
- **HTTP**: GET /search?q={query}&category={cat}&scenario={scenario}
- **Dependencies**: `fetchAPI()`, `Tool` type

#### User API

**`login(email: string, password: string): Promise<any>`**
- **Path**: `ainav-web/src/lib/api.ts:182-198`
- **Purpose**: User login with email/password credentials
- **Parameters**:
  - `email: string` - User email
  - `password: string` - Password
- **Returns**: Response object (typically includes access_token)
- **HTTP**: POST /auth/login with FormData
- **Notes**: Uses OAuth2 password flow (expects 'username' field)
- **Error Handling**: Throws with Chinese error message "登录失败"
- **Side Effects**: None (token storage handled by caller)
- **Dependencies**: Native fetch API

**`register(userData: any): Promise<any>`**
- **Path**: `ainav-web/src/lib/api.ts:200-205`
- **Purpose**: User registration with email/password
- **Parameters**: `userData: any` - User registration data
- **Returns**: Response object (typically includes new user and token)
- **HTTP**: POST /auth/register with JSON
- **Dependencies**: `fetchAPI()`

#### Skills API

**`getSkills(params?: { tool_id?: string }): Promise<Skill[]>`**
- **Path**: `ainav-web/src/lib/api.ts:214-222`
- **Purpose**: Fetch tool skills/capabilities
- **Parameters**: `params.tool_id?: string` - Optional tool filter
- **Returns**: Array of Skill objects
- **HTTP**: GET /skills?[filter]
- **Dependencies**: `fetchAuthAPI()`, `Skill` type

**`getSkillById(id: string): Promise<Skill>`**
- **Path**: `ainav-web/src/lib/api.ts:227-229`
- **Purpose**: Fetch single skill by ID
- **Parameters**: `id: string` - Skill ID
- **Returns**: Skill object
- **HTTP**: GET /skills/{id}
- **Dependencies**: `fetchAuthAPI()`, `Skill` type

#### Workflows API

**`getWorkflows(params?: { page?: number; limit?: number }): Promise<WorkflowListResponse>`**
- **Path**: `ainav-web/src/lib/api.ts:238-251`
- **Purpose**: Fetch paginated public workflow list
- **Parameters**:
  - `params.page?: number` - Page number (1-indexed)
  - `params.limit?: number` - Items per page
- **Returns**: WorkflowListResponse with pagination
- **HTTP**: GET /workflows?page={p}&limit={l}
- **Dependencies**: `fetchAPI()`, `WorkflowListResponse` type

**`getMyWorkflows(): Promise<AgentWorkflow[]>`**
- **Path**: `ainav-web/src/lib/api.ts:256-258`
- **Purpose**: Fetch current user's workflows
- **Returns**: Array of user-owned workflows
- **HTTP**: GET /workflows/me
- **Authentication**: Required (uses auth token)
- **Dependencies**: `fetchAuthAPI()`, `AgentWorkflow` type

**`getPublicWorkflows(): Promise<AgentWorkflow[]>`**
- **Path**: `ainav-web/src/lib/api.ts:263-265`
- **Purpose**: Fetch publicly available workflows (templates/discovery)
- **Returns**: Array of public workflows
- **HTTP**: GET /workflows/public
- **Dependencies**: `fetchAPI()`, `AgentWorkflow` type

**`getWorkflowById(id: string): Promise<AgentWorkflow>`**
- **Path**: `ainav-web/src/lib/api.ts:270-272`
- **Purpose**: Fetch workflow by ID
- **Parameters**: `id: string` - Workflow ID
- **Returns**: AgentWorkflow object
- **HTTP**: GET /workflows/{id}
- **Dependencies**: `fetchAPI()`, `AgentWorkflow` type

**`getWorkflowBySlug(slug: string): Promise<AgentWorkflow>`**
- **Path**: `ainav-web/src/lib/api.ts:277-279`
- **Purpose**: Fetch workflow by URL slug
- **Parameters**: `slug: string` - Workflow slug
- **Returns**: AgentWorkflow object
- **HTTP**: GET /workflows/slug/{slug}
- **Dependencies**: `fetchAPI()`, `AgentWorkflow` type

**`createWorkflow(data: WorkflowCreate): Promise<AgentWorkflow>`**
- **Path**: `ainav-web/src/lib/api.ts:284-291`
- **Purpose**: Create new workflow
- **Parameters**: `data: WorkflowCreate` - Workflow creation data
- **Returns**: Created AgentWorkflow with ID
- **HTTP**: POST /workflows with JSON
- **Authentication**: Required (uses auth token)
- **Dependencies**: `fetchAuthAPI()`, `AgentWorkflow`, `WorkflowCreate` types

**`updateWorkflow(id: string, data: WorkflowUpdate): Promise<AgentWorkflow>`**
- **Path**: `ainav-web/src/lib/api.ts:296-304`
- **Purpose**: Update existing workflow
- **Parameters**:
  - `id: string` - Workflow ID
  - `data: WorkflowUpdate` - Fields to update
- **Returns**: Updated AgentWorkflow object
- **HTTP**: PUT /workflows/{id} with JSON
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentWorkflow`, `WorkflowUpdate` types

**`deleteWorkflow(id: string): Promise<void>`**
- **Path**: `ainav-web/src/lib/api.ts:309-313`
- **Purpose**: Delete a workflow
- **Parameters**: `id: string` - Workflow ID
- **Returns**: Void (204 No Content)
- **HTTP**: DELETE /workflows/{id}
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

**`forkWorkflow(id: string): Promise<AgentWorkflow>`**
- **Path**: `ainav-web/src/lib/api.ts:318-322`
- **Purpose**: Create a copy of workflow for current user
- **Parameters**: `id: string` - Original workflow ID
- **Returns**: New AgentWorkflow (forked copy)
- **HTTP**: POST /workflows/{id}/fork
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentWorkflow` type

**`starWorkflow(id: string): Promise<void>`**
- **Path**: `ainav-web/src/lib/api.ts:327-331`
- **Purpose**: Mark workflow as favorite
- **Parameters**: `id: string` - Workflow ID
- **Returns**: Void
- **HTTP**: POST /workflows/{id}/star
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

**`unstarWorkflow(id: string): Promise<void>`**
- **Path**: `ainav-web/src/lib/api.ts:336-340`
- **Purpose**: Unmark workflow as favorite
- **Parameters**: `id: string` - Workflow ID
- **Returns**: Void
- **HTTP**: DELETE /workflows/{id}/star
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

#### Executions API

**`runWorkflow(workflowId: string, input: Record<string, unknown>): Promise<AgentExecution>`**
- **Path**: `ainav-web/src/lib/api.ts:349-361`
- **Purpose**: Trigger workflow execution
- **Parameters**:
  - `workflowId: string` - Workflow to execute
  - `input: Record<string, unknown>` - Execution inputs
- **Returns**: AgentExecution record (may be pending)
- **HTTP**: POST /executions/workflows/{id}/run with JSON
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentExecution` type

**`getExecution(id: string): Promise<AgentExecution>`**
- **Path**: `ainav-web/src/lib/api.ts:366-368`
- **Purpose**: Get execution details and status
- **Parameters**: `id: string` - Execution ID
- **Returns**: AgentExecution object
- **HTTP**: GET /executions/{id}
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentExecution` type

**`getExecutions(workflowId: string, params?: { page?: number; limit?: number }): Promise<AgentExecution[]>`**
- **Path**: `ainav-web/src/lib/api.ts:373-389`
- **Purpose**: Fetch execution history for a workflow
- **Parameters**:
  - `workflowId: string` - Workflow ID
  - `params.page?: number` - Page number
  - `params.limit?: number` - Items per page
- **Returns**: Array of AgentExecution objects
- **HTTP**: GET /executions/workflows/{id}?page={p}&limit={l}
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentExecution` type

**`cancelExecution(id: string): Promise<void>`**
- **Path**: `ainav-web/src/lib/api.ts:394-398`
- **Purpose**: Cancel a running execution
- **Parameters**: `id: string` - Execution ID
- **Returns**: Void
- **HTTP**: POST /executions/{id}/cancel
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

**`getMyExecutions(params?: { page?: number; limit?: number; status?: string }): Promise<AgentExecution[]>`**
- **Path**: `ainav-web/src/lib/api.ts:403-418`
- **Purpose**: Fetch all executions for current user
- **Parameters**:
  - `params.page?: number` - Page number
  - `params.limit?: number` - Items per page
  - `params.status?: string` - Filter by status
- **Returns**: Array of AgentExecution objects
- **HTTP**: GET /executions/me?[filters]
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `AgentExecution` type

#### Chat API

**`chatWithAgent(workflowId: string, message: string, sessionId?: string): Promise<ChatResponse>`**
- **Path**: `ainav-web/src/lib/api.ts:427-447`
- **Purpose**: Send message to agent workflow (interactive chat)
- **Parameters**:
  - `workflowId: string` - Workflow ID
  - `message: string` - User message text
  - `sessionId?: string` - Optional session ID for continuity
- **Returns**: ChatResponse with agent's message
- **HTTP**: POST /agents/{id}/chat with JSON
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `ChatResponse` type

**`getSessionHistory(sessionId: string): Promise<ChatMessage[]>`**
- **Path**: `ainav-web/src/lib/api.ts:452-459`
- **Purpose**: Fetch chat session message history
- **Parameters**: `sessionId: string` - Session ID
- **Returns**: Array of ChatMessage objects
- **HTTP**: GET /agents/sessions/{id}/history
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`, `ChatMessage` type

**`clearSessionHistory(sessionId: string): Promise<void>`**
- **Path**: `ainav-web/src/lib/api.ts:464-468`
- **Purpose**: Delete all messages in a session
- **Parameters**: `sessionId: string` - Session ID
- **Returns**: Void
- **HTTP**: DELETE /agents/sessions/{id}
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

**`getMySessions(): Promise<Array<{ session_id: string; workflow_id: string; created_at: string; last_message_at: string; message_count: number }>>`**
- **Path**: `ainav-web/src/lib/api.ts:473-491`
- **Purpose**: Fetch list of current user's chat sessions
- **Returns**: Array of session summary objects
- **HTTP**: GET /agents/sessions/me
- **Authentication**: Required
- **Dependencies**: `fetchAuthAPI()`

### Utility Module (`utils.ts`)

**`cn(...inputs: ClassValue[]): string`**
- **Path**: `ainav-web/src/lib/utils.ts:4-6`
- **Purpose**: Merge Tailwind CSS classes with proper conflict resolution
- **Parameters**: `inputs: ClassValue[]` - Variable number of class strings or objects
- **Returns**: Merged CSS class string
- **Dependencies**: `clsx` library, `tailwind-merge` library
- **Usage Pattern**: Used in React components to conditionally apply Tailwind classes
- **Example**: `cn("px-2", isActive && "bg-blue-500", className)`

### Module Exports (`index.ts`)

**Re-exports**:
- All types from `types.ts` (Category, Tool, Skill, AgentWorkflow, etc.)
- All API functions from `api.ts` (getTools, createWorkflow, etc.)
- **Not exported**: `cn()` utility (imported directly from utils.ts in components)

**Path**: `ainav-web/src/lib/index.ts:1-3`

**Purpose**: Convenience barrel export allowing `import { Tool, getTools } from '@/lib'`

## Dependencies

### External Dependencies (from package.json)

**HTTP & Data Fetching**:
- `fetch` API (native browser API, no external package)

**UI & Styling**:
- `clsx` (^2.1.1) - CSS class merging utility
- `tailwind-merge` (^2.6.0) - Tailwind class conflict resolver
- `@radix-ui/*` (various) - Accessible UI components (used by consuming components)
- `tailwindcss` (^4) - Utility-first CSS framework

**State Management** (used by consuming components):
- `zustand` (^5.0.2) - Lightweight state store
- `@tanstack/react-query` (^5.62.7) - Server state management (potential consumer)

**Form & Validation**:
- `react-hook-form` (^7.54.1) - Form state (potential consumer)
- `zod` (^3.24.1) - TypeScript schema validation (potential consumer)

**Framework**:
- `next` (16.1.1) - React framework (provides fetch polyfill, environment variables)
- `react` (19.2.3) - React library
- `react-dom` (19.2.3) - DOM rendering

**Real-time & Collaboration** (potential consumers):
- `yjs` (^13.6.29) - CRDT for collaborative editing
- `y-webrtc` (^10.3.0) - WebRTC provider for Yjs
- `y-zustand` (^1.1.2) - Zustand binding for Yjs

### Internal Dependencies

**Within lib module**:
- `types.ts` ← `api.ts` (imports all type definitions)
- `index.ts` → `types.ts`, `api.ts` (re-exports)

**Consuming modules** (components, pages):
- All components in `ainav-web/src/components/` consume api functions
- All pages in `ainav-web/src/app/` consume api functions
- React Query hooks wrap api functions for state management
- Form components use types for schema validation

### Backend Service Dependencies

API functions connect to four backend microservices:

1. **Content Service** (`CONTENT_API` - :8001/v1)
   - Provides: Categories, Scenarios, Tools
   - Functions: getCategories, getTools, createTool, etc.

2. **Search Service** (`SEARCH_API` - :8002/v1)
   - Provides: Full-text search
   - Functions: searchTools
   - Technology: Meilisearch

3. **User Service** (`USER_API` - :8003/v1)
   - Provides: Authentication
   - Functions: login, register
   - Technology: FastAPI with OAuth2

4. **Agent Service** (`AGENT_API` - :8005/v1)
   - Provides: Workflows, Skills, Executions, Chat
   - Functions: getWorkflows, runWorkflow, chatWithAgent, etc.
   - Technology: FastAPI with LangGraph

### Environment Configuration

**Build-time Variables** (set during `npm run build`):
- `NEXT_PUBLIC_API_URL` - Content service endpoint
- `NEXT_PUBLIC_SEARCH_API` - Search service endpoint
- `NEXT_PUBLIC_USER_API` - User service endpoint
- `NEXT_PUBLIC_AGENT_API` - Agent service endpoint

**Runtime** (browser localStorage):
- `access_token` - JWT authentication token

## Architecture Patterns

### API Layer Pattern

```
┌─────────────────────────────────────────────────┐
│          React Components/Pages                 │
│         (consume api functions)                 │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│          API Client Module (api.ts)             │
│  ┌─────────────────────────────────────────┐   │
│  │ fetchAPI<T>() / fetchAuthAPI<T>()       │   │
│  │ (generic fetch wrappers)                │   │
│  └──────────────────┬──────────────────────┘   │
│  ┌─────────────────┴──────────────────────┐   │
│  │   Domain-specific API Functions        │   │
│  │  (getTools, createWorkflow, etc.)      │   │
│  └─────────────────┬──────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Backend Microservices                   │
│  Content │ Search │ User │ Agent               │
└──────────────────────────────────────────────────┘
```

### Type Safety Flow

```
Backend Service (FastAPI Pydantic)
      ↓
types.ts (TypeScript Interfaces)
      ↓
api.ts (Typed API Functions)
      ↓
React Components (Type-safe props/data)
```

### Authentication Pattern

```
User Login
    ↓
login() API → access_token stored in localStorage
    ↓
buildAuthHeaders() adds Bearer token to protected endpoints
    ↓
fetchAuthAPI() automatically includes headers
    ↓
Authenticated requests to Agent Service
```

## Relationships Diagram

```mermaid
---
title: Frontend Library Code Architecture
---
classDiagram
    namespace Types {
        class Content["Content Types"]
        class Skill["Skill Types"]
        class Tool["Tool Types"]
        class Workflow["Workflow Types"]
        class Execution["Execution Types"]
        class Chat["Chat Types"]
    }

    namespace APIClient {
        class Fetchers["Fetch Wrappers"]
        class ContentAPI["Content API"]
        class SearchAPI["Search API"]
        class UserAPI["User API"]
        class SkillAPI["Skills API"]
        class WorkflowAPI["Workflow API"]
        class ExecutionAPI["Execution API"]
        class ChatAPI["Chat API"]
    }

    namespace Utils {
        class ClassUtils["Class Utilities"]
    }

    namespace Exports {
        class Barrel["Barrel Export (index.ts)"]
    }

    Fetchers --> Exports
    ContentAPI --> Fetchers
    ContentAPI --> Content
    SearchAPI --> Fetchers
    SearchAPI --> Tool
    UserAPI --> Fetchers
    SkillAPI --> Fetchers
    SkillAPI --> Skill
    WorkflowAPI --> Fetchers
    WorkflowAPI --> Workflow
    ExecutionAPI --> Fetchers
    ExecutionAPI --> Execution
    ChatAPI --> Fetchers
    ChatAPI --> Chat
    Tool --> Content
    Workflow --> Tool
    Execution --> Workflow
    Chat --> Workflow
    ClassUtils --> Exports
```

## Key Design Characteristics

### 1. Type-Safe API Layer
- All API functions return typed objects matching backend Pydantic schemas
- Generic `fetchAPI<T>` and `fetchAuthAPI<T>` provide type inference
- No `any` types in type definitions (except user input DTOs for flexibility)

### 2. Environment-Based Configuration
- Service URLs configured via environment variables
- Defaults to localhost for development
- Production endpoints set at build time via NEXT_PUBLIC_* variables

### 3. Authentication Strategy
- JWT tokens stored in browser localStorage
- Bearer token added automatically to protected endpoints
- `fetchAuthAPI()` handles token injection
- No token refresh logic (tokens expire in 1 hour per backend config)

### 4. Separation of Concerns
- `types.ts` - Data contracts only
- `api.ts` - HTTP communication and service integration
- `utils.ts` - Generic utility functions
- `index.ts` - Public module interface

### 5. Four Microservice Architecture
- Content service handles tool directory data
- Search service provides full-text search via Meilisearch
- User service manages authentication and profiles
- Agent service orchestrates workflow execution and chat

### 6. Pagination Pattern
- Consistent `PaginatedResponse<T>` for list endpoints
- Page-based (not cursor-based) pagination
- Support for skip/limit parameters

### 7. Bilingual Support
- `name_zh` and `description_zh` fields for Chinese translations
- API returns both English and Chinese content
- UI layer handles language selection

## Notes

- The lib module has zero React component dependencies - it's pure data and utilities
- All API functions use native `fetch` API (polyfilled by Next.js in older browsers)
- Error handling is basic (throws Error with message) - caller handles try/catch
- No retry logic or exponential backoff (would be added at React Query layer)
- Chat API supports long-running streams (implementation in consuming component)
- Workflow graph_json serializes React Flow canvas state directly (no schema validation here)
- Skills API exposes OpenAPI-style definitions for agent workflow building
