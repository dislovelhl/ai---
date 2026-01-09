"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutGrid,
  Sparkles,
  Code,
  Palette,
  BarChart3,
  Zap,
  ArrowRight,
  Bot,
  Terminal,
  Pencil,
  Image as ImageIcon,
  Video,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { getCategories, getScenarios } from "@/lib/api";

// Helper to map slugs/names to icons
const getIconForCategory = (slug: string) => {
  const icons: Record<string, any> = {
    coding: Code,
    design: Palette,
    writing: Pencil,
    image: ImageIcon,
    video: Video,
    productivity: Zap,
    analysis: BarChart3,
    "ai-tools": Sparkles,
  };
  return icons[slug] || Terminal;
};

export function Sidebar() {
  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => getCategories(),
  });

  const { data: scenarios = [] } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => getScenarios(),
  });

  return (
    <aside className="w-64 flex-col hidden md:flex border-r h-[calc(100vh-4rem)] sticky top-16 bg-background/50 backdrop-blur-sm">
      <div className="flex-1 overflow-y-auto py-6 px-4">
        <div className="mb-8">
          <h3 className="px-4 mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            分类浏览
          </h3>
          <nav className="space-y-1">
            <Link
              href="/tools"
              className="flex items-center gap-3 px-4 py-2 text-sm font-medium rounded-lg hover:bg-primary/10 hover:text-primary transition-all group"
            >
              <LayoutGrid className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              全部工具
            </Link>
            {categories.map((item) => {
              const Icon = getIconForCategory(item.slug);
              return (
                <Link
                  key={item.id}
                  href={`/tools?category=${item.slug}`}
                  className="flex items-center gap-3 px-4 py-2 text-sm font-medium rounded-lg hover:bg-primary/10 hover:text-primary transition-all group"
                >
                  <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="mb-8">
          <h3 className="px-4 mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            应用场景
          </h3>
          <nav className="space-y-1">
            {scenarios.map((item) => (
              <Link
                key={item.id}
                href={`/scenarios/${item.slug}`}
                className="flex items-center justify-between px-4 py-2 text-sm font-medium rounded-lg hover:bg-primary/10 hover:text-primary transition-all group"
              >
                <span>{item.name}</span>
                <ArrowRight className="h-3 w-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </Link>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-4 rounded-2xl bg-gradient-to-br from-primary/20 to-blue-500/10 border border-primary/20">
          <div className="flex items-center gap-2 mb-2">
            <Bot className="h-5 w-5 text-primary" />
            <span className="font-bold text-sm">AI 助手</span>
          </div>
          <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
            找不到合适的工具？让我们的 AI 顾问帮你出谋划策。
          </p>
          <Button size="sm" className="w-full rounded-xl text-xs h-8">
            立即咨询
          </Button>
        </div>
      </div>
    </aside>
  );
}
