# AI Navigator Platform - Frontend Architecture

> Version: 1.0.0
> Created: 2026-01-09
> Framework: Next.js 14+ (App Router)

---

## 1. Project Structure

```
ainav-web/
├── app/                              # Next.js App Router
│   ├── (marketing)/                  # Marketing pages (public)
│   │   ├── page.tsx                  # Homepage
│   │   ├── about/page.tsx
│   │   ├── pricing/page.tsx
│   │   └── layout.tsx
│   │
│   ├── (tools)/                      # Tool discovery section
│   │   ├── tools/
│   │   │   ├── page.tsx              # Tool listing
│   │   │   ├── [slug]/page.tsx       # Tool detail
│   │   │   └── compare/page.tsx      # Tool comparison
│   │   ├── categories/
│   │   │   ├── page.tsx              # All categories
│   │   │   └── [slug]/page.tsx       # Category page
│   │   ├── scenarios/
│   │   │   ├── page.tsx              # All scenarios
│   │   │   └── [slug]/page.tsx       # Scenario page
│   │   └── layout.tsx
│   │
│   ├── (learning)/                   # Learning hub section
│   │   ├── roadmaps/
│   │   │   ├── page.tsx              # All roadmaps
│   │   │   └── [slug]/page.tsx       # Roadmap detail
│   │   ├── prompts/
│   │   │   ├── page.tsx              # Prompt library
│   │   │   └── [id]/page.tsx         # Prompt detail
│   │   ├── papers/
│   │   │   ├── page.tsx              # ArXiv papers
│   │   │   └── [arxiv_id]/page.tsx   # Paper detail
│   │   └── layout.tsx
│   │
│   ├── (user)/                       # User-authenticated section
│   │   ├── collections/
│   │   │   ├── page.tsx              # My collections
│   │   │   └── [id]/page.tsx         # Collection detail
│   │   ├── history/page.tsx          # Browsing history
│   │   ├── settings/page.tsx         # User settings
│   │   └── layout.tsx
│   │
│   ├── (auth)/                       # Authentication pages
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── callback/
│   │       ├── wechat/page.tsx
│   │       └── github/page.tsx
│   │
│   ├── api/                          # API Routes (BFF)
│   │   ├── search/route.ts
│   │   ├── auth/[...nextauth]/route.ts
│   │   └── webhooks/route.ts
│   │
│   ├── layout.tsx                    # Root layout
│   ├── globals.css                   # Global styles
│   ├── loading.tsx                   # Global loading UI
│   ├── error.tsx                     # Global error UI
│   └── not-found.tsx                 # 404 page
│
├── components/                       # Reusable components
│   ├── ui/                           # shadcn/ui base components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── badge.tsx
│   │   ├── skeleton.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   │
│   ├── layout/                       # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MobileNav.tsx
│   │   └── ThemeToggle.tsx
│   │
│   ├── search/                       # Search components
│   │   ├── SearchBar.tsx
│   │   ├── SearchResults.tsx
│   │   ├── SearchFilters.tsx
│   │   ├── Autocomplete.tsx
│   │   └── ScenarioChips.tsx
│   │
│   ├── tools/                        # Tool components
│   │   ├── ToolCard.tsx
│   │   ├── ToolGrid.tsx
│   │   ├── ToolDetail.tsx
│   │   ├── ToolCompare.tsx
│   │   ├── ToolRating.tsx
│   │   ├── PricingBadge.tsx
│   │   ├── AccessBadge.tsx
│   │   └── RelatedTools.tsx
│   │
│   ├── learning/                     # Learning components
│   │   ├── RoadmapViewer.tsx
│   │   ├── RoadmapNode.tsx
│   │   ├── PromptCard.tsx
│   │   ├── PromptCopyButton.tsx
│   │   ├── PaperCard.tsx
│   │   └── TutorialEmbed.tsx
│   │
│   ├── user/                         # User components
│   │   ├── UserAvatar.tsx
│   │   ├── CollectionCard.tsx
│   │   ├── RatingForm.tsx
│   │   └── PreferencesForm.tsx
│   │
│   └── shared/                       # Shared components
│       ├── Logo.tsx
│       ├── CategoryIcon.tsx
│       ├── LoadingSpinner.tsx
│       ├── EmptyState.tsx
│       ├── Pagination.tsx
│       ├── SEOHead.tsx
│       └── Analytics.tsx
│
├── lib/                              # Library code
│   ├── api/                          # API client
│   │   ├── client.ts                 # Base API client
│   │   ├── tools.ts                  # Tools API
│   │   ├── search.ts                 # Search API
│   │   ├── learning.ts               # Learning API
│   │   └── user.ts                   # User API
│   │
│   ├── hooks/                        # Custom React hooks
│   │   ├── useSearch.ts
│   │   ├── useTools.ts
│   │   ├── useAuth.ts
│   │   ├── useCollection.ts
│   │   ├── useDebounce.ts
│   │   └── useMediaQuery.ts
│   │
│   ├── utils/                        # Utility functions
│   │   ├── cn.ts                     # Class name helper
│   │   ├── format.ts                 # Formatting helpers
│   │   ├── storage.ts                # Local storage helpers
│   │   └── analytics.ts              # Analytics helpers
│   │
│   ├── stores/                       # Zustand stores
│   │   ├── searchStore.ts
│   │   ├── userStore.ts
│   │   └── uiStore.ts
│   │
│   └── constants/                    # Constants
│       ├── routes.ts
│       ├── categories.ts
│       └── config.ts
│
├── public/                           # Static assets
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── styles/                           # Additional styles
│   └── themes.css
│
├── types/                            # TypeScript types
│   ├── tool.ts
│   ├── category.ts
│   ├── user.ts
│   └── api.ts
│
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 2. Core Components

### 2.1 SearchBar Component

```tsx
// components/search/SearchBar.tsx

'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, Loader2 } from 'lucide-react';
import { useDebounce } from '@/lib/hooks/useDebounce';
import { searchApi } from '@/lib/api/search';
import { Autocomplete } from './Autocomplete';
import { cn } from '@/lib/utils/cn';

interface SearchBarProps {
  variant?: 'hero' | 'header';
  placeholder?: string;
  autoFocus?: boolean;
  onSearch?: (query: string) => void;
}

export function SearchBar({
  variant = 'hero',
  placeholder = '搜索AI工具、场景或提示词...',
  autoFocus = false,
  onSearch,
}: SearchBarProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);

  const debouncedQuery = useDebounce(query, 200);

  // Fetch suggestions when query changes
  useEffect(() => {
    if (debouncedQuery.length < 1) {
      setSuggestions([]);
      return;
    }

    setIsLoading(true);
    searchApi.suggest(debouncedQuery)
      .then((data) => setSuggestions(data.suggestions))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [debouncedQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsOpen(false);
    if (onSearch) {
      onSearch(query);
    } else {
      router.push(`/tools?q=${encodeURIComponent(query)}`);
    }
  };

  const handleSuggestionSelect = (suggestion: SearchSuggestion) => {
    setIsOpen(false);
    if (suggestion.type === 'tool') {
      router.push(`/tools/${suggestion.slug}`);
    } else if (suggestion.type === 'scenario') {
      router.push(`/scenarios/${suggestion.slug}`);
    } else {
      setQuery(suggestion.text);
      router.push(`/tools?q=${encodeURIComponent(suggestion.text)}`);
    }
  };

  const isHero = variant === 'hero';

  return (
    <div className={cn('relative w-full', isHero && 'max-w-2xl mx-auto')}>
      <form onSubmit={handleSubmit}>
        <div
          className={cn(
            'relative flex items-center rounded-full border bg-background',
            'transition-shadow duration-200',
            isOpen && 'ring-2 ring-primary/20',
            isHero
              ? 'h-14 px-6 text-lg shadow-lg hover:shadow-xl'
              : 'h-10 px-4 text-sm'
          )}
        >
          <Search
            className={cn(
              'flex-shrink-0 text-muted-foreground',
              isHero ? 'h-5 w-5' : 'h-4 w-4'
            )}
          />

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className={cn(
              'flex-1 bg-transparent outline-none placeholder:text-muted-foreground',
              isHero ? 'mx-4' : 'mx-3'
            )}
          />

          {isLoading && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          )}

          {query && !isLoading && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </form>

      {/* Autocomplete dropdown */}
      {isOpen && suggestions.length > 0 && (
        <Autocomplete
          suggestions={suggestions}
          onSelect={handleSuggestionSelect}
          onClose={() => setIsOpen(false)}
          highlightQuery={query}
        />
      )}
    </div>
  );
}
```

### 2.2 ToolCard Component

```tsx
// components/tools/ToolCard.tsx

import Link from 'next/link';
import Image from 'next/image';
import { ExternalLink, Star, Globe, Lock, Code, Zap } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PricingBadge } from './PricingBadge';
import { AccessBadge } from './AccessBadge';
import { cn } from '@/lib/utils/cn';
import type { Tool } from '@/types/tool';

interface ToolCardProps {
  tool: Tool;
  showDescription?: boolean;
  className?: string;
}

export function ToolCard({
  tool,
  showDescription = false,
  className,
}: ToolCardProps) {
  const displayName = tool.name_cn || tool.name;
  const displayTagline = tool.tagline_cn || tool.tagline;

  return (
    <Link href={`/tools/${tool.slug}`}>
      <Card
        className={cn(
          'group h-full transition-all duration-200',
          'hover:shadow-md hover:border-primary/20',
          'cursor-pointer',
          className
        )}
      >
        <CardContent className="p-4">
          {/* Header: Logo + Name */}
          <div className="flex items-start gap-3">
            {/* Tool Logo */}
            <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg border bg-muted">
              {tool.logo_url ? (
                <Image
                  src={tool.logo_url}
                  alt={displayName}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-lg font-bold text-muted-foreground">
                  {displayName.charAt(0)}
                </div>
              )}
            </div>

            {/* Name + Tagline */}
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1">
                {displayName}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">
                {displayTagline}
              </p>
            </div>
          </div>

          {/* Description (optional) */}
          {showDescription && tool.description_cn && (
            <p className="mt-3 text-sm text-muted-foreground line-clamp-3">
              {tool.description_cn}
            </p>
          )}

          {/* Badges Row */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            <PricingBadge type={tool.pricing_type} />
            <AccessBadge
              isAccessible={tool.is_china_accessible}
              requiresVpn={tool.requires_vpn}
            />
            {tool.has_api && (
              <Badge variant="outline" className="text-xs">
                <Code className="h-3 w-3 mr-1" />
                API
              </Badge>
            )}
            {tool.is_open_source && (
              <Badge variant="outline" className="text-xs">
                开源
              </Badge>
            )}
          </div>

          {/* Footer: Rating + Category */}
          <div className="mt-3 flex items-center justify-between text-sm">
            {/* Rating */}
            {tool.rating_count > 0 && (
              <div className="flex items-center gap-1 text-muted-foreground">
                <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
                <span>{tool.rating_avg.toFixed(1)}</span>
                <span className="text-xs">({tool.rating_count})</span>
              </div>
            )}

            {/* Category */}
            {tool.category && (
              <span className="text-xs text-muted-foreground">
                {tool.category.name_cn}
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

### 2.3 PricingBadge Component

```tsx
// components/tools/PricingBadge.tsx

import { Badge } from '@/components/ui/badge';
import { Gift, Coins, CreditCard, FlaskConical, Github } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

type PricingType = 'free' | 'freemium' | 'paid' | 'beta_free' | 'open_source';

const pricingConfig: Record<
  PricingType,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    className: string;
  }
> = {
  free: {
    label: '完全免费',
    icon: Gift,
    className: 'bg-green-100 text-green-700 hover:bg-green-100 dark:bg-green-900/30 dark:text-green-400',
  },
  freemium: {
    label: '免费额度',
    icon: Coins,
    className: 'bg-blue-100 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400',
  },
  paid: {
    label: '付费',
    icon: CreditCard,
    className: 'bg-orange-100 text-orange-700 hover:bg-orange-100 dark:bg-orange-900/30 dark:text-orange-400',
  },
  beta_free: {
    label: '公测免费',
    icon: FlaskConical,
    className: 'bg-purple-100 text-purple-700 hover:bg-purple-100 dark:bg-purple-900/30 dark:text-purple-400',
  },
  open_source: {
    label: '开源',
    icon: Github,
    className: 'bg-gray-100 text-gray-700 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300',
  },
};

interface PricingBadgeProps {
  type: PricingType;
  showIcon?: boolean;
  className?: string;
}

export function PricingBadge({
  type,
  showIcon = true,
  className,
}: PricingBadgeProps) {
  const config = pricingConfig[type];
  const Icon = config.icon;

  return (
    <Badge
      variant="secondary"
      className={cn('text-xs font-medium', config.className, className)}
    >
      {showIcon && <Icon className="h-3 w-3 mr-1" />}
      {config.label}
    </Badge>
  );
}
```

### 2.4 AccessBadge Component

```tsx
// components/tools/AccessBadge.tsx

import { Badge } from '@/components/ui/badge';
import { Globe, Shield, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface AccessBadgeProps {
  isAccessible: boolean;
  requiresVpn: boolean;
  className?: string;
}

export function AccessBadge({
  isAccessible,
  requiresVpn,
  className,
}: AccessBadgeProps) {
  if (isAccessible && !requiresVpn) {
    return (
      <Badge
        variant="secondary"
        className={cn(
          'text-xs bg-green-100 text-green-700 hover:bg-green-100',
          'dark:bg-green-900/30 dark:text-green-400',
          className
        )}
      >
        <Globe className="h-3 w-3 mr-1" />
        国内直连
      </Badge>
    );
  }

  if (requiresVpn) {
    return (
      <Badge
        variant="secondary"
        className={cn(
          'text-xs bg-yellow-100 text-yellow-700 hover:bg-yellow-100',
          'dark:bg-yellow-900/30 dark:text-yellow-400',
          className
        )}
      >
        <Shield className="h-3 w-3 mr-1" />
        需要VPN
      </Badge>
    );
  }

  return (
    <Badge
      variant="secondary"
      className={cn(
        'text-xs bg-gray-100 text-gray-600 hover:bg-gray-100',
        'dark:bg-gray-800 dark:text-gray-400',
        className
      )}
    >
      <AlertTriangle className="h-3 w-3 mr-1" />
      访问受限
    </Badge>
  );
}
```

### 2.5 ScenarioChips Component

```tsx
// components/search/ScenarioChips.tsx

'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { scenariosApi } from '@/lib/api/scenarios';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils/cn';

interface ScenarioChipsProps {
  limit?: number;
  className?: string;
}

export function ScenarioChips({ limit = 8, className }: ScenarioChipsProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['scenarios', 'featured'],
    queryFn: () => scenariosApi.list({ featured: true, limit }),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });

  if (isLoading) {
    return (
      <div className={cn('flex flex-wrap gap-2 justify-center', className)}>
        {Array.from({ length: limit }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-24 rounded-full" />
        ))}
      </div>
    );
  }

  return (
    <div className={cn('flex flex-wrap gap-2 justify-center', className)}>
      {data?.map((scenario) => (
        <Link
          key={scenario.slug}
          href={`/scenarios/${scenario.slug}`}
          className={cn(
            'inline-flex items-center gap-1.5 px-4 py-2 rounded-full',
            'text-sm font-medium transition-all duration-200',
            'bg-secondary/50 hover:bg-secondary',
            'text-secondary-foreground hover:text-primary',
            'border border-transparent hover:border-primary/20'
          )}
        >
          <span className="text-base">{scenario.icon}</span>
          <span>{scenario.name_cn}</span>
          <span className="text-xs text-muted-foreground ml-1">
            {scenario.tool_count}
          </span>
        </Link>
      ))}
    </div>
  );
}
```

---

## 3. Page Components

### 3.1 Homepage (Hero Section)

```tsx
// app/(marketing)/page.tsx

import { SearchBar } from '@/components/search/SearchBar';
import { ScenarioChips } from '@/components/search/ScenarioChips';
import { ToolGrid } from '@/components/tools/ToolGrid';
import { toolsApi } from '@/lib/api/tools';

export const revalidate = 600; // ISR: 10 minutes

export default async function HomePage() {
  const featuredTools = await toolsApi.list({
    featured: true,
    limit: 12,
    sort: 'popularity',
  });

  return (
    <main>
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent" />

        <div className="container relative">
          {/* Headline */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              发现最好的
              <span className="text-primary"> AI 工具</span>
            </h1>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              精选 1000+ 优质 AI 工具，涵盖文本、图像、视频、代码等领域
              <br />
              免费、好用、国内直连
            </p>
          </div>

          {/* Search Bar */}
          <div className="mb-8">
            <SearchBar variant="hero" autoFocus />
          </div>

          {/* Scenario Chips */}
          <ScenarioChips limit={8} />
        </div>
      </section>

      {/* Featured Tools Section */}
      <section className="py-16">
        <div className="container">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold">编辑推荐</h2>
              <p className="text-muted-foreground">精心挑选的高质量 AI 工具</p>
            </div>
            <a
              href="/tools"
              className="text-primary hover:underline text-sm font-medium"
            >
              查看全部 →
            </a>
          </div>

          <ToolGrid tools={featuredTools.data} columns={4} />
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-muted/50">
        <div className="container">
          <h2 className="text-2xl font-bold text-center mb-8">按分类浏览</h2>
          {/* Category grid component */}
        </div>
      </section>

      {/* Learning Hub Promo */}
      <section className="py-16">
        <div className="container">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Roadmaps promo */}
            {/* Prompts library promo */}
          </div>
        </div>
      </section>
    </main>
  );
}
```

### 3.2 Tools Listing Page

```tsx
// app/(tools)/tools/page.tsx

import { Suspense } from 'react';
import { SearchBar } from '@/components/search/SearchBar';
import { SearchFilters } from '@/components/search/SearchFilters';
import { ToolGrid } from '@/components/tools/ToolGrid';
import { Pagination } from '@/components/shared/Pagination';
import { toolsApi } from '@/lib/api/tools';
import { Skeleton } from '@/components/ui/skeleton';

interface ToolsPageProps {
  searchParams: {
    q?: string;
    category?: string;
    pricing?: string;
    china_accessible?: string;
    sort?: string;
    page?: string;
  };
}

export default async function ToolsPage({ searchParams }: ToolsPageProps) {
  const page = parseInt(searchParams.page || '1');
  const perPage = 24;

  const tools = await toolsApi.list({
    q: searchParams.q,
    category: searchParams.category,
    pricing: searchParams.pricing as any,
    china_accessible: searchParams.china_accessible === 'true',
    sort: (searchParams.sort as any) || 'popularity',
    page,
    per_page: perPage,
  });

  return (
    <div className="container py-8">
      {/* Search header */}
      <div className="mb-8">
        <SearchBar variant="header" />
      </div>

      <div className="flex gap-8">
        {/* Sidebar filters */}
        <aside className="w-64 flex-shrink-0 hidden lg:block">
          <SearchFilters currentFilters={searchParams} />
        </aside>

        {/* Main content */}
        <main className="flex-1">
          {/* Results header */}
          <div className="flex items-center justify-between mb-6">
            <p className="text-muted-foreground">
              {searchParams.q ? (
                <>
                  搜索 &quot;{searchParams.q}&quot; 的结果：
                  <span className="font-medium text-foreground ml-1">
                    {tools.meta.total} 个工具
                  </span>
                </>
              ) : (
                <>共 {tools.meta.total} 个工具</>
              )}
            </p>

            {/* Sort dropdown */}
            {/* ... */}
          </div>

          {/* Tool grid */}
          <Suspense
            fallback={
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.from({ length: 12 }).map((_, i) => (
                  <Skeleton key={i} className="h-48 rounded-lg" />
                ))}
              </div>
            }
          >
            <ToolGrid tools={tools.data} columns={3} showDescription />
          </Suspense>

          {/* Pagination */}
          {tools.meta.has_more && (
            <div className="mt-8">
              <Pagination
                currentPage={page}
                totalPages={Math.ceil(tools.meta.total / perPage)}
                baseUrl="/tools"
                searchParams={searchParams}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
```

---

## 4. State Management

### 4.1 Zustand Store - Search

```tsx
// lib/stores/searchStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SearchState {
  recentSearches: string[];
  addRecentSearch: (query: string) => void;
  clearRecentSearches: () => void;
}

export const useSearchStore = create<SearchState>()(
  persist(
    (set) => ({
      recentSearches: [],

      addRecentSearch: (query) =>
        set((state) => ({
          recentSearches: [
            query,
            ...state.recentSearches.filter((q) => q !== query),
          ].slice(0, 10),
        })),

      clearRecentSearches: () => set({ recentSearches: [] }),
    }),
    {
      name: 'ainav-search',
    }
  )
);
```

### 4.2 TanStack Query - API Hooks

```tsx
// lib/hooks/useTools.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toolsApi } from '@/lib/api/tools';

export function useTool(slug: string) {
  return useQuery({
    queryKey: ['tool', slug],
    queryFn: () => toolsApi.getBySlug(slug),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useToolsList(params: ToolsListParams) {
  return useQuery({
    queryKey: ['tools', params],
    queryFn: () => toolsApi.list(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useTrackToolClick() {
  return useMutation({
    mutationFn: ({
      slug,
      sessionId,
      referrer,
    }: {
      slug: string;
      sessionId: string;
      referrer?: string;
    }) => toolsApi.trackClick(slug, { session_id: sessionId, referrer }),
  });
}
```

---

## 5. Styling System

### 5.1 Tailwind Configuration

```ts
// tailwind.config.ts

import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '1rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-up': {
          from: { transform: 'translateY(10px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
```

### 5.2 CSS Variables (Light/Dark)

```css
/* app/globals.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

/* Custom scrollbar */
@layer utilities {
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: hsl(var(--muted-foreground)) transparent;
  }

  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    background-color: hsl(var(--muted-foreground) / 0.3);
    border-radius: 3px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background-color: hsl(var(--muted-foreground) / 0.5);
  }
}
```

---

## 6. Performance Optimizations

### 6.1 Image Optimization

```tsx
// next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.ainav.cn',
      },
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};
```

### 6.2 Route Prefetching

```tsx
// components/tools/ToolCard.tsx

import Link from 'next/link';

// Next.js automatically prefetches links in viewport
// Use prefetch={false} for less important links
<Link href={`/tools/${tool.slug}`} prefetch={true}>
  ...
</Link>
```

### 6.3 Dynamic Imports

```tsx
// Lazy load heavy components
import dynamic from 'next/dynamic';

const RoadmapViewer = dynamic(
  () => import('@/components/learning/RoadmapViewer'),
  {
    loading: () => <Skeleton className="h-96 w-full" />,
    ssr: false, // SVG interaction needs client-side
  }
);

const ToolCompare = dynamic(
  () => import('@/components/tools/ToolCompare'),
  {
    loading: () => <Skeleton className="h-64 w-full" />,
  }
);
```

---

## 7. SEO Configuration

### 7.1 Metadata Generation

```tsx
// app/(tools)/tools/[slug]/page.tsx

import { Metadata } from 'next';
import { toolsApi } from '@/lib/api/tools';

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const tool = await toolsApi.getBySlug(params.slug);

  if (!tool) {
    return {
      title: '工具未找到 | AI导航',
    };
  }

  const title = `${tool.name_cn || tool.name} - ${tool.tagline_cn || tool.tagline}`;
  const description = tool.description_cn || tool.description;

  return {
    title: `${title} | AI导航`,
    description: description?.slice(0, 160),
    openGraph: {
      title,
      description: description?.slice(0, 160),
      images: tool.screenshot_url ? [tool.screenshot_url] : [],
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description: description?.slice(0, 160),
      images: tool.screenshot_url ? [tool.screenshot_url] : [],
    },
    alternates: {
      canonical: `https://ainav.cn/tools/${params.slug}`,
    },
  };
}
```

### 7.2 Structured Data

```tsx
// components/tools/ToolDetail.tsx

function ToolStructuredData({ tool }: { tool: Tool }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: tool.name,
    description: tool.description,
    url: tool.website_url,
    image: tool.logo_url,
    applicationCategory: 'AI Tool',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: tool.pricing_type === 'free' ? '0' : undefined,
      priceCurrency: 'USD',
    },
    aggregateRating: tool.rating_count > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: tool.rating_avg,
      ratingCount: tool.rating_count,
    } : undefined,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
```

---

## 8. Mobile Responsiveness

### 8.1 Responsive Breakpoints

```tsx
// lib/hooks/useMediaQuery.ts

import { useState, useEffect } from 'react';

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

// Usage
const isMobile = useMediaQuery('(max-width: 768px)');
const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
```

### 8.2 Mobile Navigation

```tsx
// components/layout/MobileNav.tsx

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Search, User, Heart } from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';

export function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[300px]">
        <nav className="flex flex-col gap-4 mt-8">
          <Link
            href="/tools"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-muted"
          >
            <Search className="h-5 w-5" />
            发现工具
          </Link>
          <Link
            href="/roadmaps"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-muted"
          >
            学习路线
          </Link>
          <Link
            href="/prompts"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-muted"
          >
            提示词库
          </Link>
          <hr />
          <Link
            href="/collections"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-muted"
          >
            <Heart className="h-5 w-5" />
            我的收藏
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  );
}
```

---

*This frontend architecture provides a scalable foundation for building the AI Navigator platform with excellent performance, SEO, and user experience.*
