---
name: frontend-dev
description: Frontend development skill for Next.js/React
triggers:
  - "frontend"
  - "react component"
  - "ui development"
---

# Frontend Development Skill

前端开发技能配置。

## Tech Stack
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS 3+
- **Components:** shadcn/ui
- **State:** Zustand + TanStack Query
- **Testing:** Jest + React Testing Library

## Project Structure
```
ainav-web/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── (home)/            # Homepage route group
│   │   ├── tools/             # Tools pages
│   │   │   ├── page.tsx       # Tools listing
│   │   │   └── [slug]/        # Tool detail
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── tools/             # Tool-related components
│   │   ├── search/            # Search components
│   │   └── layout/            # Layout components
│   ├── hooks/                 # Custom hooks
│   ├── lib/                   # Utilities
│   ├── stores/                # Zustand stores
│   └── types/                 # TypeScript types
```

## Component Template
```typescript
import { cn } from "@/lib/utils"

interface ComponentNameProps {
  className?: string
  children?: React.ReactNode
}

export function ComponentName({
  className,
  children,
}: ComponentNameProps) {
  return (
    <div className={cn("", className)}>
      {children}
    </div>
  )
}
```

## Hook Template
```typescript
import { useQuery, useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"

export function useTools(params?: ToolsParams) {
  return useQuery({
    queryKey: ["tools", params],
    queryFn: () => api.tools.list(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useCreateTool() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.tools.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tools"] })
    },
  })
}
```

## Store Template
```typescript
import { create } from "zustand"
import { persist } from "zustand/middleware"

interface SearchStore {
  query: string
  filters: SearchFilters
  setQuery: (query: string) => void
  setFilters: (filters: Partial<SearchFilters>) => void
  reset: () => void
}

export const useSearchStore = create<SearchStore>()(
  persist(
    (set) => ({
      query: "",
      filters: defaultFilters,
      setQuery: (query) => set({ query }),
      setFilters: (filters) => set((s) => ({
        filters: { ...s.filters, ...filters }
      })),
      reset: () => set({ query: "", filters: defaultFilters }),
    }),
    { name: "search-store" }
  )
)
```

## SEO Best Practices
```typescript
// app/tools/[slug]/page.tsx
import { Metadata } from "next"

type Props = { params: { slug: string } }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const tool = await getTool(params.slug)

  return {
    title: `${tool.nameZh} - AI导航`,
    description: tool.description,
    openGraph: {
      title: tool.nameZh,
      description: tool.tagline,
      images: [tool.screenshotUrl],
    },
  }
}

export async function generateStaticParams() {
  const tools = await getAllToolSlugs()
  return tools.map((slug) => ({ slug }))
}
```

## Common Patterns

### Loading State
```typescript
export function ToolsPage() {
  const { data, isLoading, error } = useTools()

  if (isLoading) return <ToolsSkeleton />
  if (error) return <ErrorMessage error={error} />
  if (!data?.items.length) return <EmptyState />

  return <ToolGrid tools={data.items} />
}
```

### Infinite Scroll
```typescript
export function ToolsInfiniteList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ["tools"],
      queryFn: ({ pageParam = 1 }) => api.tools.list({ page: pageParam }),
      getNextPageParam: (lastPage) =>
        lastPage.page < lastPage.totalPages ? lastPage.page + 1 : undefined,
    })

  const { ref } = useInView({
    onChange: (inView) => {
      if (inView && hasNextPage) fetchNextPage()
    },
  })

  return (
    <>
      {data?.pages.map((page) =>
        page.items.map((tool) => <ToolCard key={tool.id} tool={tool} />)
      )}
      <div ref={ref}>{isFetchingNextPage && <Spinner />}</div>
    </>
  )
}
```

### Form Handling
```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const schema = z.object({
  name: z.string().min(1, "名称不能为空"),
  email: z.string().email("请输入有效的邮箱"),
})

export function ContactForm() {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
  })

  const onSubmit = form.handleSubmit(async (data) => {
    // Submit logic
  })

  return (
    <Form {...form}>
      <form onSubmit={onSubmit}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>名称</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  )
}
```
