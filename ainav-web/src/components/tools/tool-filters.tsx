"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Globe,
  Zap,
  Gift,
  Coins,
  CreditCard,
  FlaskConical,
  Github
} from "lucide-react";
import { FacetCounts, SearchFilters } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ToolFiltersProps {
  filters: SearchFilters;
  facets?: FacetCounts;
  onFiltersChange: (filters: SearchFilters) => void;
  className?: string;
}

const pricingTypeLabels: Record<string, { label: string; icon: React.ComponentType<{ className?: string }> }> = {
  free: { label: "完全免费", icon: Gift },
  freemium: { label: "免费额度", icon: Coins },
  paid: { label: "付费", icon: CreditCard },
  beta_free: { label: "公测免费", icon: FlaskConical },
  open_source: { label: "开源", icon: Github },
};

export function ToolFilters({
  filters,
  facets,
  onFiltersChange,
  className
}: ToolFiltersProps) {

  const handleChinaAccessibleChange = (checked: boolean) => {
    onFiltersChange({
      ...filters,
      is_china_accessible: checked || undefined,
    });
  };

  const handleHasApiChange = (checked: boolean) => {
    onFiltersChange({
      ...filters,
      has_api: checked || undefined,
    });
  };

  const handlePricingTypeChange = (pricingType: string, checked: boolean) => {
    if (checked) {
      onFiltersChange({
        ...filters,
        pricing_type: pricingType as SearchFilters['pricing_type'],
      });
    } else {
      // Only clear if the unchecked type matches the current filter
      if (filters.pricing_type === pricingType) {
        onFiltersChange({
          ...filters,
          pricing_type: undefined,
        });
      }
    }
  };

  return (
    <Card className={cn("glass border-border/50 rounded-2xl", className)}>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold">筛选工具</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* China Accessibility Filter */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">访问性</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="china-accessible"
                  checked={filters.is_china_accessible === true}
                  onCheckedChange={handleChinaAccessibleChange}
                />
                <Label
                  htmlFor="china-accessible"
                  className="text-sm font-normal cursor-pointer flex items-center gap-1.5"
                >
                  <Globe className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                  国内可用
                </Label>
              </div>
              {facets?.is_china_accessible && (
                <Badge
                  variant="outline"
                  className="text-xs bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400"
                >
                  {facets.is_china_accessible.accessible}
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* API Availability Filter */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">功能特性</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="has-api"
                  checked={filters.has_api === true}
                  onCheckedChange={handleHasApiChange}
                />
                <Label
                  htmlFor="has-api"
                  className="text-sm font-normal cursor-pointer flex items-center gap-1.5"
                >
                  <Zap className="h-3.5 w-3.5 text-violet-600 dark:text-violet-400" />
                  支持 API / Skills
                </Label>
              </div>
              {facets?.has_api && (
                <Badge
                  variant="outline"
                  className="text-xs bg-violet-500/10 text-violet-600 border-violet-500/20 dark:text-violet-400"
                >
                  {facets.has_api.with_api}
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Pricing Type Filter */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">定价模式</h3>
          <div className="space-y-2">
            {Object.entries(pricingTypeLabels).map(([type, config]) => {
              const Icon = config.icon;
              const count = facets?.pricing_type?.[type] || 0;

              return (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id={`pricing-${type}`}
                      checked={filters.pricing_type === type}
                      onCheckedChange={(checked) => handlePricingTypeChange(type, checked as boolean)}
                    />
                    <Label
                      htmlFor={`pricing-${type}`}
                      className="text-sm font-normal cursor-pointer flex items-center gap-1.5"
                    >
                      <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                      {config.label}
                    </Label>
                  </div>
                  {count > 0 && (
                    <Badge
                      variant="outline"
                      className="text-xs"
                    >
                      {count}
                    </Badge>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
