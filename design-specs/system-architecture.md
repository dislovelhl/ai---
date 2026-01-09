# AI Navigator Platform - System Architecture Design

> Version: 1.0.0
> Created: 2026-01-09
> Status: Design Phase
> Project: 中国AI生态导航与认知中枢平台

---

## 1. Executive Summary

This document provides the comprehensive technical architecture for building a next-generation Chinese AI navigation and learning platform. The platform transcends the traditional Hao123 link-aggregation model to become an intelligent capability distribution and cognitive upgrade ecosystem.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Search-First** | All interactions start from intelligent search, not hierarchical navigation |
| **Scenario-Driven** | Tool discovery through Jobs-to-be-Done, not technology categories |
| **China-Optimized** | Architecture designed for GFW constraints and local network conditions |
| **Automation-First** | Content discovery and curation powered by automated pipelines |
| **Privacy-Conscious** | Minimal data collection, PIPL-compliant from day one |

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Web App    │  │  Mobile Web  │  │  WeChat H5   │  │  Mini Program (WIP)  │ │
│  │  (Next.js)   │  │ (Responsive) │  │  (Optimized) │  │    (Future Phase)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    CDN (Cloudflare / 七牛云 / 又拍云)                      │   │
│  │  • Static Assets (JS/CSS/Images)                                          │   │
│  │  • ISR Page Cache                                                         │   │
│  │  • DDoS Protection                                                        │   │
│  │  • China PoP Optimization                                                 │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         API GATEWAY (Kong/Traefik)                          │ │
│  │  • Rate Limiting  • Auth Middleware  • Request Routing  • Metrics          │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│         ┌──────────────────────────────┼──────────────────────────────┐         │
│         ▼                              ▼                              ▼         │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐      │
│  │  Web BFF        │        │  Search Service │        │  Content API    │      │
│  │  (Next.js API)  │        │  (FastAPI)      │        │  (FastAPI)      │      │
│  │                 │        │                 │        │                 │      │
│  │ • SSR/ISR       │        │ • Meilisearch   │        │ • Tool CRUD     │      │
│  │ • Auth Session  │        │ • Vector Search │        │ • Categories    │      │
│  │ • Page Routing  │        │ • Autocomplete  │        │ • Ratings       │      │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘      │
│         │                              │                              │         │
│         │         ┌────────────────────┼────────────────────┐         │         │
│         ▼         ▼                    ▼                    ▼         ▼         │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐      │
│  │  Learning Hub   │        │  User Service   │        │  Analytics      │      │
│  │  (FastAPI)      │        │  (FastAPI)      │        │  Service        │      │
│  │                 │        │                 │        │  (FastAPI)      │      │
│  │ • Roadmaps      │        │ • Registration  │        │ • Events        │      │
│  │ • Tutorials     │        │ • Preferences   │        │ • Tracking      │      │
│  │ • Prompts       │        │ • Collections   │        │ • Reports       │      │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   PostgreSQL    │  │     Redis       │  │   Meilisearch   │                  │
│  │                 │  │                 │  │                 │                  │
│  │ • Primary DB    │  │ • Session Cache │  │ • Full-Text     │                  │
│  │ • Tool Catalog  │  │ • Rate Limiting │  │ • Instant       │                  │
│  │ • User Data     │  │ • Hot Data      │  │ • Typo-Tolerant │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Supabase      │  │   MinIO/S3      │  │   ClickHouse    │                  │
│  │   (pgvector)    │  │                 │  │   (Optional)    │                  │
│  │                 │  │ • Tool Logos    │  │                 │                  │
│  │ • Embeddings    │  │ • Screenshots   │  │ • Analytics     │                  │
│  │ • Semantic      │  │ • Prompt Images │  │ • Time-Series   │                  │
│  │   Search        │  │ • User Uploads  │  │ • Dashboards    │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AUTOMATION LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                     Task Queue (Celery + Redis)                              ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                        │                                         │
│         ┌──────────────────────────────┼──────────────────────────────┐         │
│         ▼                              ▼                              ▼         │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐      │
│  │ Product Hunt    │        │ GitHub Trending │        │ ArXiv Paper     │      │
│  │ Crawler         │        │ Scraper         │        │ Processor       │      │
│  │                 │        │                 │        │                 │      │
│  │ • Daily Fetch   │        │ • Star Tracking │        │ • Paper Fetch   │      │
│  │ • Vote Filter   │        │ • Topic Filter  │        │ • LLM Summary   │      │
│  │ • Auto-Ingest   │        │ • Readme Parse  │        │ • Translation   │      │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘      │
│                                                                                  │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐      │
│  │ RSS Aggregator  │        │ Embedding Gen   │        │ Screenshot Bot  │      │
│  │                 │        │                 │        │                 │      │
│  │ • 36Kr/InfoQ    │        │ • Tool Desc     │        │ • Playwright    │      │
│  │ • 机器之心       │        │ • Query Embed   │        │ • Thumbnail     │      │
│  │ • Dedup Engine  │        │ • Similarity    │        │ • Auto-Update   │      │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Architecture

### 3.1 Frontend Architecture (Next.js 14+)

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEXT.JS APPLICATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  app/                                                            │
│  ├── (marketing)/          # Landing & static pages             │
│  │   ├── page.tsx          # Homepage with search               │
│  │   ├── about/                                                 │
│  │   └── pricing/                                               │
│  │                                                              │
│  ├── (tools)/              # Tool discovery                     │
│  │   ├── tools/                                                 │
│  │   │   ├── page.tsx      # Tool listing                       │
│  │   │   ├── [slug]/       # Tool detail                        │
│  │   │   └── compare/      # Tool comparison                    │
│  │   ├── categories/                                            │
│  │   └── scenarios/        # Jobs-to-be-Done pages              │
│  │                                                              │
│  ├── (learning)/           # Learning hub                       │
│  │   ├── roadmaps/                                              │
│  │   ├── tutorials/                                             │
│  │   ├── prompts/                                               │
│  │   └── papers/           # ArXiv summaries                    │
│  │                                                              │
│  ├── (user)/               # User features                      │
│  │   ├── collections/                                           │
│  │   ├── history/                                               │
│  │   └── settings/                                              │
│  │                                                              │
│  ├── api/                  # API Routes (BFF)                   │
│  │   ├── search/                                                │
│  │   ├── auth/                                                  │
│  │   └── webhooks/                                              │
│  │                                                              │
│  └── layout.tsx            # Root layout                        │
│                                                                  │
│  components/                                                     │
│  ├── search/                                                    │
│  │   ├── SearchBar.tsx          # Main search component         │
│  │   ├── SearchResults.tsx      # Results display               │
│  │   ├── ScenarioChips.tsx      # Quick scenario buttons        │
│  │   └── Autocomplete.tsx       # Suggestion dropdown           │
│  │                                                              │
│  ├── tools/                                                     │
│  │   ├── ToolCard.tsx           # Tool display card             │
│  │   ├── ToolGrid.tsx           # Grid layout                   │
│  │   ├── ToolCompare.tsx        # Side-by-side comparison       │
│  │   ├── PricingBadge.tsx       # Free/Freemium/Paid badge      │
│  │   └── AccessBadge.tsx        # 国内直连/VPN标识               │
│  │                                                              │
│  ├── learning/                                                  │
│  │   ├── RoadmapViewer.tsx      # Interactive SVG roadmap       │
│  │   ├── PromptCard.tsx         # Prompt with copy button       │
│  │   └── TutorialPlayer.tsx     # Embedded video player         │
│  │                                                              │
│  └── ui/                        # shadcn/ui components          │
│                                                                  │
│  lib/                                                           │
│  ├── api/                       # API client functions          │
│  ├── hooks/                     # Custom React hooks            │
│  ├── utils/                     # Utility functions             │
│  └── constants/                 # App constants                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Backend Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 MICROSERVICES STRUCTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  services/                                                       │
│  │                                                              │
│  ├── content-service/           # Core content management       │
│  │   ├── app/                                                   │
│  │   │   ├── main.py            # FastAPI app                   │
│  │   │   ├── routers/                                           │
│  │   │   │   ├── tools.py       # Tool CRUD                     │
│  │   │   │   ├── categories.py  # Category management           │
│  │   │   │   ├── scenarios.py   # Scenario management           │
│  │   │   │   └── ratings.py     # User ratings                  │
│  │   │   ├── models/            # SQLAlchemy models             │
│  │   │   ├── schemas/           # Pydantic schemas              │
│  │   │   └── services/          # Business logic                │
│  │   └── Dockerfile                                             │
│  │                                                              │
│  ├── search-service/            # Search infrastructure         │
│  │   ├── app/                                                   │
│  │   │   ├── main.py                                            │
│  │   │   ├── routers/                                           │
│  │   │   │   ├── search.py      # Full-text search              │
│  │   │   │   ├── semantic.py    # Vector search                 │
│  │   │   │   └── suggest.py     # Autocomplete                  │
│  │   │   ├── indexers/          # Meilisearch indexers          │
│  │   │   └── embeddings/        # Embedding generators          │
│  │   └── Dockerfile                                             │
│  │                                                              │
│  ├── learning-service/          # Learning content              │
│  │   ├── app/                                                   │
│  │   │   ├── routers/                                           │
│  │   │   │   ├── roadmaps.py    # Learning roadmaps             │
│  │   │   │   ├── tutorials.py   # Tutorial management           │
│  │   │   │   ├── prompts.py     # Prompt library                │
│  │   │   │   └── papers.py      # ArXiv papers                  │
│  │   └── Dockerfile                                             │
│  │                                                              │
│  ├── user-service/              # User management               │
│  │   ├── app/                                                   │
│  │   │   ├── routers/                                           │
│  │   │   │   ├── auth.py        # Authentication                │
│  │   │   │   ├── profile.py     # User profile                  │
│  │   │   │   └── collections.py # Saved collections             │
│  │   └── Dockerfile                                             │
│  │                                                              │
│  └── automation-service/        # Content automation            │
│      ├── app/                                                   │
│      │   ├── workers/                                           │
│      │   │   ├── producthunt.py # Product Hunt crawler          │
│      │   │   ├── github.py      # GitHub trending scraper       │
│      │   │   ├── arxiv.py       # ArXiv paper processor         │
│      │   │   ├── rss.py         # RSS feed aggregator           │
│      │   │   └── screenshot.py  # Screenshot generator          │
│      │   ├── pipelines/                                         │
│      │   │   ├── ingest.py      # Tool ingestion pipeline       │
│      │   │   └── enrich.py      # Data enrichment pipeline      │
│      │   └── tasks/             # Celery task definitions       │
│      └── Dockerfile                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Diagrams

### 4.1 Search Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────▶│  Next.js     │────▶│  API Gateway │
│  Types Query │     │  Frontend    │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     │                            │                            │
                     ▼                            ▼                            ▼
              ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
              │ Meilisearch │            │  pgvector   │            │   Redis     │
              │ Full-Text   │            │  Semantic   │            │   Cache     │
              │ Search      │            │  Search     │            │   (Hot)     │
              └─────────────┘            └─────────────┘            └─────────────┘
                     │                            │                            │
                     └────────────────────────────┼────────────────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  Result Merger  │
                                         │  & Ranker       │
                                         │                 │
                                         │ • Score Fusion  │
                                         │ • Deduplication │
                                         │ • Personalize   │
                                         └─────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  Response to    │
                                         │  Frontend       │
                                         └─────────────────┘
```

### 4.2 Content Automation Pipeline

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        AUTOMATED CONTENT DISCOVERY                              │
└────────────────────────────────────────────────────────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  Product Hunt   │           │  GitHub API     │           │  ArXiv API      │
│  API v2         │           │  + Scraper      │           │                 │
│                 │           │                 │           │                 │
│ Schedule: Daily │           │ Schedule: 6h    │           │ Schedule: Daily │
│ Filter: AI cat  │           │ Filter: Python  │           │ Filter: cs.AI   │
│ Threshold: 100  │           │         + stars │           │                 │
└─────────────────┘           └─────────────────┘           └─────────────────┘
         │                               │                               │
         └───────────────────────────────┼───────────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Ingestion Queue   │
                              │   (Celery + Redis)  │
                              └─────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Data Enrichment   │
                              │                     │
                              │ • Screenshot Gen    │
                              │ • LLM Description   │
                              │ • Category Classify │
                              │ • Pricing Extract   │
                              │ • Embedding Gen     │
                              └─────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Review Queue      │
                              │   (Admin Dashboard) │
                              │                     │
                              │ • Human Validation  │
                              │ • Quality Score     │
                              │ • Publish Decision  │
                              └─────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Index Update      │
                              │                     │
                              │ • PostgreSQL Write  │
                              │ • Meilisearch Sync  │
                              │ • Vector DB Update  │
                              │ • CDN Invalidation  │
                              └─────────────────────┘
```

---

## 5. Technology Stack Summary

### 5.1 Frontend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | Next.js 14+ (App Router) | SSR/ISR for SEO, React Server Components |
| Language | TypeScript 5.x | Type safety, developer experience |
| Styling | Tailwind CSS 4.0 | Utility-first, responsive design |
| UI Library | shadcn/ui + Radix | Accessible, customizable components |
| State | Zustand / TanStack Query | Lightweight state, server state caching |
| Search UI | InstantSearch.js | Meilisearch integration |
| Charts | Recharts / Tremor | Data visualization |
| Icons | Lucide React | Consistent iconography |

### 5.2 Backend Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| API Framework | FastAPI 0.115+ | High performance, OpenAPI auto-docs |
| Language | Python 3.12+ | ML ecosystem, rapid development |
| ORM | SQLAlchemy 2.0 | Async support, type hints |
| Validation | Pydantic V2 | Fast validation, OpenAPI integration |
| Task Queue | Celery 5.x | Distributed task processing |
| Message Broker | Redis | Celery backend, caching |
| Web Scraping | Playwright / httpx | JavaScript rendering, async HTTP |
| ML/Embeddings | sentence-transformers | Multilingual embedding generation |

### 5.3 Data Layer

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Primary DB | PostgreSQL 16 | Reliability, JSON support, extensions |
| Vector Store | Supabase pgvector | Integrated with PostgreSQL |
| Search Engine | Meilisearch | Fast, typo-tolerant, Chinese support |
| Cache | Redis 7 | Session, rate limiting, hot data |
| Object Storage | MinIO / Aliyun OSS | S3-compatible, China-friendly |
| Analytics DB | ClickHouse (optional) | Time-series analytics |

### 5.4 Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Container | Docker + Docker Compose | Consistent environments |
| Orchestration | Kubernetes (Phase 2) | Scaling, self-healing |
| API Gateway | Kong / Traefik | Rate limiting, auth, routing |
| CDN | Cloudflare + 七牛云 | Global + China acceleration |
| Monitoring | Prometheus + Grafana | Metrics, dashboards |
| Logging | Loki / ELK | Centralized logging |
| CI/CD | GitHub Actions | Automated deployment |

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  WeChat  │    │  Phone   │    │  Email   │    │  GitHub  │
│  OAuth   │    │  OTP     │    │  Magic   │    │  OAuth   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     └───────────────┴───────────────┴───────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Auth Service   │
                    │  (NextAuth.js)  │
                    │                 │
                    │ • Session Mgmt  │
                    │ • JWT Tokens    │
                    │ • CSRF Protect  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  User Service   │
                    │                 │
                    │ • Profile CRUD  │
                    │ • Preferences   │
                    │ • RBAC          │
                    └─────────────────┘
```

### 6.2 Security Controls

| Layer | Control | Implementation |
|-------|---------|----------------|
| Network | HTTPS Everywhere | Let's Encrypt + Cloudflare |
| Network | DDoS Protection | Cloudflare WAF |
| API | Rate Limiting | Kong / Redis-based sliding window |
| API | Input Validation | Pydantic strict mode |
| Data | Encryption at Rest | PostgreSQL TDE |
| Data | PII Protection | Minimal collection, anonymization |
| Auth | Session Security | HttpOnly cookies, SameSite=Strict |
| Auth | CSRF Protection | Double-submit cookie pattern |

---

## 7. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| TTFB (Time to First Byte) | < 200ms | Lighthouse, China PoP |
| LCP (Largest Contentful Paint) | < 1.2s | Core Web Vitals |
| FID (First Input Delay) | < 100ms | Core Web Vitals |
| Search Response | < 50ms | Meilisearch P95 |
| API Response (P95) | < 200ms | Backend services |
| Availability | 99.9% | Monthly SLA |
| Page Cache Hit Rate | > 95% | CDN metrics |

---

## 8. Deployment Architecture

### 8.1 Initial Deployment (Hong Kong)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALIYUN HONG KONG REGION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VPC (10.0.0.0/16)                      │   │
│  │                                                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                │   │
│  │  │  Public Subnet  │  │  Private Subnet │                │   │
│  │  │  10.0.1.0/24    │  │  10.0.2.0/24    │                │   │
│  │  │                 │  │                 │                │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │                │   │
│  │  │  │   Nginx   │  │  │  │   App     │  │                │   │
│  │  │  │   LB      │  │  │  │  Servers  │  │                │   │
│  │  │  └───────────┘  │  │  │  (x2)     │  │                │   │
│  │  │                 │  │  └───────────┘  │                │   │
│  │  │  ┌───────────┐  │  │                 │                │   │
│  │  │  │  Bastion  │  │  │  ┌───────────┐  │                │   │
│  │  │  │   Host    │  │  │  │  Workers  │  │                │   │
│  │  │  └───────────┘  │  │  │  (Celery) │  │                │   │
│  │  │                 │  │  └───────────┘  │                │   │
│  │  └─────────────────┘  └─────────────────┘                │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │              Managed Services                        │ │   │
│  │  │                                                      │ │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │   │
│  │  │  │ RDS      │  │  Redis   │  │  OSS     │           │ │   │
│  │  │  │ Postgres │  │  Cluster │  │  Bucket  │           │ │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘           │ │   │
│  │  │                                                      │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CDN LAYER                                │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Cloudflare    │  │    七牛云 CDN    │  │   又拍云 CDN    │  │
│  │   (Global)      │  │   (China PoP)   │  │   (China PoP)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Scalability Strategy

### 9.1 Horizontal Scaling Triggers

| Service | Metric | Scale Up Threshold | Scale Down Threshold |
|---------|--------|-------------------|---------------------|
| Web App | CPU | > 70% for 5 min | < 30% for 15 min |
| Search API | Latency P95 | > 100ms | < 30ms |
| Content API | Request Rate | > 1000 RPS | < 200 RPS |
| Celery Workers | Queue Depth | > 100 tasks | < 10 tasks |

### 9.2 Database Scaling Path

```
Phase 1: Single PostgreSQL (RDS)
    │
    ▼ Traffic > 10K DAU
Phase 2: Read Replicas (1 Primary + 2 Replicas)
    │
    ▼ Traffic > 100K DAU
Phase 3: Connection Pooling (PgBouncer)
    │
    ▼ Traffic > 500K DAU
Phase 4: Sharding by Tool Category
```

---

## 10. Monitoring & Observability

### 10.1 Metrics Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY STACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Prometheus    │  │     Loki        │  │    Tempo        │  │
│  │   (Metrics)     │  │   (Logs)        │  │   (Traces)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                 │
│                                ▼                                 │
│                       ┌─────────────────┐                       │
│                       │     Grafana     │                       │
│                       │   Dashboards    │                       │
│                       └─────────────────┘                       │
│                                │                                 │
│                                ▼                                 │
│                       ┌─────────────────┐                       │
│                       │   Alertmanager  │                       │
│                       │   + PagerDuty   │                       │
│                       └─────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Key Dashboards

1. **System Health**: CPU, Memory, Disk, Network across all services
2. **Application Metrics**: Request rate, latency, error rate by endpoint
3. **Search Performance**: Query latency, cache hit rate, top queries
4. **Content Pipeline**: Ingestion rate, enrichment success, queue depth
5. **Business Metrics**: DAU, tool views, search volume, conversion rates

---

## 11. Cost Estimation (Initial Phase)

| Resource | Specification | Monthly Cost (USD) |
|----------|---------------|-------------------|
| App Server (x2) | 4 vCPU, 8GB RAM | ~$200 |
| PostgreSQL RDS | 4 vCPU, 16GB RAM, 100GB | ~$150 |
| Redis Cluster | 2GB Memory | ~$50 |
| Object Storage | 100GB + CDN | ~$30 |
| Meilisearch | 2 vCPU, 4GB RAM | ~$80 |
| CDN (China) | 500GB bandwidth | ~$100 |
| Monitoring | Grafana Cloud free tier | $0 |
| **Total** | | **~$610/month** |

---

## 12. Implementation Phases

### Phase 1: MVP (4-6 weeks)
- [ ] Next.js frontend with basic search
- [ ] PostgreSQL + Meilisearch setup
- [ ] Manual tool ingestion (100 tools)
- [ ] Basic category navigation
- [ ] Responsive design

### Phase 2: Automation (4 weeks)
- [ ] Product Hunt crawler
- [ ] GitHub trending scraper
- [ ] LLM-powered enrichment
- [ ] Admin dashboard for curation

### Phase 3: Learning Hub (4 weeks)
- [ ] Roadmap viewer component
- [ ] Prompt library
- [ ] Tutorial integration
- [ ] ArXiv paper summaries

### Phase 4: Growth (Ongoing)
- [ ] WeChat integration
- [ ] User accounts & collections
- [ ] Affiliate system
- [ ] Analytics dashboard
- [ ] API monetization

---

*This architecture document serves as the technical blueprint for the AI Navigator platform. It should be reviewed and updated as requirements evolve.*
