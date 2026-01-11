"use client";

import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Sparkles,
  Zap,
  Shield,
  Target,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { getTools, getScenarios } from "@/lib/api";
import { ToolCard } from "@/components/tools/tool-card";
import { SearchHero } from "@/components/home/search-hero";
import { ScenarioChips } from "@/components/home/scenario-chips";

export default function Home() {
  const { data: tools, isLoading: toolsLoading } = useQuery({
    queryKey: ["featured-tools"],
    queryFn: () => getTools({ limit: 6 }),
  });

  const { data: scenarios, isLoading: scenariosLoading } = useQuery({
    queryKey: ["popular-scenarios"],
    queryFn: () => getScenarios(),
  });

  return (
    <>
      <Navbar />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative pt-20 pb-16 sm:pt-24 sm:pb-20 md:pt-28 md:pb-24 lg:pt-32 overflow-hidden">
          <div className="absolute inset-0 bg-grid-pattern opacity-5 pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background pointer-events-none" />

          <div className="container relative mx-auto px-4 sm:px-6 text-center z-10">
            <div className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-full bg-primary/10 text-primary text-xs sm:text-sm font-medium mb-6 sm:mb-8 animate-in fade-in zoom-in duration-500">
              <Sparkles className="h-3 w-3 sm:h-3.5 sm:w-3.5 shrink-0" />
              <span className="whitespace-nowrap">AI 时代的数字前哨</span>
            </div>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 sm:mb-8 px-2 animate-in fade-in slide-in-from-bottom-6 duration-700">
              探索 <span className="text-gradient">最好的免费 AI 工具</span>
            </h1>

            <p className="max-w-xl mx-auto text-base sm:text-lg text-muted-foreground mb-8 sm:mb-10 md:mb-12 px-4 leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-900">
              不仅仅是导航，更是你的认知升级中枢。
              <br className="hidden sm:block" />
              全网精选，场景赋能，助你驾驭 AI 浪潮。
            </p>

            <div className="animate-in fade-in slide-in-from-bottom-10 duration-1000">
              <SearchHero />
              <ScenarioChips />
            </div>

            {/* Stats / Trust Badges - Simplified */}
            <div className="mt-16 sm:mt-20 md:mt-24 grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 md:gap-6 max-w-3xl mx-auto opacity-70 hover:opacity-100 transition-opacity duration-500 animate-in fade-in slide-in-from-bottom-12 duration-1200 delay-300">
              {[
                { label: "精选工具", value: "5,000+" },
                { label: "应用场景", value: "100+" },
                { label: "内容更新", value: "24/7" },
                { label: "活跃用户", value: "50k+" },
              ].map((stat, i) => (
                <div key={i} className="text-center p-3 sm:p-4">
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground mb-1">
                    {stat.value}
                  </div>
                  <div className="text-xs sm:text-sm text-muted-foreground uppercase tracking-wider">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Featured Tools Section */}
        <section className="py-12 sm:py-16 md:py-20 lg:py-24">
          <div className="container mx-auto px-4 sm:px-6">
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 sm:gap-0 mb-8 sm:mb-10 md:mb-12">
              <div>
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-2 sm:mb-3 md:mb-4">热门推荐</h2>
                <p className="text-sm sm:text-base text-muted-foreground">
                  为大家精选的当下最热门 AI 工具
                </p>
              </div>
              <Link
                href="/tools"
                className="text-primary font-semibold hover:underline flex items-center gap-1 min-h-[44px] self-start sm:self-auto"
              >
                查看全部 <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {toolsLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary/50" />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
                {tools?.map((tool) => (
                  <ToolCard key={tool.id} tool={tool} />
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Categories Section */}
        <section className="py-12 sm:py-16 md:py-20 lg:py-24 bg-secondary/20">
          <div className="container mx-auto px-4 sm:px-6">
            <div className="text-center mb-10 sm:mb-12 md:mb-16">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4">为什么选择 AI 导航</h2>
              <p className="text-sm sm:text-base text-muted-foreground">我们不仅仅是链接的搬运工</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
              {[
                {
                  title: "深度测评",
                  desc: "每一款工具都经过我们的专业团队亲自测试，确保真实可靠。",
                  icon: Shield,
                  color: "blue",
                },
                {
                  title: "快速响应",
                  desc: "秒级搜索响应，即刻找到你需要的 AI 解决方案。",
                  icon: Zap,
                  color: "amber",
                },
                {
                  title: "专注实战",
                  desc: "提供大量实战案例与变现路径，让 AI 真正落地产生价值。",
                  icon: Target,
                  color: "emerald",
                },
              ].map((feature, i) => (
                <div
                  key={i}
                  className="glass p-6 sm:p-7 md:p-8 rounded-2xl sm:rounded-3xl group hover:shadow-2xl transition-all duration-500 active:scale-[0.98]"
                >
                  <div
                    className={`w-11 h-11 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-${feature.color}-500/10 flex items-center justify-center mb-5 sm:mb-6 group-hover:scale-110 transition-transform`}
                  >
                    <feature.icon
                      className={`h-5 w-5 sm:h-6 sm:w-6 text-${feature.color}-500`}
                    />
                  </div>
                  <h3 className="text-lg sm:text-xl md:text-2xl font-bold mb-2 sm:mb-3">{feature.title}</h3>
                  <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
