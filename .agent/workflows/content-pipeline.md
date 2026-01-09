---
name: content-pipeline
description: Workflow for content automation pipeline
triggers:
  - "/workflow content-pipeline"
  - "content automation"
  - "process crawled content"
---

# Content Pipeline Workflow

内容自动化管线的运维流程。

## Pipeline Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│   Sources   │───▶│  Ingestion   │───▶│ Enrichment  │───▶│  Review  │───▶ Publish
│ PH/GH/ArXiv │    │    Queue     │    │   (LLM)     │    │  Queue   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
```

## Phase 1: Source Monitoring

### 1.1 Check Crawler Status
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# Check Celery workers
celery -A app.workers inspect active

# Check scheduled tasks
celery -A app.workers inspect scheduled

# Check task results
celery -A app.workers inspect stats
```

### 1.2 Manual Trigger
```bash
# Trigger specific crawler
celery -A app.workers call app.workers.crawlers.crawl_producthunt
celery -A app.workers call app.workers.crawlers.crawl_github_trending
celery -A app.workers call app.workers.crawlers.fetch_arxiv_papers

# Trigger all crawlers
python -m app.scripts.run_all_crawlers
```

### 1.3 Monitor Crawler Logs
```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# Or if running locally
celery -A app.workers worker --loglevel=info
```

## Phase 2: Ingestion Queue Management

### 2.1 Check Queue Status
```bash
# View pending items
python -m app.scripts.check_ingestion_queue

# Output example:
# Pending: 45 items
# Processing: 3 items
# Failed: 2 items
# Completed today: 127 items
```

### 2.2 Queue Operations
```python
# app/scripts/queue_operations.py
from app.services.ingestion_service import IngestionService

# Get pending items
pending = await IngestionService.get_pending(limit=100)

# Retry failed items
await IngestionService.retry_failed()

# Clear old completed items
await IngestionService.cleanup(days_old=30)

# Prioritize specific item
await IngestionService.set_priority(item_id, priority=100)
```

### 2.3 Handle Failed Items
```bash
# List failed items
python -m app.scripts.list_failed_ingestions

# Retry specific item
python -m app.scripts.retry_ingestion --id "uuid"

# Retry all failed
python -m app.scripts.retry_all_failed

# Mark as skipped
python -m app.scripts.skip_ingestion --id "uuid" --reason "Duplicate"
```

## Phase 3: Enrichment Processing

### 3.1 LLM Content Generation
```python
# Enrichment tasks
from app.workers.tasks import (
    generate_chinese_description,
    generate_feature_summary,
    generate_use_case_suggestions,
    generate_comparison_notes,
)

# Trigger enrichment for new tool
celery -A app.workers call app.workers.tasks.enrich_tool --args='["tool-uuid"]'
```

### 3.2 Screenshot Generation
```bash
# Generate pending screenshots
celery -A app.workers call app.workers.tasks.generate_pending_screenshots

# Generate for specific tool
python -m app.scripts.generate_screenshot --tool-id "uuid"

# Batch generate
python -m app.scripts.generate_screenshots --limit 50
```

### 3.3 Embedding Generation
```bash
# Generate embeddings for tools without them
celery -A app.workers call app.workers.tasks.generate_missing_embeddings

# Regenerate all embeddings (careful - expensive)
python -m app.scripts.regenerate_embeddings --confirm
```

### 3.4 Accessibility Check
```bash
# Check China accessibility for pending tools
celery -A app.workers call app.workers.tasks.check_china_accessibility

# Check specific tool
python -m app.scripts.check_accessibility --url "https://tool.com"
```

## Phase 4: Quality Scoring

### 4.1 Auto Scoring
```python
# Quality score calculation
def calculate_quality_score(tool: Tool) -> int:
    score = 0

    # Content completeness (40 points)
    if tool.description and len(tool.description) > 100:
        score += 20
    if tool.name_zh:
        score += 10
    if tool.features and len(tool.features) >= 3:
        score += 10

    # Data quality (30 points)
    if tool.screenshot_url:
        score += 15
    if tool.embedding is not None:
        score += 15

    # Verification (30 points)
    if tool.url_verified:
        score += 15
    if tool.china_accessibility_verified:
        score += 15

    return score
```

### 4.2 Manual Quality Review
```bash
# List tools needing review
python -m app.scripts.list_review_queue

# Approve tool
python -m app.scripts.approve_tool --id "uuid"

# Reject tool
python -m app.scripts.reject_tool --id "uuid" --reason "Low quality content"

# Request re-enrichment
python -m app.scripts.request_reenrichment --id "uuid"
```

## Phase 5: Publication

### 5.1 Publish Approved Tools
```bash
# Publish all approved tools
python -m app.scripts.publish_approved

# Publish specific tool
python -m app.scripts.publish_tool --id "uuid"
```

### 5.2 Update Search Index
```bash
# Sync to Meilisearch
python -m app.scripts.sync_search_index

# Full reindex (use sparingly)
python -m app.scripts.reindex_search --full
```

### 5.3 Clear CDN Cache
```bash
# Invalidate tool pages
python -m app.scripts.invalidate_cdn --pattern "/tools/*"

# Invalidate specific tool
python -m app.scripts.invalidate_cdn --path "/tools/tool-slug"
```

## Monitoring & Alerts

### 6.1 Pipeline Metrics
```bash
# View pipeline metrics
python -m app.scripts.pipeline_metrics

# Output:
# ┌─────────────────────────────────────────┐
# │ Content Pipeline Status                 │
# ├─────────────────────────────────────────┤
# │ Crawled (24h):        156               │
# │ Enriched (24h):       142               │
# │ Published (24h):      128               │
# │ Failed (24h):         8                 │
# │ Queue Length:         23                │
# │ Avg Processing Time:  45.2s             │
# └─────────────────────────────────────────┘
```

### 6.2 Alert Thresholds
```yaml
alerts:
  - name: queue_backlog
    condition: queue_length > 100
    severity: warning

  - name: high_failure_rate
    condition: failure_rate > 10%
    severity: critical

  - name: crawler_stalled
    condition: no_new_items_in_hours > 24
    severity: warning

  - name: enrichment_slow
    condition: avg_processing_time > 120s
    severity: warning
```

### 6.3 Grafana Dashboard
```
Key Panels:
1. Items Processed (24h trend)
2. Queue Length Over Time
3. Failure Rate by Source
4. Processing Time Distribution
5. Quality Score Distribution
6. Publication Rate
```

## Troubleshooting

### Crawler Not Running
```bash
# Check Celery Beat
docker-compose logs celery-beat

# Restart Celery services
docker-compose restart celery-worker celery-beat
```

### LLM API Errors
```bash
# Check API quota
python -m app.scripts.check_llm_quota

# Fallback to basic enrichment
python -m app.scripts.basic_enrich --tool-id "uuid"
```

### Screenshot Failures
```bash
# Check Playwright
python -m playwright install chromium

# Test screenshot manually
python -m app.scripts.test_screenshot --url "https://example.com"
```

### Embedding Generation Slow
```bash
# Check GPU availability
nvidia-smi

# Use batch processing
python -m app.scripts.batch_embeddings --batch-size 32
```
