"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Search, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { searchTools } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = "search-results-listbox";

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

  // Keyboard navigation for search results
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!results?.length) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setFocusedIndex((prev) =>
            prev < results.length - 1 ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setFocusedIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;
        case "Enter":
          if (focusedIndex >= 0 && results[focusedIndex]) {
            e.preventDefault();
            router.push(`/tools/${results[focusedIndex].slug}`);
            setIsOpen(false);
            setFocusedIndex(-1);
          }
          break;
        case "Escape":
          setIsOpen(false);
          setFocusedIndex(-1);
          inputRef.current?.blur();
          break;
      }
    },
    [results, focusedIndex, router]
  );

  // Reset focused index when results change
  useEffect(() => {
    setFocusedIndex(-1);
  }, [results]);

  const isExpanded = isOpen && query.length >= 2;

  return (
    <div className="relative group flex-1 max-w-md" ref={searchRef} role="search">
      <form onSubmit={handleSearch} className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" aria-hidden="true" />
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-label="搜索 AI 工具"
          aria-expanded={isExpanded}
          aria-controls={listboxId}
          aria-autocomplete="list"
          aria-activedescendant={
            focusedIndex >= 0 ? `search-result-${focusedIndex}` : undefined
          }
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="搜索 AI 工具 (例如: ChatGPT, Midjourney)..."
          className="h-10 w-full pl-10 pr-10 rounded-full bg-secondary/50 border-none focus:ring-2 focus:ring-primary focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 transition-all outline-none text-sm placeholder:text-muted-foreground/70"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-primary animate-spin" aria-hidden="true" />
        )}
        {isLoading && (
          <span className="sr-only" role="status" aria-live="polite">
            正在搜索...
          </span>
        )}
      </form>

      {isExpanded && (
        <div
          id={listboxId}
          role="listbox"
          aria-label="搜索结果"
          className="absolute top-full left-0 right-0 mt-2 bg-background border rounded-2xl shadow-2xl overflow-hidden glass z-[60] animate-in fade-in slide-in-from-top-2 duration-200"
        >
          <div className="p-2">
            {!isLoading && results?.length === 0 && (
              <p className="px-4 py-3 text-sm text-muted-foreground text-center" role="status">
                未找到相关工具
              </p>
            )}
            {results?.map((tool, index) => (
              <Link
                key={tool.id}
                id={`search-result-${index}`}
                role="option"
                aria-selected={focusedIndex === index}
                href={`/tools/${tool.slug}`}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 hover:bg-primary/5 rounded-xl transition-colors group ${
                  focusedIndex === index ? "bg-primary/10 ring-2 ring-primary" : ""
                }`}
              >
                <div className="w-10 h-10 rounded-lg bg-secondary/80 flex items-center justify-center overflow-hidden flex-shrink-0">
                  {tool.logo_url ? (
                    <img
                      src={tool.logo_url}
                      alt={`${tool.name} 图标`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-lg font-bold text-primary/40 leading-none" aria-hidden="true">
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
