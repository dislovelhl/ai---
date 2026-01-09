# AI Navigator Platform - Database Schema Design

> Version: 1.0.0
> Created: 2026-01-09
> Database: PostgreSQL 16 with pgvector extension

---

## 1. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATABASE SCHEMA OVERVIEW                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     users       │      │   collections   │      │ collection_items│
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ id (PK)         │──┐   │ id (PK)         │──┐   │ id (PK)         │
│ phone           │  │   │ user_id (FK)    │◀─┘   │ collection_id   │◀──┐
│ email           │  │   │ name            │  │   │ tool_id (FK)    │───┼──┐
│ wechat_openid   │  │   │ is_public       │  │   │ added_at        │   │  │
│ github_id       │  │   │ created_at      │  │   │ notes           │   │  │
│ avatar_url      │  └───│ updated_at      │  │   └─────────────────┘   │  │
│ nickname        │      └─────────────────┘  │                         │  │
│ preferences     │                           │                         │  │
│ created_at      │                           │                         │  │
└─────────────────┘                           │                         │  │
        │                                     │                         │  │
        │                                     │                         │  │
        ▼                                     │                         │  │
┌─────────────────┐      ┌─────────────────┐  │                         │  │
│  user_sessions  │      │   tool_ratings  │  │                         │  │
├─────────────────┤      ├─────────────────┤  │                         │  │
│ id (PK)         │      │ id (PK)         │  │                         │  │
│ user_id (FK)    │◀─────│ user_id (FK)    │◀─┘                         │  │
│ token           │      │ tool_id (FK)    │────────────────────────────┼──┤
│ device_info     │      │ rating          │                            │  │
│ ip_address      │      │ review_text     │                            │  │
│ expires_at      │      │ created_at      │                            │  │
│ created_at      │      └─────────────────┘                            │  │
└─────────────────┘                                                     │  │
                                                                        │  │
                    ┌───────────────────────────────────────────────────┘  │
                    │                                                      │
                    ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    tools                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ id (PK)           UUID                                                      │
│ slug              VARCHAR(255) UNIQUE                                       │
│ name              VARCHAR(255) NOT NULL                                     │
│ name_cn           VARCHAR(255)                    -- 中文名称               │
│ tagline           TEXT                            -- 一句话介绍             │
│ tagline_cn        TEXT                            -- 中文一句话介绍         │
│ description       TEXT                            -- 详细描述               │
│ description_cn    TEXT                            -- 中文详细描述           │
│ website_url       VARCHAR(512) NOT NULL                                     │
│ logo_url          VARCHAR(512)                                              │
│ screenshot_url    VARCHAR(512)                                              │
│ video_url         VARCHAR(512)                                              │
│                                                                             │
│ -- 定价信息                                                                 │
│ pricing_type      pricing_type_enum               -- free/freemium/paid     │
│ pricing_details   JSONB                           -- 详细定价结构           │
│ free_tier_limits  TEXT                            -- 免费额度说明           │
│                                                                             │
│ -- 访问性标签                                                               │
│ is_china_accessible  BOOLEAN DEFAULT true         -- 国内可直连             │
│ requires_vpn         BOOLEAN DEFAULT false        -- 需要VPN                │
│ requires_signup      BOOLEAN DEFAULT true         -- 需要注册               │
│ has_api              BOOLEAN DEFAULT false        -- 提供API                │
│ is_open_source       BOOLEAN DEFAULT false        -- 开源项目               │
│ github_url           VARCHAR(512)                 -- GitHub地址             │
│                                                                             │
│ -- 分类与标签                                                               │
│ primary_category_id  UUID REFERENCES categories(id)                         │
│ tags                 TEXT[]                       -- 标签数组               │
│ scenarios            TEXT[]                       -- 适用场景               │
│                                                                             │
│ -- 元数据                                                                   │
│ producthunt_id       VARCHAR(100)                 -- Product Hunt ID        │
│ producthunt_votes    INTEGER                                                │
│ github_stars         INTEGER                                                │
│ source               source_enum                  -- 来源渠道               │
│                                                                             │
│ -- 向量嵌入 (语义搜索)                                                      │
│ embedding            vector(384)                  -- 文本嵌入向量           │
│                                                                             │
│ -- 统计与排序                                                               │
│ view_count           INTEGER DEFAULT 0                                      │
│ click_count          INTEGER DEFAULT 0                                      │
│ rating_avg           DECIMAL(3,2)                                           │
│ rating_count         INTEGER DEFAULT 0                                      │
│ popularity_score     DECIMAL(10,2)                -- 综合热度分数           │
│                                                                             │
│ -- 状态与时间                                                               │
│ status               status_enum DEFAULT 'draft'                            │
│ featured             BOOLEAN DEFAULT false        -- 编辑推荐               │
│ featured_order       INTEGER                      -- 推荐排序               │
│ created_at           TIMESTAMPTZ DEFAULT NOW()                              │
│ updated_at           TIMESTAMPTZ DEFAULT NOW()                              │
│ published_at         TIMESTAMPTZ                                            │
│ last_verified_at     TIMESTAMPTZ                  -- 最后验证时间           │
└─────────────────────────────────────────────────────────────────────────────┘
        │                    │
        │                    │
        ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   categories    │  │  tool_scenarios │  │ tool_comparisons│
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ id (PK)         │  │ tool_id (FK)    │  │ id (PK)         │
│ slug            │  │ scenario_id(FK) │  │ tool_a_id (FK)  │
│ name            │  │ relevance_score │  │ tool_b_id (FK)  │
│ name_cn         │  └─────────────────┘  │ comparison_data │
│ description     │          │            │ created_at      │
│ icon            │          ▼            └─────────────────┘
│ parent_id (FK)  │  ┌─────────────────┐
│ display_order   │  │    scenarios    │
│ tool_count      │  ├─────────────────┤
│ created_at      │  │ id (PK)         │
└─────────────────┘  │ slug            │
                     │ name            │  -- e.g., "写周报"
                     │ name_cn         │
                     │ description     │
                     │ icon            │
                     │ keywords        │  -- 搜索关键词
                     │ tool_count      │
                     │ display_order   │
                     │ created_at      │
                     └─────────────────┘
```

---

## 2. Core Tables

### 2.1 Tools Table

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enum types
CREATE TYPE pricing_type_enum AS ENUM ('free', 'freemium', 'paid', 'beta_free', 'open_source');
CREATE TYPE source_enum AS ENUM ('manual', 'producthunt', 'github', 'user_submit', 'crawler');
CREATE TYPE status_enum AS ENUM ('draft', 'pending_review', 'published', 'archived', 'rejected');

-- Main tools table
CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(255) NOT NULL UNIQUE,

    -- Basic info
    name VARCHAR(255) NOT NULL,
    name_cn VARCHAR(255),
    tagline TEXT,
    tagline_cn TEXT,
    description TEXT,
    description_cn TEXT,

    -- URLs
    website_url VARCHAR(512) NOT NULL,
    logo_url VARCHAR(512),
    screenshot_url VARCHAR(512),
    video_url VARCHAR(512),

    -- Pricing
    pricing_type pricing_type_enum NOT NULL DEFAULT 'freemium',
    pricing_details JSONB DEFAULT '{}',
    free_tier_limits TEXT,

    -- Access characteristics (critical for Chinese users)
    is_china_accessible BOOLEAN DEFAULT true,
    requires_vpn BOOLEAN DEFAULT false,
    requires_signup BOOLEAN DEFAULT true,
    has_api BOOLEAN DEFAULT false,
    is_open_source BOOLEAN DEFAULT false,
    github_url VARCHAR(512),

    -- Classification
    primary_category_id UUID,
    tags TEXT[] DEFAULT '{}',
    scenarios TEXT[] DEFAULT '{}',

    -- External references
    producthunt_id VARCHAR(100),
    producthunt_votes INTEGER,
    github_stars INTEGER,
    source source_enum NOT NULL DEFAULT 'manual',

    -- Vector embedding for semantic search
    embedding vector(384),

    -- Metrics
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    popularity_score DECIMAL(10,2) DEFAULT 0,

    -- Status
    status status_enum NOT NULL DEFAULT 'draft',
    featured BOOLEAN DEFAULT false,
    featured_order INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    last_verified_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT tools_website_url_check CHECK (website_url ~ '^https?://'),
    CONSTRAINT tools_rating_avg_check CHECK (rating_avg >= 0 AND rating_avg <= 5)
);

-- Indexes for tools table
CREATE INDEX idx_tools_slug ON tools(slug);
CREATE INDEX idx_tools_status ON tools(status) WHERE status = 'published';
CREATE INDEX idx_tools_category ON tools(primary_category_id);
CREATE INDEX idx_tools_pricing ON tools(pricing_type);
CREATE INDEX idx_tools_china_accessible ON tools(is_china_accessible) WHERE is_china_accessible = true;
CREATE INDEX idx_tools_featured ON tools(featured, featured_order) WHERE featured = true;
CREATE INDEX idx_tools_popularity ON tools(popularity_score DESC);
CREATE INDEX idx_tools_tags ON tools USING GIN(tags);
CREATE INDEX idx_tools_scenarios ON tools USING GIN(scenarios);
CREATE INDEX idx_tools_name_trgm ON tools USING GIN(name gin_trgm_ops);
CREATE INDEX idx_tools_embedding ON tools USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search index (Chinese support via pg_jieba if installed)
CREATE INDEX idx_tools_fts ON tools USING GIN(
    to_tsvector('simple', coalesce(name, '') || ' ' || coalesce(name_cn, '') || ' ' || coalesce(tagline, ''))
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tools_updated_at
    BEFORE UPDATE ON tools
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 Categories Table

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    name_cn VARCHAR(100),
    description TEXT,
    description_cn TEXT,
    icon VARCHAR(50),  -- Lucide icon name
    color VARCHAR(7),  -- Hex color code

    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    display_order INTEGER DEFAULT 0,
    tool_count INTEGER DEFAULT 0,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_active ON categories(is_active) WHERE is_active = true;
CREATE INDEX idx_categories_order ON categories(display_order);

-- Foreign key for tools.primary_category_id
ALTER TABLE tools ADD CONSTRAINT fk_tools_category
    FOREIGN KEY (primary_category_id) REFERENCES categories(id) ON DELETE SET NULL;
```

### 2.3 Scenarios Table (Jobs-to-be-Done)

```sql
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) NOT NULL UNIQUE,

    name VARCHAR(100) NOT NULL,  -- e.g., "Generate PPT"
    name_cn VARCHAR(100),        -- e.g., "一键生成PPT"
    description TEXT,
    description_cn TEXT,

    icon VARCHAR(50),
    color VARCHAR(7),
    keywords TEXT[] DEFAULT '{}',  -- Related search terms

    tool_count INTEGER DEFAULT 0,
    display_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT false,  -- Show on homepage

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scenarios_featured ON scenarios(is_featured) WHERE is_featured = true;
CREATE INDEX idx_scenarios_keywords ON scenarios USING GIN(keywords);

-- Junction table for tools-scenarios many-to-many
CREATE TABLE tool_scenarios (
    tool_id UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0,

    PRIMARY KEY (tool_id, scenario_id)
);

CREATE INDEX idx_tool_scenarios_scenario ON tool_scenarios(scenario_id);
```

---

## 3. User Tables

### 3.1 Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Authentication identifiers (at least one required)
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    wechat_openid VARCHAR(100) UNIQUE,
    github_id VARCHAR(100) UNIQUE,

    -- Profile
    nickname VARCHAR(100),
    avatar_url VARCHAR(512),
    bio TEXT,

    -- Preferences (JSONB for flexibility)
    preferences JSONB DEFAULT '{
        "theme": "system",
        "language": "zh-CN",
        "email_notifications": true,
        "weekly_digest": true
    }',

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role VARCHAR(20) DEFAULT 'user',  -- user, curator, admin

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT users_at_least_one_auth CHECK (
        phone IS NOT NULL OR
        email IS NOT NULL OR
        wechat_openid IS NOT NULL OR
        github_id IS NOT NULL
    )
);

CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_users_wechat ON users(wechat_openid) WHERE wechat_openid IS NOT NULL;
CREATE INDEX idx_users_role ON users(role);
```

### 3.2 User Sessions

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    token_hash VARCHAR(64) NOT NULL,  -- SHA256 of session token
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,

    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

### 3.3 User Collections

```sql
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(512),

    is_public BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT false,  -- Default "Favorites" collection

    tool_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_collections_user ON collections(user_id);
CREATE INDEX idx_collections_public ON collections(is_public) WHERE is_public = true;

CREATE TABLE collection_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    tool_id UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,

    notes TEXT,
    display_order INTEGER DEFAULT 0,

    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(collection_id, tool_id)
);

CREATE INDEX idx_collection_items_collection ON collection_items(collection_id);
CREATE INDEX idx_collection_items_tool ON collection_items(tool_id);
```

### 3.4 Tool Ratings & Reviews

```sql
CREATE TABLE tool_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tool_id UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,

    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,

    -- Upvotes from other users
    helpful_count INTEGER DEFAULT 0,

    is_verified_user BOOLEAN DEFAULT false,  -- Verified they actually use the tool
    is_visible BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, tool_id)
);

CREATE INDEX idx_ratings_tool ON tool_ratings(tool_id);
CREATE INDEX idx_ratings_user ON tool_ratings(user_id);
CREATE INDEX idx_ratings_visible ON tool_ratings(is_visible) WHERE is_visible = true;

-- Function to update tool rating average
CREATE OR REPLACE FUNCTION update_tool_rating_avg()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE tools SET
        rating_avg = (SELECT AVG(rating)::DECIMAL(3,2) FROM tool_ratings WHERE tool_id = COALESCE(NEW.tool_id, OLD.tool_id) AND is_visible = true),
        rating_count = (SELECT COUNT(*) FROM tool_ratings WHERE tool_id = COALESCE(NEW.tool_id, OLD.tool_id) AND is_visible = true)
    WHERE id = COALESCE(NEW.tool_id, OLD.tool_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tool_rating
    AFTER INSERT OR UPDATE OR DELETE ON tool_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_tool_rating_avg();
```

---

## 4. Learning Hub Tables

### 4.1 Roadmaps

```sql
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) NOT NULL UNIQUE,

    title VARCHAR(200) NOT NULL,
    title_cn VARCHAR(200),
    description TEXT,
    description_cn TEXT,

    -- SVG content for interactive roadmap
    svg_content TEXT,

    -- JSON structure for programmatic access
    structure JSONB NOT NULL DEFAULT '[]',

    -- Metadata
    difficulty_level VARCHAR(20),  -- beginner, intermediate, advanced
    estimated_hours INTEGER,

    author_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Status
    is_published BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

CREATE INDEX idx_roadmaps_published ON roadmaps(is_published) WHERE is_published = true;
CREATE INDEX idx_roadmaps_difficulty ON roadmaps(difficulty_level);
```

### 4.2 Prompts Library

```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    title VARCHAR(200) NOT NULL,
    title_cn VARCHAR(200),

    -- The actual prompt content
    prompt_text TEXT NOT NULL,

    -- For image generation prompts
    preview_image_url VARCHAR(512),

    -- Classification
    model_type VARCHAR(50) NOT NULL,  -- chatgpt, midjourney, stable_diffusion, etc.
    category VARCHAR(50),             -- writing, coding, design, etc.
    tags TEXT[] DEFAULT '{}',

    -- Example output
    example_output TEXT,
    example_output_image_url VARCHAR(512),

    -- Metadata
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    source_url VARCHAR(512),

    -- Metrics
    copy_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,

    is_featured BOOLEAN DEFAULT false,
    is_published BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_prompts_model ON prompts(model_type);
CREATE INDEX idx_prompts_category ON prompts(category);
CREATE INDEX idx_prompts_tags ON prompts USING GIN(tags);
CREATE INDEX idx_prompts_featured ON prompts(is_featured) WHERE is_featured = true;
```

### 4.3 ArXiv Papers

```sql
CREATE TABLE arxiv_papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arxiv_id VARCHAR(20) NOT NULL UNIQUE,  -- e.g., "2401.12345"

    title TEXT NOT NULL,
    title_cn TEXT,  -- AI-translated Chinese title

    abstract TEXT,
    abstract_cn TEXT,  -- AI-translated Chinese abstract

    -- AI-generated summary
    summary TEXT,
    summary_cn TEXT,
    key_findings TEXT[],
    practical_applications TEXT[],

    authors TEXT[] NOT NULL,
    categories TEXT[] NOT NULL,  -- cs.AI, cs.CL, etc.

    pdf_url VARCHAR(512) NOT NULL,

    -- Date info
    submitted_date DATE NOT NULL,
    updated_date DATE,

    -- Metrics
    view_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,

    -- Processing status
    is_processed BOOLEAN DEFAULT false,
    is_published BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_papers_arxiv_id ON arxiv_papers(arxiv_id);
CREATE INDEX idx_papers_date ON arxiv_papers(submitted_date DESC);
CREATE INDEX idx_papers_categories ON arxiv_papers USING GIN(categories);
CREATE INDEX idx_papers_published ON arxiv_papers(is_published) WHERE is_published = true;
```

---

## 5. Analytics Tables

### 5.1 Page Views & Events

```sql
CREATE TABLE page_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Page info
    page_path VARCHAR(500) NOT NULL,
    page_title VARCHAR(200),
    referrer VARCHAR(500),

    -- Entity reference (optional)
    entity_type VARCHAR(50),  -- tool, category, roadmap, etc.
    entity_id UUID,

    -- User info (anonymous tracking)
    session_id VARCHAR(64),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Device/geo info
    device_type VARCHAR(20),  -- desktop, mobile, tablet
    browser VARCHAR(50),
    os VARCHAR(50),
    country_code CHAR(2),
    region VARCHAR(100),

    -- Timestamps
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partition by month for performance
CREATE INDEX idx_pageviews_date ON page_views(viewed_at);
CREATE INDEX idx_pageviews_path ON page_views(page_path);
CREATE INDEX idx_pageviews_entity ON page_views(entity_type, entity_id);
CREATE INDEX idx_pageviews_session ON page_views(session_id);

-- Search queries tracking
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    query_text VARCHAR(500) NOT NULL,
    query_normalized VARCHAR(500),  -- Lowercase, trimmed

    results_count INTEGER,
    clicked_result_id UUID,  -- Which result was clicked

    session_id VARCHAR(64),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_search_date ON search_queries(searched_at);
CREATE INDEX idx_search_query ON search_queries(query_normalized);
```

### 5.2 Aggregated Stats (Daily)

```sql
CREATE TABLE daily_stats (
    date DATE NOT NULL,

    -- Global metrics
    total_pageviews INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    total_searches INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,

    -- Top content (JSONB arrays)
    top_tools JSONB DEFAULT '[]',      -- [{id, name, views, clicks}]
    top_categories JSONB DEFAULT '[]',
    top_searches JSONB DEFAULT '[]',   -- [{query, count}]

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (date)
);

-- Tool-level daily stats
CREATE TABLE tool_daily_stats (
    tool_id UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    collection_adds INTEGER DEFAULT 0,
    rating_submissions INTEGER DEFAULT 0,

    PRIMARY KEY (tool_id, date)
);

CREATE INDEX idx_tool_stats_date ON tool_daily_stats(date);
```

---

## 6. Content Automation Tables

### 6.1 Ingestion Queue

```sql
CREATE TYPE ingestion_status_enum AS ENUM (
    'pending', 'processing', 'enriching', 'review', 'approved', 'rejected', 'error'
);

CREATE TABLE ingestion_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Source info
    source source_enum NOT NULL,
    source_id VARCHAR(100),  -- External ID from source
    source_url VARCHAR(512) NOT NULL,

    -- Raw data from source
    raw_data JSONB NOT NULL,

    -- Extracted/enriched data
    extracted_name VARCHAR(255),
    extracted_tagline TEXT,
    extracted_description TEXT,
    extracted_pricing pricing_type_enum,

    -- AI-generated content
    ai_description_cn TEXT,
    ai_category_suggestion UUID,
    ai_scenario_suggestions UUID[],
    ai_tags TEXT[],

    -- Screenshots
    screenshot_url VARCHAR(512),
    logo_url VARCHAR(512),

    -- Processing status
    status ingestion_status_enum NOT NULL DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Review info
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    -- Result
    created_tool_id UUID REFERENCES tools(id),

    -- Timestamps
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ingestion_status ON ingestion_queue(status);
CREATE INDEX idx_ingestion_source ON ingestion_queue(source, source_id);
CREATE INDEX idx_ingestion_pending ON ingestion_queue(status) WHERE status = 'pending';
```

### 6.2 Scheduled Tasks

```sql
CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    task_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,  -- crawler, enrichment, cleanup, etc.

    -- Cron expression
    schedule VARCHAR(100) NOT NULL,  -- e.g., "0 0 * * *" for daily

    -- Configuration
    config JSONB DEFAULT '{}',

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMPTZ,
    last_run_status VARCHAR(20),
    last_run_duration_ms INTEGER,
    next_run_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Task run history
CREATE TABLE task_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES scheduled_tasks(id) ON DELETE CASCADE,

    status VARCHAR(20) NOT NULL,  -- running, success, failed
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,

    -- Results
    items_processed INTEGER DEFAULT 0,
    items_success INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,

    error_message TEXT,
    log_output TEXT
);

CREATE INDEX idx_task_runs_task ON task_runs(task_id);
CREATE INDEX idx_task_runs_date ON task_runs(started_at DESC);
```

---

## 7. Sample Data & Seeding

```sql
-- Sample categories
INSERT INTO categories (slug, name, name_cn, icon, display_order) VALUES
('text-generation', 'Text Generation', '文本生成', 'pen-line', 1),
('image-generation', 'Image Generation', '图像生成', 'image', 2),
('video-generation', 'Video Generation', '视频生成', 'video', 3),
('audio-speech', 'Audio & Speech', '音频与语音', 'volume-2', 4),
('coding-dev', 'Coding & Development', '编程开发', 'code', 5),
('productivity', 'Productivity', '效率工具', 'zap', 6),
('research', 'Research & Analysis', '研究分析', 'search', 7),
('design', 'Design & Creative', '设计创意', 'palette', 8),
('education', 'Education & Learning', '教育学习', 'graduation-cap', 9),
('business', 'Business & Marketing', '商业营销', 'briefcase', 10);

-- Sample scenarios
INSERT INTO scenarios (slug, name, name_cn, icon, is_featured, display_order, keywords) VALUES
('write-weekly-report', 'Write Weekly Report', '写周报', 'file-text', true, 1, ARRAY['周报', '工作总结', 'weekly report']),
('generate-ppt', 'Generate PPT', '生成PPT', 'presentation', true, 2, ARRAY['PPT', '演示文稿', 'slides']),
('polish-essay', 'Polish Essay', '论文润色', 'edit', true, 3, ARRAY['论文', '润色', '学术写作']),
('remove-background', 'Remove Background', '抠图去背景', 'eraser', true, 4, ARRAY['抠图', '去背景', 'remove bg']),
('ai-code-assistant', 'AI Coding', 'AI写代码', 'terminal', true, 5, ARRAY['写代码', '编程', 'coding']),
('translate-text', 'Translation', '翻译文本', 'languages', true, 6, ARRAY['翻译', 'translate']),
('summarize-article', 'Summarize Article', '文章总结', 'text-select', true, 7, ARRAY['总结', '摘要', 'summary']),
('generate-image', 'Generate Image', 'AI绘画', 'brush', true, 8, ARRAY['AI绘画', '生成图片', 'image generation']);

-- Sample tool (DeepSeek)
INSERT INTO tools (
    slug, name, name_cn, tagline, tagline_cn,
    description, description_cn,
    website_url, logo_url,
    pricing_type, free_tier_limits,
    is_china_accessible, requires_vpn, requires_signup, has_api, is_open_source,
    github_url, primary_category_id, tags, scenarios,
    status, featured
) VALUES (
    'deepseek',
    'DeepSeek',
    '深度求索',
    'Advanced AI assistant for reasoning and coding',
    '强大的推理和编程AI助手',
    'DeepSeek is a powerful AI model excelling in mathematical reasoning, code generation, and complex problem solving.',
    'DeepSeek（深度求索）是国产顶级大模型，在数学推理、代码生成和复杂问题解决方面表现卓越，推理成本极低，开发者首选。',
    'https://www.deepseek.com/',
    'https://www.deepseek.com/logo.png',
    'beta_free',
    '公测期间完全免费使用',
    true, false, true, true, true,
    'https://github.com/deepseek-ai',
    (SELECT id FROM categories WHERE slug = 'text-generation'),
    ARRAY['大模型', 'LLM', '推理', '代码生成', '数学', '开源'],
    ARRAY['ai-code-assistant', 'write-weekly-report'],
    'published',
    true
);
```

---

## 8. Performance Optimization

### 8.1 Materialized Views

```sql
-- Popular tools view (refreshed every 10 minutes)
CREATE MATERIALIZED VIEW mv_popular_tools AS
SELECT
    t.id,
    t.slug,
    t.name,
    t.name_cn,
    t.tagline_cn,
    t.logo_url,
    t.pricing_type,
    t.is_china_accessible,
    t.rating_avg,
    t.rating_count,
    c.name_cn as category_name,
    (t.view_count * 0.3 + t.click_count * 0.5 + t.rating_count * 20) as score
FROM tools t
LEFT JOIN categories c ON t.primary_category_id = c.id
WHERE t.status = 'published'
ORDER BY score DESC
LIMIT 100;

CREATE UNIQUE INDEX idx_mv_popular_tools_id ON mv_popular_tools(id);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_popular_tools()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_popular_tools;
END;
$$ LANGUAGE plpgsql;
```

### 8.2 Partitioning Strategy

```sql
-- Partition page_views by month for better query performance
-- (PostgreSQL 12+ native partitioning)

CREATE TABLE page_views_partitioned (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    page_path VARCHAR(500) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    session_id VARCHAR(64),
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (viewed_at);

-- Create monthly partitions
CREATE TABLE page_views_2026_01 PARTITION OF page_views_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE page_views_2026_02 PARTITION OF page_views_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Continue for other months...
```

---

## 9. Database Configuration

### 9.1 PostgreSQL Tuning (for 8GB RAM server)

```ini
# postgresql.conf optimizations
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 64MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 32MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

### 9.2 Connection Pooling (PgBouncer)

```ini
[databases]
ainav = host=localhost port=5432 dbname=ainav

[pgbouncer]
pool_mode = transaction
max_client_conn = 500
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
```

---

*This database schema is designed for scalability, supporting growth from MVP to high-traffic production with minimal schema changes.*
