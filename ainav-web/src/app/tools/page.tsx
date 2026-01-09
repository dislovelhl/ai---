"use client";

import { useQuery } from "@tanstack/react-query";
import { getTools, searchTools } from "@/lib/api";
import { ToolCard } from "@/components/tools/tool-card";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { Footer } from "@/components/layout/footer";
import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function ToolsContent() {
  const searchParams = useSearchParams();
  const category = searchParams.get("category");
  const searchQuery = searchParams.get("search");

  const {
    data: tools,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["tools", category, searchQuery],
    queryFn: () => {
      if (searchQuery) {
        return searchTools(searchQuery);
      }
      return getTools({
        category_slug: category || undefined,
        limit: 50,
      });
    },
  });

  return (
    <div className="max-w-6xl mx-auto">
      <header className="mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
          <span>工具库</span>
        </div>
        <h1 className="text-4xl font-bold mb-3 tracking-tight">
          发现顶尖 AI 生产力
        </h1>
        <p className="text-muted-foreground text-lg">
          探索全球最优秀的 AI 工具与服务，助力你的工作与生活。
        </p>
      </header>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-96 gap-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
          <p className="text-sm text-muted-foreground animate-pulse">
            正在为您搜寻最前沿的 AI 工具...
          </p>
        </div>
      ) : error ? (
        <div className="p-12 bg-destructive/5 text-destructive border border-destructive/10 rounded-3xl text-center">
          <p className="font-bold mb-2">出错了</p>
          <p className="text-sm opacity-80">
            无法加载工具信息，请检查您的网络连接或稍后重试。
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {tools?.map((tool) => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      )}

      {!isLoading && (!tools || tools.length === 0) && (
        <div className="text-center py-24 bg-secondary/20 rounded-[3rem] border-2 border-dashed">
          <p className="text-muted-foreground text-lg">
            暂无工具信息，我们正在马不停蹄地更新中...
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
        <main className="flex-1 p-6 md:p-10">
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
