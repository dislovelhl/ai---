"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Gift,
  Coins,
  CreditCard,
  FlaskConical,
  Github,
  Globe,
  ShieldCheck,
  X,
  Filter,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ToolFilters } from "@/lib/types";

interface ToolFiltersProps {
  filters: ToolFilters;
  onFiltersChange: (filters: ToolFilters) => void;
  className?: string;
}

type PricingTypeOption = "free" | "freemium" | "paid" | "beta_free" | "open_source";

const pricingOptions: {
  value: PricingTypeOption;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { value: "free", label: "完全免费", icon: Gift },
  { value: "freemium", label: "免费额度", icon: Coins },
  { value: "paid", label: "付费", icon: CreditCard },
  { value: "beta_free", label: "公测免费", icon: FlaskConical },
  { value: "open_source", label: "开源", icon: Github },
];

const accessOptions = [
  {
    value: "china_accessible",
    label: "国内直连",
    icon: Globe,
    filter: { is_china_accessible: true, requires_vpn: false },
  },
  {
    value: "vpn_required",
    label: "需要VPN",
    icon: ShieldCheck,
    filter: { is_china_accessible: false, requires_vpn: true },
  },
];

export function ToolFilters({
  filters,
  onFiltersChange,
  className,
}: ToolFiltersProps) {
  const handlePricingChange = (pricing: PricingTypeOption) => {
    if (filters.pricing_type === pricing) {
      // Deselect if already selected
      const { pricing_type, ...rest } = filters;
      onFiltersChange(rest);
    } else {
      onFiltersChange({ ...filters, pricing_type: pricing });
    }
  };

  const handleAccessChange = (option: typeof accessOptions[0]) => {
    const isChinaAccessible = option.value === "china_accessible";
    const currentMatch =
      filters.is_china_accessible === isChinaAccessible &&
      filters.requires_vpn === !isChinaAccessible;

    if (currentMatch) {
      // Deselect if already selected
      const { is_china_accessible, requires_vpn, ...rest } = filters;
      onFiltersChange(rest);
    } else {
      onFiltersChange({ ...filters, ...option.filter });
    }
  };

  const handleClearFilters = () => {
    onFiltersChange({});
  };

  const activeFilterCount = Object.keys(filters).length;

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-muted-foreground" />
            <CardTitle>筛选工具</CardTitle>
            {activeFilterCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFilterCount}
              </Badge>
            )}
          </div>
          {activeFilterCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFilters}
              className="h-8 px-2 lg:px-3"
            >
              <X className="h-4 w-4 mr-1" />
              清空
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Pricing Type Filters */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-foreground">定价模式</h3>
          <div className="flex flex-wrap gap-2">
            {pricingOptions.map((option) => {
              const Icon = option.icon;
              const isActive = filters.pricing_type === option.value;
              return (
                <Button
                  key={option.value}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => handlePricingChange(option.value)}
                  className={cn(
                    "h-8 rounded-full transition-all",
                    isActive
                      ? "shadow-md"
                      : "hover:border-primary/50 hover:bg-primary/5"
                  )}
                >
                  <Icon className="h-3.5 w-3.5 mr-1.5" />
                  {option.label}
                </Button>
              );
            })}
          </div>
        </div>

        {/* China Accessibility Filters */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-foreground">国内访问</h3>
          <div className="flex flex-wrap gap-2">
            {accessOptions.map((option) => {
              const Icon = option.icon;
              const isChinaAccessible = option.value === "china_accessible";
              const isActive =
                filters.is_china_accessible === isChinaAccessible &&
                filters.requires_vpn === !isChinaAccessible;

              return (
                <Button
                  key={option.value}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleAccessChange(option)}
                  className={cn(
                    "h-8 rounded-full transition-all",
                    isActive
                      ? "shadow-md"
                      : "hover:border-primary/50 hover:bg-primary/5"
                  )}
                >
                  <Icon className="h-3.5 w-3.5 mr-1.5" />
                  {option.label}
                </Button>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
