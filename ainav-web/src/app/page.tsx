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
        <section className="relative pt-20 pb-32 overflow-hidden bg-grid">
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/90 to-background pointer-events-none" />

          <div className="container relative mx-auto px-4 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <Sparkles className="h-3 w-3" />
              <span>发现人工智能的无限可能</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
              开启你的 <span className="text-gradient">AI 进化</span> 旅程
            </h1>

            <p className="max-w-2xl mx-auto text-lg text-muted-foreground mb-10 leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-900">
              AI 导航是一个专业的 AI 工具发现平台。我们为你精选全球最前沿的 AI
              技术， 从创意生产到商业变现，助你全面拥抱 AI 时代。
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-10 duration-1000">
              <Link href="/tools">
                <Button
                  size="lg"
                  className="h-14 px-8 rounded-full text-lg group"
                >
                  立即探索{" "}
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/learn">
                <Button
                  size="lg"
                  variant="outline"
                  className="h-14 px-8 rounded-full text-lg glass"
                >
                  查看教程
                </Button>
              </Link>
            </div>

            {/* Stats / Trust Badges */}
            <div className="mt-20 grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1200">
              <div className="glass p-6 rounded-2xl">
                <div className="text-3xl font-bold text-primary mb-1">
                  5,000+
                </div>
                <div className="text-sm text-muted-foreground">精选工具</div>
              </div>
              <div className="glass p-6 rounded-2xl">
                <div className="text-3xl font-bold text-primary mb-1">100+</div>
                <div className="text-sm text-muted-foreground">应用场景</div>
              </div>
              <div className="glass p-6 rounded-2xl">
                <div className="text-3xl font-bold text-primary mb-1">24/7</div>
                <div className="text-sm text-muted-foreground">内容更新</div>
              </div>
              <div className="glass p-6 rounded-2xl">
                <div className="text-3xl font-bold text-primary mb-1">50k+</div>
                <div className="text-sm text-muted-foreground">活跃用户</div>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Tools Section */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <div className="flex items-end justify-between mb-12">
              <div>
                <h2 className="text-3xl font-bold mb-4">热门推荐</h2>
                <p className="text-muted-foreground">
                  为大家精选的当下最热门 AI 工具
                </p>
              </div>
              <Link
                href="/tools"
                className="text-primary font-semibold hover:underline flex items-center gap-1"
              >
                查看全部 <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {toolsLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary/50" />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                {tools?.map((tool) => (
                  <ToolCard key={tool.id} tool={tool} />
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Categories Section */}
        <section className="py-24 bg-secondary/20">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">为什么选择 AI 导航</h2>
              <p className="text-muted-foreground">我们不仅仅是链接的搬运工</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
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
                  className="glass p-8 rounded-3xl group hover:shadow-2xl transition-all duration-500"
                >
                  <div
                    className={`w-12 h-12 rounded-2xl bg-${feature.color}-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}
                  >
                    <feature.icon
                      className={`h-6 w-6 text-${feature.color}-500`}
                    />
                  </div>
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
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
