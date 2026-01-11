import {
  Category,
  Scenario,
  Tool,
  ToolCreate,
  Skill,
  AgentWorkflow,
  AgentExecution,
  WorkflowListResponse,
  WorkflowCreate,
  WorkflowUpdate,
  ChatResponse,
  ChatMessage,
  VersionHistoryEntry,
  VersionComparison,
  WorkflowRevert,
} from "./types";

// =============================================================================
// API BASE URLS
// =============================================================================

const CONTENT_API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/v1";
const SEARCH_API =
  process.env.NEXT_PUBLIC_SEARCH_API || "http://localhost:8002/v1";
const USER_API =
  process.env.NEXT_PUBLIC_USER_API || "http://localhost:8003/v1";
const AGENT_API =
  process.env.NEXT_PUBLIC_AGENT_API || "http://localhost:8005/v1";

// =============================================================================
// AUTH TOKEN HELPERS
// =============================================================================

/**
 * Get the stored auth token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

/**
 * Build headers with optional auth token
 */
function buildAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  if (token) {
    return {
      Authorization: `Bearer ${token}`,
    };
  }
  return {};
}

// =============================================================================
// GENERIC FETCH WRAPPER
// =============================================================================

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI<T>(
  baseUrl: string,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${baseUrl}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch wrapper with authentication
 */
async function fetchAuthAPI<T>(
  baseUrl: string,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  return fetchAPI<T>(baseUrl, endpoint, {
    ...options,
    headers: {
      ...buildAuthHeaders(),
      ...options.headers,
    },
  });
}

// =============================================================================
// CATEGORIES API
// =============================================================================

export async function getCategories(): Promise<Category[]> {
  return fetchAPI<Category[]>(CONTENT_API, "/categories");
}

export async function getCategoryBySlug(slug: string): Promise<Category> {
  return fetchAPI<Category>(CONTENT_API, `/categories/${slug}`);
}

// =============================================================================
// SCENARIOS API
// =============================================================================

export async function getScenarios(): Promise<Scenario[]> {
  return fetchAPI<Scenario[]>(CONTENT_API, "/scenarios");
}

export async function getScenarioBySlug(slug: string): Promise<Scenario> {
  return fetchAPI<Scenario>(CONTENT_API, `/scenarios/${slug}`);
}

export async function getToolsByScenario(slug: string): Promise<Tool[]> {
  return fetchAPI<Tool[]>(CONTENT_API, `/scenarios/${slug}/tools`);
}

// =============================================================================
// TOOLS API
// =============================================================================

export async function getTools(params?: {
  skip?: number;
  limit?: number;
  category_slug?: string;
  scenario_slug?: string;
}): Promise<Tool[]> {
  const searchParams = new URLSearchParams();
  if (params?.skip) searchParams.set("skip", params.skip.toString());
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.category_slug)
    searchParams.set("category_slug", params.category_slug);
  if (params?.scenario_slug)
    searchParams.set("scenario_slug", params.scenario_slug);

  const query = searchParams.toString();
  return fetchAPI<Tool[]>(CONTENT_API, `/tools${query ? `?${query}` : ""}`);
}

export async function getToolBySlug(slug: string): Promise<Tool> {
  return fetchAPI<Tool>(CONTENT_API, `/tools/${slug}`);
}

export async function createTool(tool: ToolCreate): Promise<Tool> {
  return fetchAPI<Tool>(CONTENT_API, "/tools", {
    method: "POST",
    body: JSON.stringify(tool),
  });
}

// =============================================================================
// SEARCH API
// =============================================================================

export async function searchTools(
  query: string,
  category?: string,
  scenario?: string
): Promise<Tool[]> {
  const searchParams = new URLSearchParams({ q: query });
  if (category) searchParams.set("category", category);
  if (scenario) searchParams.set("scenario", scenario);

  return fetchAPI<Tool[]>(SEARCH_API, `/search?${searchParams.toString()}`);
}

// =============================================================================
// USER API
// =============================================================================

export async function login(email: string, password: string): Promise<any> {
  const formData = new FormData();
  formData.append("username", email); // OAuth2 expects 'username'
  formData.append("password", password);

  const response = await fetch(`${USER_API}/auth/login`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "登录失败");
  }

  return response.json();
}

export async function register(userData: any): Promise<any> {
  return fetchAPI<any>(USER_API, "/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
}

// =============================================================================
// SKILLS API (Agent Service)
// =============================================================================

/**
 * Get all skills, optionally filtered by tool
 */
export async function getSkills(params?: {
  tool_id?: string;
}): Promise<Skill[]> {
  const searchParams = new URLSearchParams();
  if (params?.tool_id) searchParams.set("tool_id", params.tool_id);

  const query = searchParams.toString();
  return fetchAPI<Skill[]>(AGENT_API, `/skills${query ? `?${query}` : ""}`);
}

/**
 * Get a skill by ID
 */
export async function getSkillById(id: string): Promise<Skill> {
  return fetchAPI<Skill>(AGENT_API, `/skills/${id}`);
}

// =============================================================================
// WORKFLOWS API (Agent Service)
// =============================================================================

/**
 * Get paginated list of workflows
 */
export async function getWorkflows(params?: {
  page?: number;
  limit?: number;
}): Promise<WorkflowListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.limit) searchParams.set("limit", params.limit.toString());

  const query = searchParams.toString();
  return fetchAPI<WorkflowListResponse>(
    AGENT_API,
    `/workflows${query ? `?${query}` : ""}`
  );
}

/**
 * Get workflows owned by the current user
 */
export async function getMyWorkflows(): Promise<AgentWorkflow[]> {
  return fetchAuthAPI<AgentWorkflow[]>(AGENT_API, "/workflows/me");
}

/**
 * Get public workflows (for discovery/templates)
 */
export async function getPublicWorkflows(): Promise<AgentWorkflow[]> {
  return fetchAPI<AgentWorkflow[]>(AGENT_API, "/workflows/public");
}

/**
 * Get a workflow by ID
 */
export async function getWorkflowById(id: string): Promise<AgentWorkflow> {
  return fetchAPI<AgentWorkflow>(AGENT_API, `/workflows/${id}`);
}

/**
 * Get a workflow by slug
 */
export async function getWorkflowBySlug(slug: string): Promise<AgentWorkflow> {
  return fetchAPI<AgentWorkflow>(AGENT_API, `/workflows/slug/${slug}`);
}

/**
 * Create a new workflow
 */
export async function createWorkflow(
  data: WorkflowCreate
): Promise<AgentWorkflow> {
  return fetchAuthAPI<AgentWorkflow>(AGENT_API, "/workflows", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing workflow
 */
export async function updateWorkflow(
  id: string,
  data: WorkflowUpdate
): Promise<AgentWorkflow> {
  return fetchAuthAPI<AgentWorkflow>(AGENT_API, `/workflows/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a workflow
 */
export async function deleteWorkflow(id: string): Promise<void> {
  await fetchAuthAPI<void>(AGENT_API, `/workflows/${id}`, {
    method: "DELETE",
  });
}

/**
 * Fork an existing workflow (creates a copy for the current user)
 */
export async function forkWorkflow(id: string): Promise<AgentWorkflow> {
  return fetchAuthAPI<AgentWorkflow>(AGENT_API, `/workflows/${id}/fork`, {
    method: "POST",
  });
}

/**
 * Star/favorite a workflow
 */
export async function starWorkflow(id: string): Promise<void> {
  await fetchAuthAPI<void>(AGENT_API, `/workflows/${id}/star`, {
    method: "POST",
  });
}

/**
 * Unstar/unfavorite a workflow
 */
export async function unstarWorkflow(id: string): Promise<void> {
  await fetchAuthAPI<void>(AGENT_API, `/workflows/${id}/star`, {
    method: "DELETE",
  });
}

// =============================================================================
// WORKFLOW VERSION HISTORY API (Agent Service)
// =============================================================================

/**
 * Get version history for a workflow
 */
export async function getWorkflowVersions(
  workflowId: string
): Promise<{
  workflow_id: string;
  current_version: number;
  history: VersionHistoryEntry[];
}> {
  return fetchAuthAPI<{
    workflow_id: string;
    current_version: number;
    history: VersionHistoryEntry[];
  }>(AGENT_API, `/workflows/${workflowId}/versions`);
}

/**
 * Compare two versions of a workflow
 */
export async function compareWorkflowVersions(
  workflowId: string,
  v1: number,
  v2: number
): Promise<VersionComparison> {
  const searchParams = new URLSearchParams();
  searchParams.set("v1", v1.toString());
  searchParams.set("v2", v2.toString());

  return fetchAuthAPI<VersionComparison>(
    AGENT_API,
    `/workflows/${workflowId}/versions/compare?${searchParams.toString()}`
  );
}

/**
 * Revert a workflow to a previous version
 * Creates a new version entry documenting the revert operation
 */
export async function revertWorkflowVersion(
  workflowId: string,
  targetVersion: number
): Promise<AgentWorkflow> {
  const revertData: WorkflowRevert = {
    target_version: targetVersion,
  };

  return fetchAuthAPI<AgentWorkflow>(
    AGENT_API,
    `/workflows/${workflowId}/revert`,
    {
      method: "POST",
      body: JSON.stringify(revertData),
    }
  );
}

// =============================================================================
// EXECUTIONS API (Agent Service)
// =============================================================================

/**
 * Run a workflow with the given input
 */
export async function runWorkflow(
  workflowId: string,
  input: Record<string, unknown>
): Promise<AgentExecution> {
  return fetchAuthAPI<AgentExecution>(
    AGENT_API,
    `/executions/workflows/${workflowId}/run`,
    {
      method: "POST",
      body: JSON.stringify({ input_data: input }),
    }
  );
}

/**
 * Get execution details by ID
 */
export async function getExecution(id: string): Promise<AgentExecution> {
  return fetchAuthAPI<AgentExecution>(AGENT_API, `/executions/${id}`);
}

/**
 * Get all executions for a workflow
 */
export async function getExecutions(
  workflowId: string,
  params?: {
    page?: number;
    limit?: number;
  }
): Promise<AgentExecution[]> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.limit) searchParams.set("limit", params.limit.toString());

  const query = searchParams.toString();
  return fetchAuthAPI<AgentExecution[]>(
    AGENT_API,
    `/executions/workflows/${workflowId}${query ? `?${query}` : ""}`
  );
}

/**
 * Cancel a running execution
 */
export async function cancelExecution(id: string): Promise<void> {
  await fetchAuthAPI<void>(AGENT_API, `/executions/${id}/cancel`, {
    method: "POST",
  });
}

/**
 * Get executions for the current user
 */
export async function getMyExecutions(params?: {
  page?: number;
  limit?: number;
  status?: string;
}): Promise<AgentExecution[]> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.status) searchParams.set("status", params.status);

  const query = searchParams.toString();
  return fetchAuthAPI<AgentExecution[]>(
    AGENT_API,
    `/executions/me${query ? `?${query}` : ""}`
  );
}

// =============================================================================
// CHAT API (Agent Service)
// =============================================================================

/**
 * Send a chat message to an agent workflow
 */
export async function chatWithAgent(
  workflowId: string,
  message: string,
  sessionId?: string
): Promise<ChatResponse> {
  const body: Record<string, unknown> = {
    message,
  };
  if (sessionId) {
    body.session_id = sessionId;
  }

  return fetchAuthAPI<ChatResponse>(
    AGENT_API,
    `/agents/${workflowId}/chat`,
    {
      method: "POST",
      body: JSON.stringify(body),
    }
  );
}

/**
 * Get chat session history
 */
export async function getSessionHistory(
  sessionId: string
): Promise<ChatMessage[]> {
  return fetchAuthAPI<ChatMessage[]>(
    AGENT_API,
    `/agents/sessions/${sessionId}/history`
  );
}

/**
 * Clear chat session history
 */
export async function clearSessionHistory(sessionId: string): Promise<void> {
  await fetchAuthAPI<void>(AGENT_API, `/agents/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

/**
 * Get active chat sessions for the current user
 */
export async function getMySessions(): Promise<
  Array<{
    session_id: string;
    workflow_id: string;
    created_at: string;
    last_message_at: string;
    message_count: number;
  }>
> {
  return fetchAuthAPI<
    Array<{
      session_id: string;
      workflow_id: string;
      created_at: string;
      last_message_at: string;
      message_count: number;
    }>
  >(AGENT_API, "/agents/sessions/me");
}
