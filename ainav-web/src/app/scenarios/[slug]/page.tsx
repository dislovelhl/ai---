"use client";

import { useQuery } from "@tanstack/react-query";
import { getTools, getScenarios } from "@/lib/api";
import { ToolCard } from "@/components/tools/tool-card";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { Footer } from "@/components/layout/footer";
import { Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function ScenarioPage() {
  const { slug } = useParams();
  const scenarioSlug = typeof slug === "string" ? slug : "";

  // Fetch scenario details to get the name
  const { data: scenarios = [] } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => getScenarios(),
  });

  const scenario = scenarios.find((s) => s.slug === scenarioSlug);

  const {
    data: tools,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["tools", "scenario", scenarioSlug],
    queryFn: () => getTools({ scenario_slug: scenarioSlug, limit: 50 }),
    enabled: !!scenarioSlug,
  });

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-10">
          <div className="max-w-6xl mx-auto">
            <Link
              href="/scenarios"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary mb-8 group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              返回应用场景
            </Link>

            <header className="mb-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
                <span>应用场景</span>
              </div>
              <h1 className="text-4xl font-bold mb-3 tracking-tight">
                {scenario?.name || "加载中..."}
              </h1>
              <p className="text-muted-foreground text-lg">
                专门为「{scenario?.name || scenarioSlug}」场景精选的 AI 工具。
              </p>
            </header>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-96 gap-4">
                <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
                <p className="text-sm text-muted-foreground">
                  正在搜寻最佳匹配工具...
                </p>
              </div>
            ) : error ? (
              <div className="p-12 bg-destructive/5 text-destructive border border-destructive/10 rounded-3xl text-center">
                <p className="font-bold mb-2">出错了</p>
                <p className="text-sm opacity-80">无法加载工具信息。</p>
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
                  当前场景暂无推荐工具，请换个场景看看吧。
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
