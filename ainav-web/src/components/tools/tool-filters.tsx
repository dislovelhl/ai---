"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SlidersHorizontal, ArrowUpDown, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface ToolFiltersProps {
  categories?: Category[];
  selectedCategory?: string;
  selectedPricing?: string;
  selectedSort?: string;
  selectedAccessibility?: string;
  onCategoryChange: (category: string) => void;
  onPricingChange: (pricing: string) => void;
  onSortChange: (sort: string) => void;
  onAccessibilityChange: (accessibility: string) => void;
  onClearFilters: () => void;
}

export function ToolFilters({
  categories = [],
  selectedCategory,
  selectedPricing,
  selectedSort,
  selectedAccessibility,
  onCategoryChange,
  onPricingChange,
  onSortChange,
  onAccessibilityChange,
  onClearFilters,
}: ToolFiltersProps) {
  const [open, setOpen] = useState(false);

  const activeFilterCount = [
    selectedCategory,
    selectedPricing,
    selectedAccessibility,
  ].filter((v) => v && v !== "all").length;

  const handleClearFilters = () => {
    onClearFilters();
    setOpen(false);
  };

  const FilterContent = () => (
    <div className="space-y-6">
      {/* Category Filter */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-foreground">
          工具分类
        </label>
        <Select value={selectedCategory || "all"} onValueChange={onCategoryChange}>
          <SelectTrigger className="min-h-[44px]" aria-label="选择工具分类">
            <SelectValue placeholder="全部分类" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部分类</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.slug}>
                {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Pricing Filter */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-foreground">
          定价模式
        </label>
        <Select
          value={selectedPricing || "all"}
          onValueChange={onPricingChange}
        >
          <SelectTrigger className="min-h-[44px]" aria-label="选择定价模式">
            <SelectValue placeholder="全部价格" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部价格</SelectItem>
            <SelectItem value="free">免费</SelectItem>
            <SelectItem value="freemium">部分免费</SelectItem>
            <SelectItem value="paid">付费</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Accessibility Filter */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-foreground">
          访问方式
        </label>
        <Select
          value={selectedAccessibility || "all"}
          onValueChange={onAccessibilityChange}
        >
          <SelectTrigger className="min-h-[44px]" aria-label="选择访问方式">
            <SelectValue placeholder="全部工具" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部工具</SelectItem>
            <SelectItem value="china-accessible">国内可访问</SelectItem>
            <SelectItem value="vpn-required">需要 VPN</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Sort Options */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-foreground">
          排序方式
        </label>
        <Select value={selectedSort || "rating"} onValueChange={onSortChange}>
          <SelectTrigger className="min-h-[44px]" aria-label="选择排序方式">
            <SelectValue placeholder="按评分" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="rating">评分最高</SelectItem>
            <SelectItem value="name">名称 A-Z</SelectItem>
            <SelectItem value="newest">最新添加</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );

  return (
    <div className="flex items-center gap-2 sm:gap-3">
      {/* Mobile Sheet */}
      <div className="lg:hidden">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="default"
              className="relative min-h-[44px] gap-2 active:scale-[0.98] transition-transform touch-manipulation"
              aria-label={`筛选和排序${activeFilterCount > 0 ? ` (${activeFilterCount} 个筛选项已激活)` : ""}`}
            >
              <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">筛选</span>
              {activeFilterCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-[10px]"
                  aria-label={`${activeFilterCount} 个筛选项已激活`}
                >
                  {activeFilterCount}
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent
            side="bottom"
            className="max-h-[85vh] overflow-y-auto rounded-t-3xl"
          >
            <SheetHeader className="text-left">
              <SheetTitle className="text-xl font-bold">筛选和排序</SheetTitle>
              <SheetDescription>
                根据您的需求筛选和排序 AI 工具
              </SheetDescription>
            </SheetHeader>
            <div className="py-6">
              <FilterContent />
            </div>
            {activeFilterCount > 0 && (
              <SheetFooter>
                <Button
                  variant="outline"
                  onClick={handleClearFilters}
                  className="w-full min-h-[44px] gap-2 active:scale-[0.98] transition-transform touch-manipulation"
                >
                  <X className="h-4 w-4" aria-hidden="true" />
                  清除筛选
                </Button>
              </SheetFooter>
            )}
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop Inline Sort */}
      <div className="hidden lg:flex items-center gap-3">
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Select value={selectedSort || "rating"} onValueChange={onSortChange}>
            <SelectTrigger className="w-[150px]" aria-label="选择排序方式">
              <SelectValue placeholder="排序" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="rating">评分最高</SelectItem>
              <SelectItem value="name">名称 A-Z</SelectItem>
              <SelectItem value="newest">最新添加</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Mobile Quick Sort */}
      <div className="lg:hidden flex-1">
        <Select value={selectedSort || "rating"} onValueChange={onSortChange}>
          <SelectTrigger className="min-h-[44px]" aria-label="快速排序">
            <ArrowUpDown className="h-4 w-4 mr-2 shrink-0" aria-hidden="true" />
            <SelectValue placeholder="排序" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="rating">评分最高</SelectItem>
            <SelectItem value="name">名称 A-Z</SelectItem>
            <SelectItem value="newest">最新添加</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
