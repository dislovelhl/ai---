"use client";

import { useQuery } from "@tanstack/react-query";
import { getToolBySlug, getTools, getToolAlternatives } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { ToolCard } from "@/components/tools/tool-card";
import { ToolAlternatives } from "@/components/tools/tool-alternatives";
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

  const { data: alternatives, isLoading: alternativesLoading } = useQuery({
    queryKey: ["tool-alternatives", slug],
    queryFn: () => getToolAlternatives(slug),
    enabled: !!tool,
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
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <h2 className="text-2xl font-bold">未找到该工具</h2>
          <Button onClick={() => router.push("/tools")}>返回工具列表</Button>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      <main className="flex-1 py-12">
        <div className="container mx-auto px-4 max-w-6xl">
          {/* Breadcrumbs */}
          <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-8">
            <Link href="/" className="hover:text-primary transition-colors">
              首页
            </Link>
            <ChevronRight className="w-4 h-4" />
            <Link
              href="/tools"
              className="hover:text-primary transition-colors"
            >
              工具库
            </Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-foreground font-medium">{tool.name}</span>
          </nav>

          <div className="grid lg:grid-cols-3 gap-12">
            {/* Left Column: Tool Info */}
            <div className="lg:col-span-2 space-y-12">
              <div className="flex flex-col md:flex-row gap-8 items-start">
                <div className="relative w-32 h-32 rounded-3xl overflow-hidden border-2 border-primary/10 glass flex-shrink-0">
                  {tool.logo_url ? (
                    <Image
                      src={tool.logo_url}
                      alt={tool.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-4xl font-bold opacity-10">
                      {tool.name[0]}
                    </div>
                  )}
                </div>

                <div className="flex-1 space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <h1 className="text-4xl font-black tracking-tight">
                      {tool.name}
                    </h1>
                    {tool.name_zh && (
                      <span className="text-2xl text-muted-foreground font-medium">
                        / {tool.name_zh}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <AccessBadge
                      isAccessible={tool.is_china_accessible}
                      requiresVpn={tool.requires_vpn}
                    />
                    {tool.pricing_type && (
                      <PricingBadge type={tool.pricing_type} />
                    )}
                    {tool.category && (
                      <Badge
                        variant="secondary"
                        className="bg-primary/5 text-primary border-primary/10"
                      >
                        {tool.category.name}
                      </Badge>
                    )}
                  </div>

                  <p className="text-xl text-muted-foreground leading-relaxed">
                    {tool.description_zh || tool.description}
                  </p>

                  <div className="flex flex-wrap gap-4 pt-4">
                    <Button
                      size="lg"
                      className="h-14 px-8 rounded-full text-lg font-bold shadow-lg shadow-primary/20 hover:scale-105 transition-transform"
                      asChild
                    >
                      <a
                        href={tool.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        访问官网 <ExternalLink className="ml-2 w-5 h-5" />
                      </a>
                    </Button>
                    <Button
                      variant="outline"
                      size="lg"
                      className="h-14 px-8 rounded-full text-lg glass hover:scale-105 transition-transform"
                    >
                      立即收藏
                    </Button>
                  </div>
                </div>
              </div>

              {/* Description & Features */}
              <section className="space-y-6">
                <h2 className="text-2xl font-bold">详细介绍</h2>
                <div className="prose prose-slate dark:prose-invert max-w-none glass p-8 rounded-[2rem] border-2">
                  {tool.description_zh ? (
                    <div className="space-y-6">
                      <p className="text-lg leading-relaxed">
                        {tool.description_zh}
                      </p>
                      <hr className="border-primary/10" />
                      <div className="text-muted-foreground italic">
                        <p className="font-semibold mb-2">
                          English Description:
                        </p>
                        <p>{tool.description}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-lg leading-relaxed">
                      {tool.description}
                    </p>
                  )}
                </div>
              </section>

              {/* Scenarios */}
              {tool.scenarios && tool.scenarios.length > 0 && (
                <section className="space-y-6">
                  <h2 className="text-2xl font-bold">应用场景</h2>
                  <div className="flex flex-wrap gap-4">
                    {tool.scenarios.map((s) => (
                      <Link key={s.id} href={`/scenarios/${s.slug}`}>
                        <div className="flex items-center gap-3 px-6 py-4 rounded-2xl glass border-2 hover:border-primary/30 transition-all hover:scale-105 group">
                          {s.icon && <span className="text-2xl">{s.icon}</span>}
                          <span className="font-bold group-hover:text-primary transition-colors">
                            {s.name}
                          </span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}

              {/* Tool Alternatives */}
              <ToolAlternatives
                alternatives={alternatives?.alternatives || []}
                isLoading={alternativesLoading}
                originalToolRequiresVpn={tool.requires_vpn}
              />
            </div>

            {/* Right Column: Stats & Sidebar */}
            <div className="space-y-8">
              <div className="glass rounded-[2rem] border-2 p-8 space-y-6 shrink-0">
                <h3 className="text-xl font-bold border-b pb-4 border-primary/10">
                  工具信息
                </h3>

                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Star className="w-5 h-5 fill-amber-500 text-amber-500" />
                      <span>评分</span>
                    </div>
                    <span className="font-bold text-xl">
                      {tool.avg_rating.toFixed(1)}{" "}
                      <span className="text-sm font-normal text-muted-foreground">
                        ({tool.review_count} 评价)
                      </span>
                    </span>
                  </div>

                  {tool.github_stars !== undefined && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Github className="w-5 h-5" />
                        <span>GitHub Stars</span>
                      </div>
                      <span className="font-bold text-xl">
                        {tool.github_stars?.toLocaleString()}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Layers className="w-5 h-5 text-primary" />
                      <span>分类</span>
                    </div>
                    <span className="font-bold">
                      {tool.category?.name || "未分类"}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="w-5 h-5" />
                      <span>入库时间</span>
                    </div>
                    <span className="font-bold">
                      {new Date(tool.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Related Tools */}
              <div className="space-y-6">
                <h3 className="text-xl font-bold">相关推荐</h3>
                <div className="space-y-6">
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
