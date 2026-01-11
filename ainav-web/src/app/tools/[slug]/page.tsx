"use client";

import { useQuery } from "@tanstack/react-query";
import { getToolBySlug, getTools } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { ToolCard } from "@/components/tools/tool-card";
import { PricingBadge } from "@/components/tools/pricing-badge";
import { AccessBadge } from "@/components/tools/access-badge";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ExternalLink,
  Star,
  Github,
  Calendar,
  Layers,
  ChevronRight,
  Loader2,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useParams, useRouter } from "next/navigation";

export default function ToolDetailPage() {
  const { slug } = useParams() as { slug: string };
  const router = useRouter();

  const {
    data: tool,
    isLoading: toolLoading,
    error,
  } = useQuery({
    queryKey: ["tool", slug],
    queryFn: () => getToolBySlug(slug),
  });

  const { data: relatedTools, isLoading: relatedLoading } = useQuery({
    queryKey: ["related-tools", tool?.category?.slug],
    queryFn: () =>
      getTools({
        category_slug: tool?.category?.slug || undefined,
        limit: 4,
      }),
    enabled: !!tool?.category?.slug,
  });

  if (toolLoading) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-10 h-10 animate-spin text-primary/50" />
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !tool) {
    return (
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <div className="flex-1 flex flex-col items-center justify-center gap-3 sm:gap-4 px-4">
          <h2 className="text-xl sm:text-2xl font-bold text-center">未找到该工具</h2>
          <Button
            onClick={() => router.push("/tools")}
            className="min-h-[44px] touch-manipulation active:scale-[0.98] transition-transform"
          >
            返回工具列表
          </Button>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 py-6 sm:py-8 md:py-12">
        <div className="container mx-auto px-4 sm:px-6 max-w-6xl">
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-muted-foreground mb-4 sm:mb-6 md:mb-8 overflow-x-auto">
            <Link
              href="/"
              className="hover:text-primary transition-colors min-h-[44px] flex items-center whitespace-nowrap"
            >
              首页
            </Link>
            <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 shrink-0" />
            <Link
              href="/tools"
              className="hover:text-primary transition-colors min-h-[44px] flex items-center whitespace-nowrap"
            >
              工具库
            </Link>
            <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 shrink-0" />
            <span className="text-foreground font-medium min-h-[44px] flex items-center truncate">{tool.name}</span>
          </nav>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 md:gap-12">
            {/* Left Column: Tool Info */}
            <div className="lg:col-span-2 space-y-6 sm:space-y-8 md:space-y-12">
              <div className="flex flex-col md:flex-row gap-4 sm:gap-6 md:gap-8 items-start">
                <div className="relative w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 rounded-2xl sm:rounded-3xl overflow-hidden border-2 border-primary/10 glass flex-shrink-0">
                  {tool.logo_url ? (
                    <Image
                      src={tool.logo_url}
                      alt={tool.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-2xl sm:text-3xl md:text-4xl font-bold opacity-10">
                      {tool.name[0]}
                    </div>
                  )}
                </div>

                <div className="flex-1 space-y-3 sm:space-y-4">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                    <h1 className="text-2xl sm:text-3xl md:text-4xl font-black tracking-tight">
                      {tool.name}
                    </h1>
                    {tool.name_zh && (
                      <span className="text-lg sm:text-xl md:text-2xl text-muted-foreground font-medium">
                        / {tool.name_zh}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <AccessBadge
                      isAccessible={tool.is_china_accessible}
                      requiresVpn={tool.requires_vpn}
                      className="text-xs sm:text-sm"
                    />
                    {tool.pricing_type && (
                      <PricingBadge type={tool.pricing_type} className="text-xs sm:text-sm" />
                    )}
                    {tool.category && (
                      <Badge
                        variant="secondary"
                        className="bg-primary/5 text-primary border-primary/10 text-xs sm:text-sm"
                      >
                        {tool.category.name}
                      </Badge>
                    )}
                  </div>

                  <p className="text-base sm:text-lg md:text-xl text-muted-foreground leading-relaxed">
                    {tool.description_zh || tool.description}
                  </p>

                  <div className="flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-4 pt-2 sm:pt-4">
                    <Button
                      size="lg"
                      className="min-h-[44px] sm:h-12 md:h-14 px-6 sm:px-8 rounded-full text-base sm:text-lg font-bold shadow-lg shadow-primary/20 hover:scale-105 active:scale-[0.98] transition-transform touch-manipulation w-full sm:w-auto"
                      asChild
                    >
                      <a
                        href={tool.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        访问官网 <ExternalLink className="ml-2 w-4 h-4 sm:w-5 sm:h-5" />
                      </a>
                    </Button>
                    <Button
                      variant="outline"
                      size="lg"
                      className="min-h-[44px] sm:h-12 md:h-14 px-6 sm:px-8 rounded-full text-base sm:text-lg glass hover:scale-105 active:scale-[0.98] transition-transform touch-manipulation w-full sm:w-auto"
                    >
                      立即收藏
                    </Button>
                  </div>
                </div>
              </div>

              {/* Description & Features */}
              <section className="space-y-4 sm:space-y-6">
                <h2 className="text-xl sm:text-2xl font-bold">详细介绍</h2>
                <div className="prose prose-slate dark:prose-invert max-w-none glass p-4 sm:p-6 md:p-8 rounded-2xl sm:rounded-[2rem] border-2">
                  {tool.description_zh ? (
                    <div className="space-y-4 sm:space-y-6">
                      <p className="text-sm sm:text-base md:text-lg leading-relaxed">
                        {tool.description_zh}
                      </p>
                      <hr className="border-primary/10" />
                      <div className="text-muted-foreground italic">
                        <p className="font-semibold mb-2 text-sm sm:text-base">
                          English Description:
                        </p>
                        <p className="text-sm sm:text-base">{tool.description}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm sm:text-base md:text-lg leading-relaxed">
                      {tool.description}
                    </p>
                  )}
                </div>
              </section>

              {/* Scenarios */}
              {tool.scenarios && tool.scenarios.length > 0 && (
                <section className="space-y-4 sm:space-y-6">
                  <h2 className="text-xl sm:text-2xl font-bold">应用场景</h2>
                  <div className="flex flex-wrap gap-2 sm:gap-3 md:gap-4">
                    {tool.scenarios.map((s) => (
                      <Link
                        key={s.id}
                        href={`/scenarios/${s.slug}`}
                        className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-2xl"
                      >
                        <div className="flex items-center gap-2 sm:gap-3 px-4 sm:px-5 md:px-6 min-h-[44px] py-3 sm:py-4 rounded-xl sm:rounded-2xl glass border-2 hover:border-primary/30 transition-all hover:scale-105 active:scale-[0.98] touch-manipulation group">
                          {s.icon && <span className="text-lg sm:text-xl md:text-2xl">{s.icon}</span>}
                          <span className="font-bold text-sm sm:text-base group-hover:text-primary transition-colors">
                            {s.name}
                          </span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}
            </div>

            {/* Right Column: Stats & Sidebar */}
            <div className="space-y-6 sm:space-y-8">
              <div className="glass rounded-2xl sm:rounded-[2rem] border-2 p-4 sm:p-6 md:p-8 space-y-4 sm:space-y-6 shrink-0">
                <h3 className="text-lg sm:text-xl font-bold border-b pb-3 sm:pb-4 border-primary/10">
                  工具信息
                </h3>

                <div className="space-y-4 sm:space-y-6">
                  <div className="flex items-center justify-between min-h-[44px]">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm sm:text-base">
                      <Star className="w-4 h-4 sm:w-5 sm:h-5 fill-amber-500 text-amber-500" />
                      <span>评分</span>
                    </div>
                    <span className="font-bold text-lg sm:text-xl">
                      {tool.avg_rating.toFixed(1)}{" "}
                      <span className="text-xs sm:text-sm font-normal text-muted-foreground">
                        ({tool.review_count} 评价)
                      </span>
                    </span>
                  </div>

                  {tool.github_stars !== undefined && (
                    <div className="flex items-center justify-between min-h-[44px]">
                      <div className="flex items-center gap-2 text-muted-foreground text-sm sm:text-base">
                        <Github className="w-4 h-4 sm:w-5 sm:h-5" />
                        <span>GitHub Stars</span>
                      </div>
                      <span className="font-bold text-lg sm:text-xl">
                        {tool.github_stars?.toLocaleString()}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center justify-between min-h-[44px]">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm sm:text-base">
                      <Layers className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                      <span>分类</span>
                    </div>
                    <span className="font-bold text-sm sm:text-base">
                      {tool.category?.name || "未分类"}
                    </span>
                  </div>

                  <div className="flex items-center justify-between min-h-[44px]">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm sm:text-base">
                      <Calendar className="w-4 h-4 sm:w-5 sm:h-5" />
                      <span>入库时间</span>
                    </div>
                    <span className="font-bold text-sm sm:text-base">
                      {new Date(tool.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Related Tools */}
              <div className="space-y-4 sm:space-y-6">
                <h3 className="text-lg sm:text-xl font-bold">相关推荐</h3>
                <div className="space-y-4 sm:space-y-6">
                  {relatedLoading ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-6 h-6 animate-spin text-primary/30" />
                    </div>
                  ) : (
                    relatedTools
                      ?.filter((t) => t.id !== tool.id)
                      .slice(0, 3)
                      .map((rt) => <ToolCard key={rt.id} tool={rt} />)
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
