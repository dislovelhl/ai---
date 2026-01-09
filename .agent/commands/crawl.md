---
name: crawl
description: Content crawling and ingestion
usage: /crawl <source>
args:
  - name: source
    description: "producthunt | github | arxiv | all | status"
    required: true
---

# Crawl Command

内容爬取和入库操作。

## Usage

```bash
/crawl producthunt  # 爬取Product Hunt
/crawl github       # 爬取GitHub Trending
/crawl arxiv        # 爬取ArXiv论文
/crawl all          # 爬取所有来源
/crawl status       # 查看爬取状态
```

## Actions

### Product Hunt Crawler
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# Run crawler
celery -A app.workers call app.workers.crawlers.crawl_producthunt

# Or directly
python -m app.workers.crawlers.producthunt
```

**Product Hunt GraphQL Query:**
```graphql
query {
  posts(first: 50, topic: "artificial-intelligence") {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        topics { name }
        thumbnail { url }
      }
    }
  }
}
```

### GitHub Trending Crawler
```bash
# Run crawler
celery -A app.workers call app.workers.crawlers.crawl_github_trending

# Filter AI projects only
python -m app.workers.crawlers.github --filter-ai
```

**GitHub Topics:**
- artificial-intelligence
- machine-learning
- llm
- chatgpt
- generative-ai
- stable-diffusion

### ArXiv Paper Fetcher
```bash
# Fetch recent papers
celery -A app.workers call app.workers.crawlers.fetch_arxiv_papers

# Specific categories
python -m app.workers.crawlers.arxiv --categories cs.AI,cs.LG,cs.CL
```

**ArXiv Categories:**
- cs.AI - Artificial Intelligence
- cs.LG - Machine Learning
- cs.CL - Computation and Language
- cs.CV - Computer Vision

### Check Crawl Status
```bash
# Celery task status
celery -A app.workers inspect active

# Queue status
celery -A app.workers inspect stats

# Check ingestion queue
python -m app.scripts.check_ingestion_queue
```

## Crawl Schedule (Celery Beat)

```python
# app/workers/celeryconfig.py
beat_schedule = {
    'crawl-producthunt-daily': {
        'task': 'app.workers.crawlers.crawl_producthunt',
        'schedule': crontab(hour=8, minute=0),  # 每天8点
    },
    'crawl-github-twice-daily': {
        'task': 'app.workers.crawlers.crawl_github_trending',
        'schedule': crontab(hour='*/12'),  # 每12小时
    },
    'fetch-arxiv-daily': {
        'task': 'app.workers.crawlers.fetch_arxiv_papers',
        'schedule': crontab(hour=6, minute=0),  # 每天6点
    },
}
```

## Manual Tool Addition

```bash
# Add single tool
python -m app.scripts.add_tool \
  --name "Claude" \
  --url "https://claude.ai" \
  --category "AI Assistant" \
  --pricing "freemium"

# Bulk import from JSON
python -m app.scripts.import_tools --file tools.json
```

## Quality Check

After crawling, run quality checks:
```bash
# Check for duplicates
python -m app.scripts.check_duplicates

# Verify URLs are accessible
python -m app.scripts.verify_tool_urls

# Generate screenshots for new tools
celery -A app.workers call app.workers.tasks.generate_pending_screenshots
```
