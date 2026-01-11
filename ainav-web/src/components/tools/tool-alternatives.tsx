"use client";

import { Tool } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PricingBadge } from "./pricing-badge";
import { AccessBadge } from "./access-badge";
import { Star, Sparkles, ArrowRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface ToolAlternativesProps {
  alternatives: Tool[];
  isLoading?: boolean;
  originalToolRequiresVpn?: boolean;
  className?: string;
}

export function ToolAlternatives({
  alternatives,
  isLoading = false,
  originalToolRequiresVpn = false,
  className,
}: ToolAlternativesProps) {
  if (isLoading) {
    return (
      <section className={cn("space-y-6", className)}>
        <div className="flex items-center gap-3">
          <Sparkles className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold">相似工具</h2>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="glass rounded-3xl border-2 p-6 space-y-4"
            >
              <div className="flex items-start gap-4">
                <Skeleton className="w-16 h-16 rounded-2xl flex-shrink-0" />
                <div className="flex-1 space-y-3">
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-16" />
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (!alternatives || alternatives.length === 0) {
    return (
      <section className={cn("space-y-6", className)}>
        <div className="flex items-center gap-3">
          <Sparkles className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold">相似工具</h2>
        </div>
        <div className="glass rounded-3xl border-2 p-12 text-center">
          <p className="text-muted-foreground text-lg">
            暂无相似工具推荐
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className={cn("space-y-6", className)}>
      <div className="flex items-center gap-3">
        <Sparkles className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-bold">相似工具</h2>
        {originalToolRequiresVpn && (
          <Badge className="bg-primary/10 text-primary border-primary/20">
            <Star className="w-3 h-3 mr-1 fill-current" />
            优先推荐国内直连
          </Badge>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {alternatives.map((tool) => {
          const isChinaAccessible =
            tool.is_china_accessible && !tool.requires_vpn;
          const isPrioritized = originalToolRequiresVpn && isChinaAccessible;

          return (
            <Link key={tool.id} href={`/tools/${tool.slug}`}>
              <Card
                className={cn(
                  "group overflow-hidden border-none glass hover:shadow-2xl transition-all duration-500 rounded-3xl h-full",
                  isPrioritized && "ring-2 ring-primary/50 bg-primary/5"
                )}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-4 mb-4">
                    {/* Logo */}
                    <div className="relative w-16 h-16 rounded-2xl overflow-hidden border border-primary/10 flex-shrink-0 bg-secondary/30">
                      {tool.logo_url ? (
                        <Image
                          src={tool.logo_url}
                          alt={`${tool.name} - AI 工具图标`}
                          fill
                          className="object-cover group-hover:scale-110 transition-transform duration-500"
                        />
                      ) : (
                        <div
                          className="w-full h-full flex items-center justify-center group-hover:scale-110 transition-transform duration-500"
                          role="presentation"
                          aria-hidden="true"
                        >
                          <span className="text-2xl font-bold opacity-20">
                            {tool.name[0]}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Title and Description */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="text-lg font-bold group-hover:text-primary transition-colors line-clamp-1">
                          {tool.name}
                        </h3>
                        {isPrioritized && (
                          <Badge
                            className="bg-primary text-primary-foreground border-0 shadow-md flex-shrink-0"
                            aria-label="国内直连推荐"
                          >
                            <Star className="w-3 h-3 mr-1 fill-current" />
                            推荐
                          </Badge>
                        )}
                      </div>

                      <p className="text-muted-foreground text-sm line-clamp-2 mb-3">
                        {tool.description_zh || tool.description}
                      </p>

                      {/* Rating */}
                      <div
                        className="flex items-center gap-1 text-amber-500 mb-3"
                        role="img"
                        aria-label={`评分 ${tool.avg_rating.toFixed(1)} 分（满分 5 分）`}
                      >
                        <Star className="w-4 h-4 fill-current" aria-hidden="true" />
                        <span className="text-sm font-semibold">
                          {tool.avg_rating.toFixed(1)}
                        </span>
                        <span className="text-xs text-muted-foreground ml-1">
                          ({tool.review_count})
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <AccessBadge
                      isAccessible={tool.is_china_accessible}
                      requiresVpn={tool.requires_vpn}
                    />
                    {tool.pricing_type && (
                      <PricingBadge type={tool.pricing_type} />
                    )}
                    {tool.category && (
                      <Badge
                        variant="outline"
                        className="text-xs bg-primary/5 text-primary border-primary/20"
                      >
                        {tool.category.name}
                      </Badge>
                    )}
                  </div>

                  {/* Scenarios */}
                  {tool.scenarios && tool.scenarios.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {tool.scenarios.slice(0, 3).map((s) => (
                        <span
                          key={s.id}
                          className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground/50 bg-muted/30 rounded-full px-2 py-0.5"
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Hover indicator */}
                  <div className="flex items-center justify-end mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-sm text-primary font-medium flex items-center gap-1">
                      查看详情
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
