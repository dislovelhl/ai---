"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { getTools, searchTools, getCategories } from "@/lib/api";
import { ToolCard } from "@/components/tools/tool-card";
import { ToolFilters } from "@/components/tools/tool-filters";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { Footer } from "@/components/layout/footer";
import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { Tool } from "@/lib/types";

function ToolsContent() {
  const searchParams = useSearchParams();
  const urlCategory = searchParams.get("category");
  const searchQuery = searchParams.get("search");

  // Filter and sort state
  const [selectedCategory, setSelectedCategory] = useState<string>(
    urlCategory || "all"
  );
  const [selectedPricing, setSelectedPricing] = useState<string>("all");
  const [selectedSort, setSelectedSort] = useState<string>("rating");
  const [selectedAccessibility, setSelectedAccessibility] =
    useState<string>("all");

  const {
    data: tools,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["tools", urlCategory, searchQuery],
    queryFn: () => {
      if (searchQuery) {
        return searchTools(searchQuery);
      }
      return getTools({
        category_slug: urlCategory || undefined,
        limit: 100,
      });
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => getCategories(),
  });

  // Filter and sort tools
  const filteredAndSortedTools = useMemo(() => {
    if (!tools) return [];

    let filtered = [...tools];

    // Apply pricing filter
    if (selectedPricing !== "all") {
      filtered = filtered.filter(
        (tool) => tool.pricing_type === selectedPricing
      );
    }

    // Apply accessibility filter
    if (selectedAccessibility === "china-accessible") {
      filtered = filtered.filter((tool) => tool.is_china_accessible === true);
    } else if (selectedAccessibility === "vpn-required") {
      filtered = filtered.filter((tool) => tool.requires_vpn === true);
    }

    // Apply sorting
    if (selectedSort === "rating") {
      filtered.sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0));
    } else if (selectedSort === "name") {
      filtered.sort((a, b) => a.name.localeCompare(b.name, "zh-CN"));
    } else if (selectedSort === "newest") {
      filtered.sort(
        (a, b) =>
          new Date(b.created_at || 0).getTime() -
          new Date(a.created_at || 0).getTime()
      );
    }

    return filtered;
  }, [tools, selectedPricing, selectedAccessibility, selectedSort]);

  const handleClearFilters = () => {
    setSelectedCategory("all");
    setSelectedPricing("all");
    setSelectedAccessibility("all");
    setSelectedSort("rating");
  };

  return (
    <div className="max-w-7xl mx-auto">
      <header className="mb-6 sm:mb-8 lg:mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium mb-3 sm:mb-4">
          <span>工具库</span>
        </div>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2 sm:mb-3 tracking-tight">
          发现顶尖 AI 生产力
        </h1>
        <p className="text-muted-foreground text-sm sm:text-base lg:text-lg">
          探索全球最优秀的 AI 工具与服务，助力你的工作与生活。
        </p>
      </header>

      {/* Filters and Sort */}
      <div className="mb-6 sm:mb-8">
        <ToolFilters
          categories={categories}
          selectedCategory={selectedCategory}
          selectedPricing={selectedPricing}
          selectedSort={selectedSort}
          selectedAccessibility={selectedAccessibility}
          onCategoryChange={setSelectedCategory}
          onPricingChange={setSelectedPricing}
          onSortChange={setSelectedSort}
          onAccessibilityChange={setSelectedAccessibility}
          onClearFilters={handleClearFilters}
        />
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-96 gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
          <p className="text-sm text-muted-foreground animate-pulse">
            正在为您搜寻最前沿的 AI 工具...
          </p>
        </div>
      ) : error ? (
        <div className="p-6 sm:p-8 lg:p-12 bg-destructive/5 text-destructive border border-destructive/10 rounded-2xl sm:rounded-3xl text-center">
          <p className="font-bold mb-2 text-sm sm:text-base">出错了</p>
          <p className="text-xs sm:text-sm opacity-80">
            无法加载工具信息，请检查您的网络连接或稍后重试。
          </p>
        </div>
      ) : (
        <>
          {/* Results count */}
          {filteredAndSortedTools.length > 0 && (
            <div className="mb-4 text-sm text-muted-foreground">
              找到 <span className="font-semibold text-foreground">{filteredAndSortedTools.length}</span> 个工具
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
            {filteredAndSortedTools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        </>
      )}

      {!isLoading &&
        (!filteredAndSortedTools || filteredAndSortedTools.length === 0) && (
          <div className="text-center py-16 sm:py-20 lg:py-24 bg-secondary/20 rounded-2xl sm:rounded-[3rem] border-2 border-dashed">
            <p className="text-muted-foreground text-sm sm:text-base lg:text-lg">
              暂无符合条件的工具，请尝试调整筛选条件...
            </p>
          </div>
        )}
    </div>
  );
}

export default function ToolsPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-4 sm:p-6 lg:p-10">
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-96">
                <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
              </div>
            }
          >
            <ToolsContent />
          </Suspense>
        </main>
      </div>
      <Footer />
    </div>
  );
}
