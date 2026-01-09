"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { searchTools } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  const { data: results, isLoading } = useQuery({
    queryKey: ["search", query],
    queryFn: () => searchTools(query),
    enabled: query.length >= 2,
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query) {
      router.push(`/tools?search=${encodeURIComponent(query)}`);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative group flex-1 max-w-md" ref={searchRef}>
      <form onSubmit={handleSearch} className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="搜索 AI 工具 (例如: ChatGPT, Midjourney)..."
          className="h-10 w-full pl-10 pr-10 rounded-full bg-secondary/50 border-none focus:ring-2 focus:ring-primary transition-all outline-none text-sm placeholder:text-muted-foreground/70"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-primary animate-spin" />
        )}
      </form>

      {isOpen && query.length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-background border rounded-2xl shadow-2xl overflow-hidden glass z-[60] animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="p-2">
            {!isLoading && results?.length === 0 && (
              <p className="px-4 py-3 text-sm text-muted-foreground text-center">
                未找到相关工具
              </p>
            )}
            {results?.map((tool) => (
              <Link
                key={tool.id}
                href={`/tools/${tool.slug}`}
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-3 hover:bg-primary/5 rounded-xl transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-secondary/80 flex items-center justify-center overflow-hidden flex-shrink-0">
                  {tool.logo_url ? (
                    <img
                      src={tool.logo_url}
                      alt={tool.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-lg font-bold text-primary/40 leading-none">
                      {tool.name[0]}
                    </span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate group-hover:text-primary transition-colors">
                    {tool.name_zh || tool.name}
                  </div>
                  <div className="text-xs text-muted-foreground truncate leading-relaxed">
                    {tool.description_zh || tool.description}
                  </div>
                </div>
              </Link>
            ))}
            {results && results.length > 0 && (
              <div className="p-2 border-t mt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs text-primary hover:bg-primary/10"
                  onClick={handleSearch}
                >
                  查看全部 "{query}" 的结果
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

import { Button } from "@/components/ui/button";
