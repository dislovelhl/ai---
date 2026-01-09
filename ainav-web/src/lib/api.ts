import { Category, Scenario, Tool, ToolCreate } from "./types";

const CONTENT_API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/v1";
const SEARCH_API =
  process.env.NEXT_PUBLIC_SEARCH_API || "http://localhost:8002/v1";
const USER_API = process.env.NEXT_PUBLIC_USER_API || "http://localhost:8003/v1";

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

// --- Categories API ---

export async function getCategories(): Promise<Category[]> {
  return fetchAPI<Category[]>(CONTENT_API, "/categories");
}

export async function getCategoryBySlug(slug: string): Promise<Category> {
  return fetchAPI<Category>(CONTENT_API, `/categories/${slug}`);
}

// --- Scenarios API ---

export async function getScenarios(): Promise<Scenario[]> {
  return fetchAPI<Scenario[]>(CONTENT_API, "/scenarios");
}

export async function getScenarioBySlug(slug: string): Promise<Scenario> {
  return fetchAPI<Scenario>(CONTENT_API, `/scenarios/${slug}`);
}

export async function getToolsByScenario(slug: string): Promise<Tool[]> {
  return fetchAPI<Tool[]>(CONTENT_API, `/scenarios/${slug}/tools`);
}

// --- Tools API ---

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

// --- Search API ---

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

// --- User API ---

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
