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
  category?: Category;
  scenarios: Scenario[];
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
