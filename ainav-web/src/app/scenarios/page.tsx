"use client";

import { useQuery } from "@tanstack/react-query";
import { getScenarios } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { Footer } from "@/components/layout/footer";
import { Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";

export default function ScenariosPage() {
  const {
    data: scenarios,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => getScenarios(),
  });

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-10">
          <div className="max-w-6xl mx-auto">
            <header className="mb-10 text-center md:text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
                <span>应用场景</span>
              </div>
              <h1 className="text-4xl font-bold mb-3 tracking-tight">
                按场景发现 AI 的价值
              </h1>
              <p className="text-muted-foreground text-lg">
                针对不同行业与需求，为您精选最契合的 AI 解决方案。
              </p>
            </header>

            {isLoading ? (
              <div className="flex items-center justify-center h-96">
                <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
              </div>
            ) : error ? (
              <div className="p-12 bg-destructive/5 text-destructive border border-destructive/10 rounded-3xl text-center">
                <p className="font-bold">无法加载场景信息</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {scenarios?.map((s) => (
                  <Link key={s.id} href={`/scenarios/${s.slug}`}>
                    <Card className="group h-full glass border-none hover:shadow-2xl transition-all duration-500 rounded-3xl overflow-hidden relative">
                      <CardContent className="p-8">
                        <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 text-primary group-hover:scale-110 transition-transform">
                          <span className="text-2xl">{s.icon || "💡"}</span>
                        </div>
                        <h3 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                          {s.name}
                        </h3>
                        <p className="text-muted-foreground text-sm mb-6">
                          寻找适用于 {s.name} 的最佳 AI 工具与实战案例。
                        </p>
                        <div className="flex items-center gap-2 text-primary font-semibold text-sm">
                          立即进入{" "}
                          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            )}

            {!isLoading && (!scenarios || scenarios.length === 0) && (
              <div className="text-center py-24 bg-secondary/20 rounded-[3rem] border-2 border-dashed">
                <p className="text-muted-foreground text-lg">暂无场景分类</p>
              </div>
            )}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
