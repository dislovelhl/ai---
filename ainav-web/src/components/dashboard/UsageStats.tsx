"use client";

import { UsageStats as UsageStatsType } from "@/lib/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TrendingUp, Zap, AlertTriangle, Crown, Sparkles } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface UsageStatsProps {
  data: UsageStatsType;
  isLoading?: boolean;
}

/**
 * UsageStats - Display user's workflow execution quota and usage statistics
 * Shows progress bar, tier badge, and upgrade CTA for free users near limit
 */
export function UsageStats({ data, isLoading }: UsageStatsProps) {
  if (isLoading) {
    return (
      <Card className="border-muted/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="h-5 w-32 bg-muted/50 rounded animate-pulse" />
              <div className="h-4 w-48 bg-muted/30 rounded animate-pulse" />
            </div>
            <div className="h-6 w-16 bg-muted/50 rounded-full animate-pulse" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-4 w-full bg-muted/30 rounded-full animate-pulse" />
            <div className="h-3 w-24 bg-muted/30 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const usagePercentage = Math.min(100, (data.used / data.limit) * 100);
  const isNearLimit = usagePercentage >= 80;
  const isAtLimit = data.remaining <= 0;
  const isFree = data.tier === "free";

  // Get tier display info
  const getTierInfo = () => {
    switch (data.tier) {
      case "free":
        return {
          label: "免费版",
          variant: "secondary" as const,
          icon: Sparkles,
        };
      case "pro":
        return {
          label: "专业版",
          variant: "default" as const,
          icon: Zap,
        };
      case "enterprise":
        return {
          label: "企业版",
          variant: "default" as const,
          icon: Crown,
        };
      default:
        return {
          label: data.tier,
          variant: "secondary" as const,
          icon: Sparkles,
        };
    }
  };

  const tierInfo = getTierInfo();
  const TierIcon = tierInfo.icon;

  // Format reset time
  const resetDate = new Date(data.reset_at);
  const now = new Date();
  const hoursUntilReset = Math.ceil(
    (resetDate.getTime() - now.getTime()) / (1000 * 60 * 60)
  );

  return (
    <Card className="border-muted/50 bg-gradient-to-br from-card/80 to-card/50 backdrop-blur-sm hover:shadow-lg transition-all duration-300">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" aria-hidden="true" />
              API 使用量
            </CardTitle>
            <CardDescription className="mt-1">
              当前执行次数统计
            </CardDescription>
          </div>
          <Badge
            variant={tierInfo.variant}
            className={cn(
              "gap-1.5 px-3 py-1",
              data.tier === "pro" &&
                "bg-gradient-to-r from-violet-500 to-purple-600 text-white border-0",
              data.tier === "enterprise" &&
                "bg-gradient-to-r from-amber-500 to-orange-600 text-white border-0"
            )}
          >
            <TierIcon className="w-3.5 h-3.5" aria-hidden="true" />
            {tierInfo.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-baseline justify-between text-sm">
            <span className="font-medium">
              已使用{" "}
              <span className="text-2xl font-bold text-primary">
                {data.used}
              </span>
              <span className="text-muted-foreground"> / {data.limit}</span>
            </span>
            <span className="text-muted-foreground">
              剩余 <span className="font-semibold">{data.remaining}</span> 次
            </span>
          </div>
          <Progress
            value={data.used}
            max={data.limit}
            className="h-3"
            indicatorClassName={cn(
              "transition-all duration-500",
              isAtLimit && "bg-destructive",
              isNearLimit && !isAtLimit && "bg-amber-500",
              !isNearLimit && "bg-primary"
            )}
            aria-label={`使用进度: ${usagePercentage.toFixed(0)}%`}
          />
          <p className="text-xs text-muted-foreground">
            将在 {hoursUntilReset} 小时后重置
          </p>
        </div>

        {/* Warning Alert for Near Limit */}
        {isNearLimit && isFree && !isAtLimit && (
          <Alert
            variant="warning"
            className="border-amber-500/50 bg-amber-50 dark:bg-amber-950/30"
          >
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-sm">
              你的额度即将用尽。升级到专业版以获取更多执行次数。
            </AlertDescription>
          </Alert>
        )}

        {/* At Limit Alert */}
        {isAtLimit && isFree && (
          <Alert
            variant="destructive"
            className="border-destructive/50 bg-destructive/5"
          >
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-sm">
              你已达到每日执行限额。升级账户或等待额度重置。
            </AlertDescription>
          </Alert>
        )}

        {/* Upgrade CTA for Free Users Near Limit */}
        {isFree && isNearLimit && (
          <div className="pt-2">
            <Link href="/pricing" className="block">
              <Button
                className="w-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300"
                size="sm"
              >
                <Zap className="w-4 h-4 mr-2" aria-hidden="true" />
                升级到专业版
                <span className="ml-2 text-xs opacity-90">
                  500 次/天
                </span>
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
