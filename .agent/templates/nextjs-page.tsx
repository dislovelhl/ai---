/**
 * Next.js Page Template (App Router)
 * Usage: /gen page <path>
 */

import { Metadata } from "next"
import { notFound } from "next/navigation"
import { Suspense } from "react"

import { __COMPONENT_NAME__ } from "@/components/__PATH__/__COMPONENT_NAME__"
import { __COMPONENT_NAME__Skeleton } from "@/components/__PATH__/__COMPONENT_NAME__Skeleton"
import { BreadcrumbJsonLd, PageJsonLd } from "@/components/seo/JsonLd"

// =============================================================================
// Types
// =============================================================================

interface PageProps {
  params: { slug: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

// =============================================================================
// Data Fetching
// =============================================================================

async function getData(slug: string) {
  // Fetch data from API
  const res = await fetch(`${process.env.API_URL}/api/v1/__PATH__/${slug}`, {
    next: { revalidate: 3600 }, // Cache for 1 hour
  })

  if (!res.ok) {
    if (res.status === 404) return null
    throw new Error("Failed to fetch data")
  }

  return res.json()
}

// =============================================================================
// Metadata
// =============================================================================

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const data = await getData(params.slug)

  if (!data) {
    return {
      title: "未找到 - AI导航",
    }
  }

  return {
    title: `${data.nameZh || data.name} - AI导航`,
    description: data.description?.slice(0, 160),
    keywords: [data.name, data.nameZh, ...data.tags, "AI工具"].filter(Boolean),
    openGraph: {
      title: data.nameZh || data.name,
      description: data.tagline || data.description?.slice(0, 160),
      images: data.screenshotUrl
        ? [{ url: data.screenshotUrl, width: 1200, height: 630 }]
        : undefined,
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
    },
    alternates: {
      canonical: `https://ainav.com/__PATH__/${params.slug}`,
    },
  }
}

// =============================================================================
// Static Params (for SSG)
// =============================================================================

export async function generateStaticParams() {
  const res = await fetch(`${process.env.API_URL}/api/v1/__PATH__/slugs`)
  const slugs = await res.json()

  return slugs.map((slug: string) => ({ slug }))
}

// =============================================================================
// Page Component
// =============================================================================

export default async function __PAGE_NAME__Page({ params, searchParams }: PageProps) {
  const data = await getData(params.slug)

  if (!data) {
    notFound()
  }

  const breadcrumbs = [
    { name: "首页", url: "https://ainav.com" },
    { name: "__CATEGORY__", url: "https://ainav.com/__PATH__" },
    { name: data.nameZh || data.name, url: `https://ainav.com/__PATH__/${params.slug}` },
  ]

  return (
    <>
      {/* Structured Data */}
      <BreadcrumbJsonLd items={breadcrumbs} />
      <PageJsonLd data={data} />

      {/* Page Content */}
      <main className="container py-8">
        {/* Breadcrumb */}
        <nav className="mb-6">
          <ol className="flex items-center space-x-2 text-sm text-muted-foreground">
            {breadcrumbs.map((item, index) => (
              <li key={item.url} className="flex items-center">
                {index > 0 && <span className="mx-2">/</span>}
                {index === breadcrumbs.length - 1 ? (
                  <span className="text-foreground">{item.name}</span>
                ) : (
                  <a href={item.url} className="hover:text-foreground">
                    {item.name}
                  </a>
                )}
              </li>
            ))}
          </ol>
        </nav>

        {/* Main Content */}
        <article>
          <header className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">
              {data.nameZh || data.name}
            </h1>
            {data.tagline && (
              <p className="mt-2 text-lg text-muted-foreground">
                {data.tagline}
              </p>
            )}
          </header>

          <Suspense fallback={<__COMPONENT_NAME__Skeleton />}>
            <__COMPONENT_NAME__ data={data} />
          </Suspense>
        </article>

        {/* Related Items */}
        <section className="mt-16">
          <h2 className="text-2xl font-bold mb-6">相关推荐</h2>
          <Suspense fallback={<div>加载中...</div>}>
            {/* Related items component */}
          </Suspense>
        </section>
      </main>
    </>
  )
}

// =============================================================================
// Loading State
// =============================================================================

export function Loading() {
  return (
    <main className="container py-8">
      <div className="animate-pulse">
        <div className="h-4 bg-muted rounded w-1/4 mb-6" />
        <div className="h-10 bg-muted rounded w-3/4 mb-4" />
        <div className="h-6 bg-muted rounded w-1/2 mb-8" />
        <__COMPONENT_NAME__Skeleton />
      </div>
    </main>
  )
}

// =============================================================================
// Error Boundary
// =============================================================================

export function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <main className="container py-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">出错了</h2>
        <p className="text-muted-foreground mb-6">
          加载页面时发生错误，请重试。
        </p>
        <button
          onClick={reset}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          重试
        </button>
      </div>
    </main>
  )
}

// =============================================================================
// Not Found
// =============================================================================

export function NotFound() {
  return (
    <main className="container py-16 text-center">
      <h2 className="text-2xl font-bold mb-4">页面不存在</h2>
      <p className="text-muted-foreground mb-6">
        您访问的页面不存在或已被删除。
      </p>
      <a
        href="/"
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md inline-block"
      >
        返回首页
      </a>
    </main>
  )
}
