---
name: content-automation
description: Content automation and crawling skill
triggers:
  - "crawler"
  - "content automation"
  - "scraping"
  - "enrichment"
---

# Content Automation Skill

内容自动化技能配置。

## Tech Stack
- **Task Queue:** Celery 5+
- **Browser:** Playwright
- **LLM:** DeepSeek API
- **Embeddings:** BGE-M3

## Celery Configuration
```python
# app/workers/celeryconfig.py
from celery import Celery
from celery.schedules import crontab

app = Celery('ainav')

app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/1',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_routes={
        'app.workers.crawlers.*': {'queue': 'crawlers'},
        'app.workers.enrichment.*': {'queue': 'enrichment'},
        'app.workers.screenshots.*': {'queue': 'screenshots'},
    },
)

app.conf.beat_schedule = {
    'crawl-producthunt-daily': {
        'task': 'app.workers.crawlers.crawl_producthunt',
        'schedule': crontab(hour=8, minute=0),
    },
    'crawl-github-twice-daily': {
        'task': 'app.workers.crawlers.crawl_github_trending',
        'schedule': crontab(hour='*/12', minute=0),
    },
    'fetch-arxiv-daily': {
        'task': 'app.workers.crawlers.fetch_arxiv_papers',
        'schedule': crontab(hour=6, minute=0),
    },
    'generate-pending-screenshots': {
        'task': 'app.workers.screenshots.generate_pending',
        'schedule': crontab(minute='*/30'),
    },
}
```

## Product Hunt Crawler
```python
# app/workers/crawlers/producthunt.py
import httpx
from celery import shared_task

PRODUCTHUNT_API = "https://api.producthunt.com/v2/api/graphql"

QUERY = """
query {
  posts(first: 50, topic: "artificial-intelligence", order: VOTES) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        topics { edges { node { name } } }
        thumbnail { url }
        createdAt
      }
    }
  }
}
"""


@shared_task(bind=True, max_retries=3)
def crawl_producthunt(self):
    """Crawl Product Hunt AI products"""
    try:
        headers = {
            "Authorization": f"Bearer {settings.PRODUCTHUNT_TOKEN}",
            "Content-Type": "application/json",
        }

        response = httpx.post(
            PRODUCTHUNT_API,
            json={"query": QUERY},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        posts = data["data"]["posts"]["edges"]

        for edge in posts:
            post = edge["node"]
            # Queue for processing
            process_producthunt_post.delay(post)

        return {"status": "success", "count": len(posts)}

    except Exception as e:
        self.retry(countdown=60, exc=e)


@shared_task
def process_producthunt_post(post: dict):
    """Process individual Product Hunt post"""
    # Check if already exists
    # Add to ingestion queue
    # Trigger enrichment
    pass
```

## GitHub Trending Crawler
```python
# app/workers/crawlers/github.py
from bs4 import BeautifulSoup
import httpx
from celery import shared_task

AI_KEYWORDS = [
    "ai", "artificial-intelligence", "machine-learning",
    "llm", "gpt", "chatgpt", "openai", "anthropic",
    "stable-diffusion", "generative-ai", "deep-learning",
]


@shared_task(bind=True, max_retries=3)
def crawl_github_trending(self):
    """Crawl GitHub trending repositories"""
    try:
        url = "https://github.com/trending?spoken_language_code=zh"
        response = httpx.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        repos = soup.select("article.Box-row")

        ai_repos = []
        for repo in repos:
            name = repo.select_one("h2 a").text.strip()
            description = repo.select_one("p")
            description = description.text.strip() if description else ""

            # Filter AI-related
            combined = f"{name} {description}".lower()
            if any(kw in combined for kw in AI_KEYWORDS):
                ai_repos.append({
                    "name": name,
                    "description": description,
                    "url": f"https://github.com/{name.replace(' ', '')}",
                })

        for repo in ai_repos:
            process_github_repo.delay(repo)

        return {"status": "success", "count": len(ai_repos)}

    except Exception as e:
        self.retry(countdown=60, exc=e)
```

## Screenshot Generator
```python
# app/workers/screenshots/generator.py
from playwright.async_api import async_playwright
from celery import shared_task
import asyncio

@shared_task(bind=True, max_retries=2)
def generate_screenshot(self, url: str, tool_id: str):
    """Generate screenshot for a tool"""
    try:
        return asyncio.get_event_loop().run_until_complete(
            _generate_screenshot_async(url, tool_id)
        )
    except Exception as e:
        self.retry(countdown=120, exc=e)


async def _generate_screenshot_async(url: str, tool_id: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for animations

            # Remove cookie banners
            await page.evaluate("""
                document.querySelectorAll('[class*="cookie"], [class*="consent"]')
                    .forEach(el => el.remove());
            """)

            # Take screenshot
            screenshot_path = f"/tmp/screenshots/{tool_id}.png"
            await page.screenshot(path=screenshot_path, full_page=False)

            # Upload to CDN
            cdn_url = await upload_to_cdn(screenshot_path)

            return {"status": "success", "url": cdn_url}

        finally:
            await browser.close()
```

## LLM Content Enrichment
```python
# app/workers/enrichment/llm.py
import httpx
from celery import shared_task

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"


@shared_task(bind=True, max_retries=2)
def generate_chinese_description(self, tool_data: dict) -> dict:
    """Generate Chinese description using DeepSeek"""
    try:
        prompt = f"""请为以下AI工具生成一段中文介绍（200-500字）：

工具名称：{tool_data['name']}
英文介绍：{tool_data.get('description', '')}
官网：{tool_data['url']}

要求：
1. 使用专业但易懂的中文
2. 突出工具的核心功能和使用场景
3. 提及定价模式（如果已知）
4. 适合中国用户阅读

请直接输出中文介绍，不要有其他内容。"""

        response = httpx.post(
            DEEPSEEK_API,
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            timeout=60,
        )
        response.raise_for_status()

        description = response.json()["choices"][0]["message"]["content"]

        return {"status": "success", "description": description}

    except Exception as e:
        self.retry(countdown=30, exc=e)
```

## Embedding Generator
```python
# app/workers/enrichment/embeddings.py
from sentence_transformers import SentenceTransformer
from celery import shared_task
import numpy as np

model = SentenceTransformer('BAAI/bge-m3')


@shared_task
def generate_embedding(tool_id: str, text: str) -> dict:
    """Generate BGE-M3 embedding for tool"""
    # Combine relevant text
    embedding = model.encode(text, normalize_embeddings=True)

    # Store in database
    with SessionLocal() as db:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if tool:
            tool.embedding = embedding.tolist()
            db.commit()

    return {"status": "success", "dimensions": len(embedding)}


@shared_task
def batch_generate_embeddings(tool_ids: list[str]):
    """Batch generate embeddings for multiple tools"""
    with SessionLocal() as db:
        tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all()

        texts = [
            f"{t.name} {t.name_zh or ''} {t.description or ''}"
            for t in tools
        ]

        embeddings = model.encode(texts, normalize_embeddings=True)

        for tool, embedding in zip(tools, embeddings):
            tool.embedding = embedding.tolist()

        db.commit()

    return {"status": "success", "count": len(tools)}
```

## China Accessibility Checker
```python
# app/workers/enrichment/accessibility.py
import httpx
from celery import shared_task

CHINA_PROXY = "http://china-proxy:8080"


@shared_task(bind=True, max_retries=2)
def check_china_accessibility(self, url: str) -> dict:
    """Check if URL is accessible from China"""
    try:
        # Test from China proxy
        response = httpx.get(
            url,
            proxies={"http://": CHINA_PROXY, "https://": CHINA_PROXY},
            timeout=15,
            follow_redirects=True,
        )

        if response.status_code == 200:
            return {
                "accessible": True,
                "method": "direct",
                "response_time": response.elapsed.total_seconds(),
            }
        else:
            return {
                "accessible": False,
                "method": "none",
                "status_code": response.status_code,
            }

    except httpx.TimeoutException:
        return {"accessible": False, "method": "proxy", "reason": "timeout"}
    except httpx.ConnectError:
        return {"accessible": False, "method": "vpn", "reason": "blocked"}
    except Exception as e:
        self.retry(countdown=60, exc=e)
```
