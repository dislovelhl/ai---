"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function SearchHero() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) {
      router.push(`/tools?q=${encodeURIComponent(query)}`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="relative max-w-2xl mx-auto w-full group px-2 sm:px-0" role="search">
      <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-secondary/20 to-primary/20 blur-xl opacity-20 group-hover:opacity-30 transition-opacity" aria-hidden="true" />
      <div className="relative flex flex-col sm:flex-row items-stretch sm:items-center bg-background/50 backdrop-blur-xl border border-border shadow-2xl rounded-2xl sm:rounded-full p-2 sm:p-2 ring-1 ring-white/10 focus-within:ring-primary/50 transition-all duration-300 gap-2 sm:gap-0">
        <div className="flex items-center flex-1 min-h-[44px]">
          <Search className="ml-3 sm:ml-4 h-5 w-5 sm:h-6 sm:w-6 text-muted-foreground shrink-0" aria-hidden="true" />
          <Input
            className="flex-1 border-none shadow-none focus-visible:ring-0 text-base sm:text-lg h-11 sm:h-12 bg-transparent placeholder:text-muted-foreground/50"
            placeholder="搜索 AI 工具，例如：写作助手、Ppt生成..."
            aria-label="搜索 AI 工具"
            inputMode="search"
            enterKeyHint="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <Button
          size="lg"
          className="rounded-full px-6 sm:px-8 shadow-lg bg-primary/90 hover:bg-primary active:scale-[0.98] transition-all min-h-[44px] h-11 sm:h-auto"
          onClick={handleSearch}
          aria-label="搜索"
        >
          <span className="sm:inline">搜索</span>
        </Button>
      </div>
    </div>
  );
}
