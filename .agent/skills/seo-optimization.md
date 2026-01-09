---
name: seo-optimization
description: SEO optimization skill for the platform
triggers:
  - "seo"
  - "search engine"
  - "ranking"
  - "meta tags"
---

# SEO Optimization Skill

搜索引擎优化技能配置。

## Target Search Engines
- **Primary:** 百度 (Baidu)
- **Secondary:** Google
- **Social:** 微信搜一搜, 头条搜索

## Technical SEO

### Meta Tags Configuration
```typescript
// app/layout.tsx
import { Metadata } from "next"

export const metadata: Metadata = {
  metadataBase: new URL("https://ainav.com"),
  title: {
    template: "%s - AI导航",
    default: "AI导航 - 发现最好用的AI工具",
  },
  description: "AI导航是最全面的AI工具导航网站，收录了数千款AI工具，帮助你发现和使用最适合的AI工具。",
  keywords: ["AI工具", "人工智能", "AI导航", "ChatGPT", "AI应用"],
  authors: [{ name: "AI导航" }],
  creator: "AI导航",
  publisher: "AI导航",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: "https://ainav.com",
    siteName: "AI导航",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AI导航 - 发现最好用的AI工具",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@ainav",
  },
  verification: {
    google: "google-site-verification-code",
    // 百度验证
    other: {
      "baidu-site-verification": "baidu-verification-code",
    },
  },
}
```

### Dynamic Meta Tags
```typescript
// app/tools/[slug]/page.tsx
import { Metadata } from "next"

export async function generateMetadata({ params }): Promise<Metadata> {
  const tool = await getTool(params.slug)

  return {
    title: `${tool.nameZh} - ${tool.name}`,
    description: tool.description?.slice(0, 160),
    keywords: [
      tool.name,
      tool.nameZh,
      ...tool.tags,
      "AI工具",
      tool.category.nameZh,
    ],
    openGraph: {
      title: tool.nameZh,
      description: tool.tagline,
      images: [
        {
          url: tool.screenshotUrl || "/og-default.png",
          width: 1200,
          height: 630,
        },
      ],
      type: "article",
    },
    alternates: {
      canonical: `https://ainav.com/tools/${params.slug}`,
    },
  }
}
```

### Structured Data (JSON-LD)
```typescript
// components/ToolJsonLd.tsx
export function ToolJsonLd({ tool }: { tool: Tool }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: tool.name,
    alternateName: tool.nameZh,
    description: tool.description,
    url: tool.url,
    image: tool.screenshotUrl,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    offers: {
      "@type": "Offer",
      price: tool.pricing === "free" ? "0" : undefined,
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
    },
    aggregateRating: tool.averageRating > 0 ? {
      "@type": "AggregateRating",
      ratingValue: tool.averageRating,
      ratingCount: tool.ratingCount,
      bestRating: 5,
      worstRating: 1,
    } : undefined,
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}

// BreadcrumbList
export function BreadcrumbJsonLd({ items }: { items: BreadcrumbItem[] }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}
```

### Sitemap Generation
```typescript
// app/sitemap.ts
import { MetadataRoute } from "next"

export default async function sitemap(): MetadataRoute.Sitemap {
  const tools = await getAllToolSlugs()
  const categories = await getAllCategories()

  const toolUrls = tools.map((slug) => ({
    url: `https://ainav.com/tools/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }))

  const categoryUrls = categories.map((cat) => ({
    url: `https://ainav.com/categories/${cat.slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }))

  return [
    {
      url: "https://ainav.com",
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: "https://ainav.com/tools",
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    ...toolUrls,
    ...categoryUrls,
  ]
}
```

### Robots.txt
```typescript
// app/robots.ts
import { MetadataRoute } from "next"

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/api/", "/admin/", "/_next/"],
      },
      {
        userAgent: "Baiduspider",
        allow: "/",
        crawlDelay: 1,
      },
    ],
    sitemap: "https://ainav.com/sitemap.xml",
    host: "https://ainav.com",
  }
}
```

## Content SEO

### URL Structure
```
✓ Good:
/tools/chatgpt
/categories/ai-writing
/learn/prompt-engineering

✗ Bad:
/tools?id=123
/tool/ChatGPT-4
/c/1234
```

### Heading Structure
```html
<h1>AI写作工具推荐</h1>
  <h2>什么是AI写作工具</h2>
    <p>...</p>
  <h2>热门AI写作工具</h2>
    <h3>ChatGPT</h3>
    <h3>Claude</h3>
    <h3>文心一言</h3>
  <h2>如何选择AI写作工具</h2>
```

### Internal Linking
```typescript
// 在工具页面添加相关推荐
export function RelatedTools({ tool }: { tool: Tool }) {
  const related = useRelatedTools(tool.id)

  return (
    <section>
      <h2>相关工具推荐</h2>
      <div className="grid grid-cols-3 gap-4">
        {related.map((r) => (
          <Link key={r.id} href={`/tools/${r.slug}`}>
            <ToolCard tool={r} />
          </Link>
        ))}
      </div>
    </section>
  )
}
```

## Performance SEO

### Core Web Vitals Targets
| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |
| TTFB | < 800ms | Time to First Byte |

### Image Optimization
```typescript
import Image from "next/image"

// Optimized images with Next.js Image
<Image
  src={tool.screenshotUrl}
  alt={`${tool.nameZh}截图`}
  width={600}
  height={400}
  placeholder="blur"
  blurDataURL={tool.blurDataUrl}
  priority={index < 3} // Priority for above-fold images
/>
```

### SSG/ISR Configuration
```typescript
// Static generation with revalidation
export const revalidate = 3600 // Revalidate every hour

// Or on-demand revalidation
export async function generateStaticParams() {
  const tools = await getAllToolSlugs()
  return tools.map((slug) => ({ slug }))
}
```

## Monitoring

### Google Search Console Integration
```bash
# Submit sitemap
curl -X POST "https://www.google.com/ping?sitemap=https://ainav.com/sitemap.xml"
```

### 百度资源平台
```bash
# 主动推送
curl -H 'Content-Type:text/plain' --data-binary @urls.txt \
  "http://data.zz.baidu.com/urls?site=https://ainav.com&token=xxx"
```

### SEO Metrics Dashboard
```typescript
// Track key metrics
const seoMetrics = {
  indexed_pages: 1234,
  organic_traffic: 5678,
  avg_position: 12.3,
  click_through_rate: 0.034,
  core_web_vitals: {
    lcp: 2.1,
    fid: 45,
    cls: 0.05,
  },
}
```
