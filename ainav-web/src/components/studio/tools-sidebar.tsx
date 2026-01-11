"use client";

import { useState, DragEvent } from "react";
import { Search, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Tool } from "@/lib/types";
import { DraggableToolCard } from "@/components/tools/draggable-tool-card";

// Mock data for development - will be replaced with API call
const mockTools: Tool[] = [
  {
    id: "1",
    name: "GitHub",
    slug: "github",
    description: "Code hosting and version control platform",
    url: "https://github.com",
    logo_url:
      "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
    is_china_accessible: true,
    requires_vpn: false,
    avg_rating: 4.8,
    review_count: 1200,
    has_api: true,
    scenarios: [],
    skills: [
      {
        id: "s1",
        tool_id: "1",
        name: "Search Repositories",
        name_zh: "搜索仓库",
        slug: "search-repos",
        description: "Search GitHub repositories",
        api_endpoint: "https://api.github.com/search/repositories",
        http_method: "GET",
        auth_type: "bearer",
        is_active: true,
        usage_count: 0,
        avg_latency_ms: 0,
        created_at: "",
        updated_at: "",
      },
      {
        id: "s2",
        tool_id: "1",
        name: "Get User Info",
        name_zh: "获取用户信息",
        slug: "get-user",
        description: "Get GitHub user information",
        api_endpoint: "https://api.github.com/users/{username}",
        http_method: "GET",
        auth_type: "bearer",
        is_active: true,
        usage_count: 0,
        avg_latency_ms: 0,
        created_at: "",
        updated_at: "",
      },
    ],
    created_at: "",
    updated_at: "",
  },
  {
    id: "2",
    name: "Notion",
    slug: "notion",
    description: "All-in-one workspace for notes and docs",
    url: "https://notion.so",
    is_china_accessible: false,
    requires_vpn: true,
    avg_rating: 4.7,
    review_count: 890,
    has_api: true,
    scenarios: [],
    skills: [
      {
        id: "s3",
        tool_id: "2",
        name: "Create Page",
        name_zh: "创建页面",
        slug: "create-page",
        description: "Create a new Notion page",
        api_endpoint: "https://api.notion.com/v1/pages",
        http_method: "POST",
        auth_type: "bearer",
        is_active: true,
        usage_count: 0,
        avg_latency_ms: 0,
        created_at: "",
        updated_at: "",
      },
    ],
    created_at: "",
    updated_at: "",
  },
];

/**
 * ToolsSidebar - Shows tools with Skills that can be dragged onto the canvas.
 * Includes search functionality and lazy loading.
 */
export function ToolsSidebar() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // TODO: Replace with actual API call
  const tools = mockTools.filter(
    (tool) =>
      tool.has_api &&
      (tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description?.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const onDragStart = (event: DragEvent, tool: Tool) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: "skill",
        data: {
          tool: tool,
          skill: tool.skills?.[0] || null, // Default to first skill
        },
      })
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">
          工具 & 技能
        </h3>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索有 API 的工具..."
            className="pl-9 h-9 bg-muted/50"
          />
        </div>
      </div>

      {/* Tool List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : tools.length > 0 ? (
          tools.map((tool) => (
            <div
              key={tool.id}
              draggable
              onDragStart={(e) => onDragStart(e, tool)}
            >
              <DraggableToolCard tool={tool} />
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-muted-foreground text-sm">
            {searchQuery ? "没有找到匹配的工具" : "没有可用的工具"}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-muted/30">
        <p className="text-[10px] text-muted-foreground text-center">
          仅显示有 API 集成的工具
        </p>
      </div>
    </div>
  );
}
