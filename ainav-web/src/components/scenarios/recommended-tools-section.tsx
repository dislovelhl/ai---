"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ToolCard } from "@/components/tools/tool-card";
import { Loader2, Trophy, Medal, Award, Star } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ToolRecommendation } from "@/lib/types";

interface RecommendedToolsSectionProps {
  recommendations: ToolRecommendation[];
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

const RANKING_CONFIG = [
  {
    rank: 1,
    icon: Trophy,
    label: "最佳推荐",
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
  },
  {
    rank: 2,
    icon: Medal,
    label: "优秀推荐",
    color: "text-slate-400",
    bgColor: "bg-slate-400/10",
    borderColor: "border-slate-400/20",
  },
  {
    rank: 3,
    icon: Award,
    label: "推荐",
    color: "text-orange-600",
    bgColor: "bg-orange-600/10",
    borderColor: "border-orange-600/20",
  },
  {
    rank: 4,
    icon: Star,
    label: "推荐",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/20",
  },
  {
    rank: 5,
    icon: Star,
    label: "推荐",
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/20",
  },
];

export function RecommendedToolsSection({
  recommendations,
  isLoading = false,
  error = null,
  className,
}: RecommendedToolsSectionProps) {
  if (isLoading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            热门推荐
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 gap-4">
            <Loader2 className="w-8 h-8 animate-spin text-primary/50" />
            <p className="text-sm text-muted-foreground">
              正在加载推荐工具...
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            热门推荐
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-8 bg-destructive/5 text-destructive border border-destructive/10 rounded-2xl text-center">
            <p className="font-bold mb-2">加载失败</p>
            <p className="text-sm opacity-80">无法加载推荐工具信息。</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            热门推荐
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 bg-secondary/20 rounded-2xl border-2 border-dashed">
            <p className="text-muted-foreground">
              暂无推荐工具，请稍后再试。
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-amber-500" />
          热门推荐
        </CardTitle>
        <p className="text-sm text-muted-foreground mt-2">
          根据用户互动和评分精选的最佳工具
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {recommendations.slice(0, 5).map((recommendation, index) => {
          const rankConfig = RANKING_CONFIG[index] || RANKING_CONFIG[4];
          const RankIcon = rankConfig.icon;
          const scorePercentage = Math.round(
            recommendation.recommendation_score * 100
          );

          return (
            <div key={recommendation.tool.id} className="relative">
              {/* Ranking Badge */}
              <div className="absolute -left-3 -top-3 z-10">
                <div
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-full border-2 shadow-lg backdrop-blur-sm",
                    rankConfig.bgColor,
                    rankConfig.borderColor
                  )}
                >
                  <RankIcon className={cn("h-4 w-4", rankConfig.color)} />
                  <span
                    className={cn(
                      "text-xs font-bold",
                      rankConfig.color
                    )}
                  >
                    {rankConfig.label}
                  </span>
                </div>
              </div>

              {/* Tool Card */}
              <div className="relative">
                <ToolCard tool={recommendation.tool} />

                {/* Recommendation Score Overlay */}
                <div className="absolute bottom-3 right-3 z-10">
                  <Badge
                    variant="secondary"
                    className="backdrop-blur-md bg-background/80 border shadow-lg"
                  >
                    <Star className="h-3 w-3 mr-1 fill-amber-500 text-amber-500" />
                    <span className="text-xs font-semibold">
                      推荐度 {scorePercentage}%
                    </span>
                  </Badge>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
