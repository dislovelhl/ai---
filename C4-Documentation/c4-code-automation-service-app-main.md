# C4 Code Level: Automation Service Core Application

## Overview

- **Name**: Automation Service Core Application
- **Description**: Celery-based asynchronous task processing service for automated content crawling, enrichment, and search synchronization. Orchestrates daily pipelines to discover AI tools from multiple sources (Product Hunt, GitHub, ArXiv) and enriches them with LLM-generated metadata (Chinese translations, pricing classifications).
- **Location**: `/ainav-backend/services/automation_service/app/`
- **Language**: Python 3.10+
- **Purpose**: Manages background job scheduling and execution for content discovery, AI model enrichment, and search index synchronization. Provides manual task triggering endpoints and scheduled automatic pipelines via Celery Beat.

## Architecture

The automation service implements an **asynchronous distributed task queue** architecture with:
- **Task Scheduler**: Celery Beat for scheduled job execution (daily crawls at specific UTC times)
- **Task Queue**: Redis-backed Celery for async job execution with worker process pool
- **HTTP API Layer**: FastAPI for manual task triggering and health monitoring
- **Data Pipeline**: Multi-stage crawling → enrichment → database persistence → search indexing
- **External Integrations**: Product Hunt API, GitHub API, ArXiv API, DeepSeek LLM API, Meilisearch

## Code Elements

### FastAPI Application Entry Point

#### `main.py`

**FastAPI Application and Manual Task Endpoints**

```python
from fastapi import FastAPI
from .workers.tasks import (
    crawl_and_enrich_daily,
    sync_to_meilisearch,
    sync_github_stats,
    enrich_single_tool
)

app = FastAPI(title="AI Navigator - Automation Service")
```

**Endpoints:**

- `GET /` - **Root endpoint**
  - Description: Welcome message for automation service
  - Returns: `{"message": "Welcome to AI Navigator Automation Service"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:6-8`

- `GET /health` - **Health check endpoint**
  - Description: Service health status verification
  - Returns: `{"status": "healthy"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:10-12`

- `POST /tasks/crawl` - **Manual trigger for daily crawl**
  - Description: Queues the `crawl_and_enrich_daily` task for immediate execution
  - Implementation: Calls `crawl_and_enrich_daily.delay()`
  - Returns: `{"task_id": str, "status": "queued"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:14-18`
  - Dependencies: `crawl_and_enrich_daily` (Celery task)

- `POST /tasks/sync-search` - **Manual trigger for search index sync**
  - Description: Queues the `sync_to_meilisearch` task to sync all tools to search engine
  - Implementation: Calls `sync_to_meilisearch.delay()`
  - Returns: `{"task_id": str, "status": "queued"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:20-24`
  - Dependencies: `sync_to_meilisearch` (Celery task)

- `POST /tasks/sync-github` - **Manual trigger for GitHub stats sync**
  - Description: Queues the `sync_github_stats` task to update repository statistics
  - Implementation: Calls `sync_github_stats.delay()`
  - Returns: `{"task_id": str, "status": "queued"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:26-30`
  - Dependencies: `sync_github_stats` (Celery task)

- `POST /tasks/enrich/{tool_id}` - **Manual trigger for single tool enrichment**
  - Description: Queues enrichment task for a specific tool by UUID
  - Parameters: `tool_id: str` (UUID of tool in database)
  - Implementation: Calls `enrich_single_tool.delay(tool_id)`
  - Returns: `{"task_id": str, "status": "queued"}`
  - Location: `/ainav-backend/services/automation_service/app/main.py:32-36`
  - Dependencies: `enrich_single_tool` (Celery task)

### Celery Configuration

#### `celery_app.py`

**Celery Application Instance and Task Scheduler Configuration**

```python
from celery import Celery
from celery.signals import worker_process_init
from shared.config import settings
```

**Celery App Initialization:**

- `celery_app: Celery` - **Main Celery application instance**
  - Name: `"automation_tasks"`
  - Broker: Redis (configured via `settings.REDIS_URL`)
  - Backend: Redis (result storage)
  - Task module: `services.automation_service.app.workers.tasks`
  - Location: `/ainav-backend/services/automation_service/app/celery_app.py:5-10`
  - Configuration: JSON serialization, UTC timezone, late task acknowledgment

**Worker Signal Handler:**

- `init_worker(**kwargs)` - **Worker process initialization signal**
  - Description: Initializes SQLAlchemy database connection for worker processes
  - Triggered: When worker process starts (via `worker_process_init` signal)
  - Implementation:
    - Creates/manages asyncio event loop
    - Disposes SQLAlchemy connection pool to prevent connection leaks
  - Location: `/ainav-backend/services/automation_service/app/celery_app.py:12-24`
  - Dependencies: `shared.database.engine`

**Celery Configuration Settings:**

Located at lines 26-35:
- `task_serializer="json"` - Use JSON for task serialization
- `accept_content=["json"]` - Accept only JSON serialized tasks
- `result_serializer="json"` - Store results as JSON
- `timezone="UTC"` - All scheduling in UTC
- `enable_utc=True` - Enable UTC timezone support
- `worker_prefetch_multiplier=1` - Fetch one task at a time (prevents overloading workers)
- `task_acks_late=True` - Acknowledge tasks only after successful completion (prevents task loss)

**Beat Scheduler Configuration:**

Scheduled tasks execute automatically via Celery Beat (lines 37-52):

```python
celery_app.conf.beat_schedule = {
    "crawl-ph-daily": {
        "task": "crawl_and_enrich_daily",
        "schedule": crontab(hour=0, minute=0),  # Daily at 00:00 UTC
    },
    "crawl-github-daily": {
        "task": "crawl_github_trending_daily",
        "schedule": crontab(hour=1, minute=0),  # Daily at 01:00 UTC
    },
    "mine-arxiv-daily": {
        "task": "mine_arxiv_papers_daily",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 UTC
    },
}
```

| Schedule Name | Task Name | Task Function | Frequency | Time (UTC) |
|---------------|-----------|---------------|-----------|-----------|
| `crawl-ph-daily` | `crawl_and_enrich_daily` | Fetch Product Hunt tools → Enrich with DeepSeek → Save to DB | Daily | 00:00 |
| `crawl-github-daily` | `crawl_github_trending_daily` | Fetch GitHub trending repos → Enrich with DeepSeek → Save to DB | Daily | 01:00 |
| `mine-arxiv-daily` | `mine_arxiv_papers_daily` | Fetch ArXiv papers → Enrich with DeepSeek → Save to DB | Daily | 02:00 |

### Worker Tasks

#### `workers/tasks.py`

**Celery Task Definitions and Data Pipeline Implementations**

All tasks are decorated with `@celery_app.task(name="task_name")` and follow the pattern:
1. Synchronous wrapper (calls `asyncio.run()` for async execution)
2. Async implementation function (`_task_name_pipeline()`)

**Task 1: Daily Product Hunt Crawl and Enrichment**

- `crawl_and_enrich_daily()` (lines 21-24)
  - **Name**: `"crawl_and_enrich_daily"`
  - **Description**: Fetches AI tools from Product Hunt, enriches with Chinese metadata via DeepSeek, saves to database
  - **Trigger**: Scheduled daily at 00:00 UTC OR manual API call to `POST /tasks/crawl`
  - **Implementation**:
    - Calls `_crawl_and_enrich_pipeline()` async function
    - Uses `ProductHuntClient` to query Product Hunt GraphQL API
    - Filters tools by vote count (>100 votes)
    - Uses `DeepSeekClient` to generate:
      - Chinese name (`name_zh`)
      - Chinese description (`description_zh`)
      - Pricing classification (`pricing_type`: free/freemium/paid)
    - Creates Tool records in PostgreSQL
    - Creates or reuses "AI Tools" category
    - Triggers `sync_to_meilisearch` if new tools added
  - **Return**: `{"status": "success", "added": count}` or `{"status": "no_tools_found"}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:21-90`
  - **Dependencies**:
    - `ProductHuntClient`
    - `DeepSeekClient`
    - `Tool`, `Category` (SQLAlchemy models)
    - `sync_to_meilisearch` (task)

**Task 2: Daily GitHub Trending Crawl and Enrichment**

- `crawl_github_trending_daily()` (lines 92-95)
  - **Name**: `"crawl_github_trending_daily"`
  - **Description**: Fetches trending Python AI repositories from GitHub, enriches metadata, saves to database
  - **Trigger**: Scheduled daily at 01:00 UTC
  - **Implementation**:
    - Calls `_crawl_github_trending_pipeline()` async function
    - Uses `GitHubTrendingClient` to scrape GitHub trending page (HTML parsing with BeautifulSoup)
    - Filters for AI-related keywords in repo names/descriptions
    - Uses `DeepSeekClient` for enrichment
    - Creates Tool records with category "Open Source"
    - Sets `pricing_type="open_source"`
    - Records `github_stars` from trending count
    - Triggers `sync_to_meilisearch` if new tools added
  - **Return**: `{"status": "success", "added": count}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:92-146`
  - **Dependencies**:
    - `GitHubTrendingClient`
    - `DeepSeekClient`
    - `Tool`, `Category` (models)
    - `sync_to_meilisearch` (task)

**Task 3: Daily ArXiv Paper Mining and Enrichment**

- `mine_arxiv_papers_daily()` (lines 148-151)
  - **Name**: `"mine_arxiv_papers_daily"`
  - **Description**: Fetches latest AI research papers from ArXiv, enriches metadata, creates Tool records
  - **Trigger**: Scheduled daily at 02:00 UTC
  - **Implementation**:
    - Calls `_mine_arxiv_papers_pipeline()` async function
    - Uses `ArXivMiner` to query ArXiv API (searches category `cs.AI`)
    - Fetches 10 most recent papers (XML parsing)
    - Uses `DeepSeekClient` for enrichment
    - Creates Tool records with category "Research"
    - Truncates long descriptions (500 chars max)
    - Triggers `sync_to_meilisearch` if new tools added
  - **Return**: `{"status": "success", "added": count}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:148-201`
  - **Dependencies**:
    - `ArXivMiner`
    - `DeepSeekClient`
    - `Tool`, `Category` (models)
    - `sync_to_meilisearch` (task)

**Task 4: GitHub Repository Statistics Synchronization**

- `sync_github_stats()` (lines 203-206)
  - **Name**: `"sync_github_stats"`
  - **Description**: Updates GitHub repository statistics (stars, forks) for all tools with GitHub URLs
  - **Trigger**: Called by other tasks when tools are updated
  - **Implementation**:
    - Calls `_sync_github_stats_pipeline()` async function
    - Queries all Tools with GitHub URLs using SQLAlchemy
    - Uses `GitHubClient` to fetch repository statistics from GitHub REST API
    - Updates `tool.github_stars` and `tool.pricing_type` fields
    - Sets `pricing_type="open_source"` for GitHub repos if not set
    - Commits changes to database
    - Triggers `sync_to_meilisearch` if tools updated
  - **Return**: `{"status": "success", "synced": count}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:203-235`
  - **Dependencies**:
    - `GitHubClient`
    - `Tool` (model)
    - `sync_to_meilisearch` (task)

**Task 5: Single Tool Enrichment (Manual)**

- `enrich_single_tool(tool_id: str)` (lines 237-240)
  - **Name**: `"enrich_single_tool"`
  - **Description**: Manually enriches a single tool by UUID with DeepSeek and GitHub stats
  - **Trigger**: Manual API call to `POST /tasks/enrich/{tool_id}`
  - **Parameters**: `tool_id: str` (UUID of tool to enrich)
  - **Implementation**:
    - Calls `_enrich_single_tool_pipeline(tool_id)` async function
    - Fetches Tool record from database by UUID
    - Uses `DeepSeekClient` to generate/update Chinese metadata
    - Updates `name_zh`, `description_zh`, `pricing_type`
    - If tool URL is GitHub repo: fetches and updates `github_stars`
    - Commits changes to database
    - Triggers `sync_to_meilisearch`
  - **Return**: `{"status": "success", "tool": name}` or `{"status": "not_found"}` or `{"status": "enrichment_failed"}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:237-272`
  - **Dependencies**:
    - `DeepSeekClient`
    - `GitHubClient`
    - `Tool` (model)
    - `sync_to_meilisearch` (task)

**Task 6: Search Index Synchronization**

- `sync_to_meilisearch()` (lines 279-282)
  - **Name**: `"sync_to_meilisearch"`
  - **Description**: Syncs all Tool records from PostgreSQL to Meilisearch search engine with vector embeddings
  - **Trigger**: Automatically called after tools are created/updated OR manual API call to `POST /tasks/sync-search`
  - **Implementation**:
    - Calls `_sync_to_meilisearch_pipeline()` async function
    - Fetches all Tools with eager loading of relationships (category, scenarios)
    - For each tool:
      - Generates vector embedding using `embedding_service` (combines name, descriptions, metadata)
      - Creates document with Meilisearch fields (id, name, name_zh, slug, description, URL, category, scenarios, rating, pricing, github_stars)
      - Includes `_vectors` field with 384-dimensional embedding for vector search
    - Configures Meilisearch index:
      - Filterable attributes: `category_slug`, `scenario_slugs`, `pricing_type`, `github_stars`
      - Searchable attributes: `name`, `name_zh`, `description`, `category_name`, `scenario_names`
    - Upserts all documents to Meilisearch index `"tools"`
  - **Return**: `{"status": "success", "synced": count}` or `{"status": "no_tools"}`
  - **Location**: `/ainav-backend/services/automation_service/app/workers/tasks.py:279-340`
  - **Database Session**: Uses `AsyncSessionLocal()` for async PostgreSQL access
  - **Dependencies**:
    - `embedding_service` (from shared)
    - `MeiliClient` (from meilisearch library)
    - `Tool`, `Category`, `Scenario` (SQLAlchemy models with relationships)

**Database Access Pattern (All Tasks):**

```python
# SQLAlchemy async setup (task-level)
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Usage in tasks
async with AsyncSessionLocal() as session:
    query = select(Model).where(Model.condition == value)
    result = await session.execute(query)
    objects = result.scalars().all()  # or .scalar_one_or_none()
    # ... modifications ...
    await session.commit()
```

### Client Integrations

#### Data Source Clients

**ProductHuntClient** - `/ainav-backend/services/automation_service/app/clients/producthunt.py`

- `class ProductHuntClient`
  - **Purpose**: Query Product Hunt API for AI tools
  - **Methods**:
    - `__init__()` - Initialize with API token from settings
    - `async get_daily_ai_tools()` → `List[Dict]` (edges with nodes containing tool data)
  - **API**: Product Hunt GraphQL API v2
  - **Query Fields**: id, name, tagline, description, url, website, votesCount, createdAt
  - **Location**: `/ainav-backend/services/automation_service/app/clients/producthunt.py:7-47`
  - **Dependencies**: `httpx` (async HTTP), `settings.PRODUCTHUNT_TOKEN`

**DeepSeekClient** - `/ainav-backend/services/automation_service/app/clients/deepseek.py`

- `class DeepSeekClient`
  - **Purpose**: Enrich tool metadata with LLM-generated content (Chinese translations, pricing classifications)
  - **Methods**:
    - `__init__()` - Initialize with API key and endpoint from settings
    - `async enrich_tool_info(name: str, description: str)` → `Dict` (JSON response)
  - **API**: DeepSeek Chat API (compatible with OpenAI format)
  - **Enrichment Output JSON Fields**:
    - `name_zh: str` - Chinese tool name
    - `description_zh: str` - Chinese description translation
    - `tags: List[str]` - Chinese keyword tags
    - `pricing_type: str` - Classification (free/freemium/paid)
    - `summary: str` - One-sentence Chinese summary
  - **Model**: `deepseek-chat`
  - **Location**: `/ainav-backend/services/automation_service/app/clients/deepseek.py:8-56`
  - **Dependencies**: `httpx`, `settings.DEEPSEEK_API_KEY`, `settings.DEEPSEEK_API_URL`

**GitHubClient** - `/ainav-backend/services/automation_service/app/clients/github.py`

- `class GitHubClient`
  - **Purpose**: Fetch GitHub repository statistics
  - **Methods**:
    - `__init__()` - Initialize with optional GitHub token
    - `_extract_repo_path(url: str)` → `str` - Extract owner/repo from GitHub URL
    - `async get_repo_stats(url: str)` → `Dict` (repository statistics)
  - **API**: GitHub REST API v3
  - **Statistics Output Fields**:
    - `stars: int` - Star count (stargazers_count)
    - `forks: int` - Fork count
    - `last_updated: str` - Last update timestamp
    - `license: str` - License name
    - `language: str` - Primary programming language
  - **URL Parsing**: Regex extraction of `owner/repo` from various GitHub URL formats
  - **Location**: `/ainav-backend/services/automation_service/app/clients/github.py:8-48`
  - **Dependencies**: `httpx`, `settings.GITHUB_TOKEN` (optional)

**GitHubTrendingClient** - `/ainav-backend/services/automation_service/app/clients/github_trending.py`

- `class GitHubTrendingClient`
  - **Purpose**: Scrape GitHub Trending page for trending AI repositories
  - **Methods**:
    - `__init__()` - Initialize with User-Agent header
    - `async get_trending_repos(language: str = "python")` → `List[Dict]`
  - **Data Source**: GitHub Trending page (HTML scraping with BeautifulSoup)
  - **Filtering**: Searches repo names/descriptions for AI keywords
  - **AI Keywords**: "ai", "llm", "gpt", "model", "inference", "agent", "rag", "intelligence", "transformer"
  - **Repository Output Fields**:
    - `name: str` - Repository name
    - `full_name: str` - owner/repo format
    - `description: str` - Repository description
    - `url: str` - Repository URL
    - `stars_today: int` - Stars gained today
  - **Location**: `/ainav-backend/services/automation_service/app/clients/github_trending.py:8-70`
  - **Dependencies**: `httpx`, `BeautifulSoup` (lxml parser)

**ArXivMiner** - `/ainav-backend/services/automation_service/app/clients/arxiv_miner.py`

- `class ArXivMiner`
  - **Purpose**: Mine AI research papers from ArXiv API
  - **Methods**:
    - `__init__()` - Initialize with ArXiv API endpoint
    - `async get_latest_papers(category: str = "cs.AI", days: int = 1)` → `List[Dict]`
  - **API**: ArXiv Query API (Atom feed / XML)
  - **Search**: Category filter (default: `cs.AI` for computer science AI)
  - **Sorting**: By submitted date (most recent first)
  - **Limit**: 10 results per query
  - **Paper Output Fields**:
    - `name: str` - Paper title (truncated to 100 chars)
    - `title: str` - Full paper title
    - `description: str` - Abstract summary
    - `url: str` - ArXiv paper URL
    - `published_at: str` - Publication date
    - `category: str` - Literal "Scientific Paper"
  - **Location**: `/ainav-backend/services/automation_service/app/clients/arxiv_miner.py:9-53`
  - **Dependencies**: `httpx`, `xml.etree.ElementTree` (XML parsing)

## Dependencies

### Internal Dependencies

| Module | Type | Usage |
|--------|------|-------|
| `shared.config.settings` | Configuration | Database URL, Redis URL, API keys, API endpoints |
| `shared.models.Tool` | SQLAlchemy Model | Primary data entity for AI tools |
| `shared.models.Category` | SQLAlchemy Model | Tool categorization |
| `shared.models.Scenario` | SQLAlchemy Model | Use case scenarios (for search filtering) |
| `shared.database.engine` | AsyncEngine | SQLAlchemy async database connection |
| `shared.embedding.embedding_service` | Embedding Service | Generate 384-dim vector embeddings for Meilisearch |

### External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `celery` | Latest | Distributed task queue framework |
| `redis` | - | Message broker and result backend |
| `fastapi` | Latest | HTTP API framework for task triggering endpoints |
| `sqlalchemy[asyncio]` | 2.0+ | Async ORM for database operations |
| `httpx` | Latest | Async HTTP client for external APIs |
| `meilisearch` | Latest | Search engine client |
| `beautifulsoup4` | Latest | HTML/XML parsing for GitHub scraping |
| `lxml` | Latest | HTML parser backend for BeautifulSoup |
| `pydantic-settings` | Latest | Configuration management |
| `asyncpg` | Latest | PostgreSQL async driver |

### Service Integrations

| Service | Endpoint | Authentication | Usage |
|---------|----------|-----------------|-------|
| **Product Hunt API** | `https://api.producthunt.com/v2/api/graphql` | Bearer token (`PRODUCTHUNT_TOKEN`) | Daily AI tool discovery |
| **DeepSeek API** | `https://api.deepseek.com/v1/chat/completions` | Bearer token (`DEEPSEEK_API_KEY`) | Tool metadata enrichment (Chinese translations, pricing) |
| **GitHub API** | `https://api.github.com/repos` | Optional token (`GITHUB_TOKEN`) | Repository statistics (stars, forks, language) |
| **GitHub Trending** | `https://github.com/trending` | None (public) | Trending AI repository discovery (HTML scraping) |
| **ArXiv API** | `https://export.arxiv.org/api/query` | None (public) | AI research paper mining (XML feed) |
| **PostgreSQL** | `postgresql+asyncpg://` | Database credentials | Tool data persistence, transaction management |
| **Redis** | `redis://` | Optional password | Celery message broker, task result backend |
| **Meilisearch** | `http://localhost:7700` | API key (`MEILISEARCH_KEY`) | Full-text search indexing with vector search |

## Relationships

### Data Flow Architecture

```mermaid
---
title: Automation Service Data Pipeline Architecture
---
flowchart LR
    subgraph "Discovery Sources"
        PH["Product Hunt API"]
        GH["GitHub Trending"]
        AX["ArXiv API"]
    end

    subgraph "Enrichment"
        DS["DeepSeek LLM"]
        GHC["GitHub API"]
    end

    subgraph "Celery Tasks"
        T1["crawl_and_enrich_daily"]
        T2["crawl_github_trending_daily"]
        T3["mine_arxiv_papers_daily"]
        T4["sync_github_stats"]
        T5["enrich_single_tool"]
        T6["sync_to_meilisearch"]
    end

    subgraph "Persistence"
        PG["PostgreSQL<br/>Tool, Category, Scenario"]
        EMBED["Embedding Service<br/>384-dim vectors"]
    end

    subgraph "Search"
        MEILI["Meilisearch<br/>Full-text + Vector Search"]
    end

    subgraph "Task Queue"
        REDIS["Redis<br/>Broker & Backend"]
    end

    PH -->|GraphQL| T1
    GH -->|HTML Scrape| T2
    AX -->|XML Feed| T3

    T1 -->|Tool data| DS
    T2 -->|Tool data| DS
    T3 -->|Paper data| DS

    T4 -->|Repo URLs| GHC
    T5 -->|Single tool| DS
    T5 -->|GitHub URLs| GHC

    DS -->|name_zh, description_zh, pricing| T1
    DS -->|name_zh, description_zh, pricing| T2
    DS -->|name_zh, description_zh, pricing| T3
    DS -->|name_zh, description_zh, pricing| T5

    GHC -->|stars, forks, language| T4
    GHC -->|stars, forks, language| T5

    T1 -->|Save| PG
    T2 -->|Save| PG
    T3 -->|Save| PG
    T4 -->|Update| PG
    T5 -->|Update| PG

    T1 -->|Trigger| T6
    T2 -->|Trigger| T6
    T3 -->|Trigger| T6
    T4 -->|Trigger| T6
    T5 -->|Trigger| T6

    PG -->|All tools| T6
    T6 -->|Generate| EMBED
    EMBED -->|Vector embeddings| T6
    T6 -->|Upsert documents| MEILI

    T1 -.->|Queue| REDIS
    T2 -.->|Queue| REDIS
    T3 -.->|Queue| REDIS
    T4 -.->|Queue| REDIS
    T5 -.->|Queue| REDIS
    T6 -.->|Queue| REDIS
```

### Celery Beat Scheduler Timeline

```mermaid
---
title: Daily Celery Beat Schedule (UTC)
---
timeline
    title Daily Automation Pipeline Schedule

    section 00:00 UTC
        00:00 : crawl_and_enrich_daily : Product Hunt crawl starts

    section 01:00 UTC
        01:00 : crawl_github_trending_daily : GitHub trending crawl starts

    section 02:00 UTC
        02:00 : mine_arxiv_papers_daily : ArXiv paper mining starts

    section Throughout Day
        Anytime : sync_to_meilisearch : Triggered by above tasks
        Anytime : sync_github_stats : Triggered by tasks or manual call
        Anytime : enrich_single_tool : Manual API endpoint only
```

### Task Dependency Graph

```mermaid
---
title: Celery Task Dependencies and Triggers
---
flowchart TB
    subgraph API["Manual API Triggers"]
        API1["POST /tasks/crawl"]
        API2["POST /tasks/sync-search"]
        API3["POST /tasks/sync-github"]
        API4["POST /tasks/enrich/{tool_id}"]
    end

    subgraph BEAT["Celery Beat Scheduler"]
        BEAT1["Schedule: 00:00 UTC"]
        BEAT2["Schedule: 01:00 UTC"]
        BEAT3["Schedule: 02:00 UTC"]
    end

    subgraph TASKS["Task Execution"]
        T1["crawl_and_enrich_daily"]
        T2["crawl_github_trending_daily"]
        T3["mine_arxiv_papers_daily"]
        T4["sync_github_stats"]
        T5["enrich_single_tool"]
        T6["sync_to_meilisearch"]
    end

    API1 --> T1
    API2 --> T6
    API3 --> T4
    API4 --> T5

    BEAT1 --> T1
    BEAT2 --> T2
    BEAT3 --> T3

    T1 -->|Conditional trigger| T6
    T2 -->|Conditional trigger| T6
    T3 -->|Conditional trigger| T6
    T4 -->|Conditional trigger| T6
    T5 -->|Always triggers| T6

    T1 -->|Database writes| PG["PostgreSQL"]
    T2 -->|Database writes| PG
    T3 -->|Database writes| PG
    T4 -->|Database updates| PG
    T5 -->|Database updates| PG

    T6 -->|Index sync| MEILI["Meilisearch"]
```

### Worker Process Architecture

```mermaid
---
title: Celery Worker Process Initialization and Task Execution
---
classDiagram
    namespace CeleryInfrastructure {
        class CeleryApp {
            <<application>>
            name: automation_tasks
            broker: Redis
            backend: Redis
            task_serializer: json
            +register_task(name, func)
        }

        class WorkerProcess {
            <<process>>
            +init_worker()
            +execute_task()
            -event_loop: asyncio.AbstractEventLoop
            -engine: AsyncEngine
        }

        class TaskScheduler {
            <<service>>
            name: Celery Beat
            -beat_schedule: Dict
            +schedule_task()
        }

        class RedisBackend {
            <<service>>
            role: Message Broker + Result Backend
            +enqueue_task()
            +store_result()
        }
    }

    namespace Tasks {
        class Task {
            <<abstract>>
            name: str
            +execute()
            -async_pipeline(): coroutine
        }

        class CrawlTask {
            name: crawl_and_enrich_daily
            +_crawl_and_enrich_pipeline()
        }

        class GitHubTask {
            name: crawl_github_trending_daily
            +_crawl_github_trending_pipeline()
        }

        class ArXivTask {
            name: mine_arxiv_papers_daily
            +_mine_arxiv_papers_pipeline()
        }

        class SyncGitHubTask {
            name: sync_github_stats
            +_sync_github_stats_pipeline()
        }

        class EnrichTask {
            name: enrich_single_tool
            +_enrich_single_tool_pipeline()
        }

        class MeiliTask {
            name: sync_to_meilisearch
            +_sync_to_meilisearch_pipeline()
        }
    }

    namespace DataAccess {
        class AsyncSessionLocal {
            <<factory>>
            engine: AsyncEngine
            +create_session()
        }

        class SQLAlchemyModels {
            <<orm>>
            +Tool
            +Category
            +Scenario
        }
    }

    CeleryApp -->|manages| WorkerProcess
    CeleryApp -->|registers| Task
    TaskScheduler -->|schedules| Task
    Task -->|executed by| WorkerProcess
    WorkerProcess -->|messages| RedisBackend
    RedisBackend -->|stores| WorkerProcess

    Task <|-- CrawlTask
    Task <|-- GitHubTask
    Task <|-- ArXivTask
    Task <|-- SyncGitHubTask
    Task <|-- EnrichTask
    Task <|-- MeiliTask

    WorkerProcess -->|manages| AsyncSessionLocal
    AsyncSessionLocal -->|ORM| SQLAlchemyModels
```

### Enrichment Pipeline Detail

```mermaid
---
title: Tool Enrichment Pipeline (DeepSeek LLM Enrichment)
---
flowchart TD
    A["Raw Tool Data<br/>name, description/tagline, url"] -->|From PH/GitHub/ArXiv| B["DeepSeekClient<br/>enrich_tool_info"]

    B -->|Prompt| C["DeepSeek LLM API<br/>deepseek-chat model"]

    C -->|JSON Response| D["Enrichment Output"]

    D --> E["name_zh<br/>Chinese Name"]
    D --> F["description_zh<br/>Chinese Description"]
    D --> G["pricing_type<br/>free/freemium/paid"]
    D --> H["tags<br/>Chinese Keywords"]
    D --> I["summary<br/>One-liner"]

    E --> J["Tool Record Creation<br/>with Enriched Data"]
    F --> J
    G --> J

    J --> K["PostgreSQL<br/>Insert/Update"]
```

## Configuration and Environment

### Required Environment Variables

```env
# Celery & Redis
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql+asyncpg://ainav:ainavpassword@localhost:5433/ainav_db

# Search Engine
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=masterKey

# External APIs (required for data sources)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

PRODUCTHUNT_TOKEN=your_producthunt_token
GITHUB_TOKEN=your_github_token  # Optional, but recommended for rate limits

# Application
DEBUG=True
ENVIRONMENT=development
```

### Celery Configuration Details

**Performance Optimizations:**
- `worker_prefetch_multiplier=1` - Prevents worker overloading by fetching one task at a time
- `task_acks_late=True` - Ensures task acknowledgment only after successful completion, preventing task loss on worker crashes
- JSON serialization - Language-agnostic task serialization for distributed workers

**Reliability:**
- Redis backend for both message broker and result storage
- Signal handler for worker initialization ensures clean database connections
- AsyncIO event loop management per worker process

## Notes

### Data Quality and Filtering

1. **Product Hunt**: Filters tools with `votesCount > 100` to ensure quality
2. **GitHub Trending**: Filters by AI keywords ("ai", "llm", "gpt", "model", "inference", "agent", "rag", "intelligence", "transformer")
3. **ArXiv**: Queries `cs.AI` category for computer science AI papers
4. **Duplicate Prevention**: Checks existing slugs before creating new Tool records

### Async/Await Pattern

All tasks follow the wrapper pattern:
```python
@celery_app.task(name="task_name")
def task_wrapper():
    return asyncio.run(_async_pipeline())

async def _async_pipeline():
    # Async implementation
    pass
```

This is necessary because Celery workers run synchronously but the application uses async/await for I/O operations.

### Vector Embeddings

The `sync_to_meilisearch` task:
- Generates 384-dimensional embeddings for each tool
- Combines: name, name_zh, description, description_zh
- Stores in Meilisearch `_vectors` field
- Enables hybrid search: full-text + semantic vector search

### Error Handling

All clients implement try-except with logging:
- API failures are logged and return `None` or empty lists
- Tasks gracefully handle missing data (no tools found, failed enrichments)
- Database commits are atomic

### Execution Order

Designed staggered execution (00:00, 01:00, 02:00 UTC) to:
- Prevent simultaneous load on database
- Avoid rate limiting on external APIs
- Distribute computational load
