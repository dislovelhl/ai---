// API Types matching backend Pydantic schemas

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  order: number;
  created_at: string;
  updated_at: string;
  tool_count?: number;
}

export interface Scenario {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// SKILL TYPES
// =============================================================================

export interface Skill {
  id: string;
  tool_id: string;
  name: string;
  name_zh?: string;
  slug: string;
  description?: string;
  description_zh?: string;
  api_endpoint?: string;
  http_method?: string;
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  headers_template?: Record<string, string>;
  auth_type: "api_key" | "oauth2" | "bearer" | "none";
  auth_config?: Record<string, unknown>;
  is_active: boolean;
  usage_count: number;
  avg_latency_ms: number;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// TOOL TYPES
// =============================================================================

export interface Tool {
  id: string;
  name: string;
  name_zh?: string;
  slug: string;
  description?: string;
  description_zh?: string;
  url: string;
  logo_url?: string;
  pricing_type?: "free" | "freemium" | "paid" | "beta_free" | "open_source";
  is_china_accessible: boolean;
  requires_vpn: boolean;
  avg_rating: number;
  review_count: number;
  github_stars?: number;
  has_api?: boolean;
  category?: Category;
  scenarios: Scenario[];
  skills?: Skill[];
  created_at: string;
  updated_at: string;
}

export interface ToolCreate {
  name: string;
  slug: string;
  description?: string;
  url: string;
  logo_url?: string;
  pricing_type?: string;
  is_china_accessible?: boolean;
  requires_vpn?: boolean;
  category_id?: string;
  scenario_ids?: string[];
}

// =============================================================================
// AGENT WORKFLOW TYPES
// =============================================================================

export interface ReactFlowNode {
  id: string;
  type: "input" | "output" | "llm" | "skill" | "transform" | "condition";
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface ReactFlowGraph {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
  viewport?: { x: number; y: number; zoom: number };
}

export interface AgentWorkflow {
  id: string;
  user_id: string;
  name: string;
  name_zh?: string;
  slug: string;
  description?: string;
  description_zh?: string;
  icon?: string;
  graph_json: ReactFlowGraph;
  trigger_type: "manual" | "schedule" | "webhook";
  trigger_config?: Record<string, unknown>;
  input_schema?: Record<string, unknown>;
  llm_model: string;
  system_prompt?: string;
  temperature: number;
  is_public: boolean;
  is_template: boolean;
  forked_from_id?: string;
  fork_count: number;
  run_count: number;
  star_count: number;
  created_at: string;
  updated_at: string;
}

export interface AgentWorkflowCreate {
  name: string;
  slug: string;
  description?: string;
  graph_json: ReactFlowGraph;
  trigger_type?: string;
  trigger_config?: Record<string, unknown>;
  input_schema?: Record<string, unknown>;
  llm_model?: string;
  system_prompt?: string;
  temperature?: number;
  is_public?: boolean;
  is_template?: boolean;
}

export interface AgentWorkflowSummary {
  id: string;
  name: string;
  name_zh?: string;
  slug: string;
  description?: string;
  icon?: string;
  trigger_type: string;
  is_public: boolean;
  fork_count: number;
  run_count: number;
  star_count: number;
  created_at: string;
}

// =============================================================================
// AGENT EXECUTION TYPES
// =============================================================================

export interface NodeExecutionLog {
  node_id: string;
  node_type: string;
  status: "pending" | "running" | "success" | "error" | "skipped";
  input_data?: unknown;
  output_data?: unknown;
  error_message?: string;
  duration_ms?: number;
  timestamp: string;
}

export interface AgentExecution {
  id: string;
  workflow_id: string;
  user_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  input_data?: Record<string, unknown>;
  output_data?: unknown;
  error_message?: string;
  execution_log?: NodeExecutionLog[];
  token_usage: number;
  total_api_calls: number;
  duration_ms?: number;
  trigger_type?: string;
  trigger_metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AgentExecutionSummary {
  id: string;
  workflow_id: string;
  status: string;
  duration_ms?: number;
  token_usage: number;
  trigger_type?: string;
  created_at: string;
}

// =============================================================================
// COMMON RESPONSE TYPES
// =============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface SearchResult {
  tools: Tool[];
  total: number;
  query: string;
}

// =============================================================================
// AGENT CHAT TYPES
// =============================================================================

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  workflow_id: string;
  tokens_used?: number;
}

// =============================================================================
// WORKFLOW API TYPES
// =============================================================================

export interface WorkflowListResponse {
  items: AgentWorkflowSummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface WorkflowCreate {
  name: string;
  name_zh?: string;
  slug: string;
  description?: string;
  description_zh?: string;
  icon?: string;
  graph_json: ReactFlowGraph;
  trigger_type?: "manual" | "schedule" | "webhook";
  trigger_config?: Record<string, unknown>;
  input_schema?: Record<string, unknown>;
  llm_model?: string;
  system_prompt?: string;
  temperature?: number;
  is_public?: boolean;
  is_template?: boolean;
}

export interface WorkflowUpdate {
  name?: string;
  name_zh?: string;
  description?: string;
  description_zh?: string;
  icon?: string;
  graph_json?: ReactFlowGraph;
  trigger_type?: "manual" | "schedule" | "webhook";
  trigger_config?: Record<string, unknown>;
  input_schema?: Record<string, unknown>;
  llm_model?: string;
  system_prompt?: string;
  temperature?: number;
  is_public?: boolean;
  is_template?: boolean;
}

export interface ExecutionCreate {
  input_data?: Record<string, unknown>;
  trigger_type?: string;
  trigger_metadata?: Record<string, unknown>;
}

// =============================================================================
// EXECUTION TRACKING TYPES (Real-Time Debugging)
// =============================================================================

/**
 * Node execution status enum
 * Represents the current state of a node during workflow execution
 */
export enum NodeExecutionStatus {
  PENDING = "pending",
  RUNNING = "running",
  SUCCESS = "success",
  ERROR = "error",
  SKIPPED = "skipped",
  COMPLETED = "completed",
  FAILED = "failed",
}

/**
 * Detailed execution step information
 * Matches backend ExecutionStepDetail schema
 */
export interface ExecutionStep {
  node_id: string;
  status: NodeExecutionStatus;
  input_data?: unknown;
  output_data?: unknown;
  error_message?: string;
  token_usage?: {
    input: number;
    output: number;
    total: number;
  };
  started_at?: string;
  completed_at?: string;
  checkpoint?: string;  // Compressed state snapshot for replay
}

/**
 * WebSocket message for execution updates
 * Sent in real-time as nodes execute
 */
export interface ExecutionStepUpdate {
  execution_id: string;
  node_id: string;
  status: NodeExecutionStatus;
  input_data?: unknown;
  output_data?: unknown;
  error_message?: string;
  token_usage?: {
    input: number;
    output: number;
    total: number;
  };
  timestamp: string;
}

/**
 * Detailed execution response including all steps
 * Matches backend ExecutionDetailsResponse schema
 */
export interface ExecutionDetails {
  id: string;
  workflow_id: string;
  user_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  input_data?: Record<string, unknown>;
  output_data?: unknown;
  error_message?: string;
  execution_steps?: ExecutionStep[];
  token_usage: number;
  total_api_calls: number;
  duration_ms?: number;
  trigger_type?: string;
  trigger_metadata?: Record<string, unknown>;
  parent_execution_id?: string;
  replayed_from_step?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Execution replay request
 */
export interface ExecutionReplayRequest {
  from_step_id: string;
}

/**
 * Execution replay response
 */
export interface ExecutionReplayResponse {
  new_execution_id: string;
  parent_execution_id: string;
  replayed_from_step: string;
  status: string;
  message: string;
}
