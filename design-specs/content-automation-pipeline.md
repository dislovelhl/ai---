# AI Navigator Platform - Content Automation Pipeline

> Version: 1.0.0
> Created: 2026-01-09
> Purpose: Automated AI Tool Discovery & Content Enrichment

---

## 1. Pipeline Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CONTENT AUTOMATION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Product     │  │   GitHub    │  │   ArXiv     │  │    RSS      │             │
│  │ Hunt API    │  │  Trending   │  │    API      │  │   Feeds     │             │
│  │             │  │             │  │             │  │             │             │
│  │ Daily       │  │ Every 6h   │  │ Daily       │  │ Hourly      │             │
│  │ AI Category │  │ Python/ML   │  │ cs.AI/CL    │  │ Tech News   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                │                    │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION LAYER                                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         Celery Task Queue                                    │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │ │
│  │  │ ph_crawler    │  │ gh_scraper    │  │ arxiv_fetcher │                   │ │
│  │  │ Priority: Low │  │ Priority: Low │  │ Priority: Med │                   │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘                   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Deduplication Engine                                  │ │
│  │  • URL normalization                                                         │ │
│  │  • Fuzzy name matching                                                       │ │
│  │  • Domain detection                                                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
└────────────────────────────────────┼──────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          ENRICHMENT LAYER                                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Screenshot     │  │  LLM Content    │  │  Embedding      │                   │
│  │  Generator      │  │  Generator      │  │  Generator      │                   │
│  │  (Playwright)   │  │  (DeepSeek)     │  │  (BGE-M3)       │                   │
│  │                 │  │                 │  │                 │                   │
│  │ • Full page     │  │ • CN tagline    │  │ • Tool desc     │                   │
│  │ • Thumbnail     │  │ • CN description│  │ • 384-dim vector│                   │
│  │ • Logo extract  │  │ • Category      │  │ • Similarity    │                   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │
│                                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Pricing        │  │  Access         │  │  Quality        │                   │
│  │  Detector       │  │  Checker        │  │  Scorer         │                   │
│  │                 │  │                 │  │                 │                   │
│  │ • Pricing page  │  │ • China ping    │  │ • Completeness  │                   │
│  │ • Free tier     │  │ • VPN required  │  │ • Uniqueness    │                   │
│  │ • API pricing   │  │ • Login check   │  │ • Popularity    │                   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │
│                                                                                   │
└────────────────────────────────────┼──────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           REVIEW LAYER                                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         Admin Dashboard                                      │ │
│  │                                                                              │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │ │
│  │  │  Pending Review Queue                                                 │   │ │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐ │   │ │
│  │  │  │ Tool: "AI Video Generator"                                      │ │   │ │
│  │  │  │ Source: Product Hunt  │  Score: 85/100  │  Status: Pending     │ │   │ │
│  │  │  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────────┐│ │   │ │
│  │  │  │ │ Approve │ │ Reject  │ │  Edit   │ │ Request More Info       ││ │   │ │
│  │  │  │ └─────────┘ └─────────┘ └─────────┘ └─────────────────────────┘│ │   │ │
│  │  │  └─────────────────────────────────────────────────────────────────┘ │   │ │
│  │  └──────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
└────────────────────────────────────┼──────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          PUBLICATION LAYER                                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  PostgreSQL     │  │  Meilisearch    │  │  CDN Cache      │                   │
│  │  Update         │  │  Index          │  │  Invalidate     │                   │
│  │                 │  │                 │  │                 │                   │
│  │ • Insert tool   │  │ • Update index  │  │ • Purge old     │                   │
│  │ • Update stats  │  │ • Sync vectors  │  │ • Warm new      │                   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                   │
│                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Source Crawlers

### 2.1 Product Hunt Crawler

```python
# services/automation-service/app/workers/producthunt.py

import httpx
from datetime import datetime, timedelta
from celery import shared_task
from app.models import IngestionQueue
from app.db import async_session

PRODUCTHUNT_API_URL = "https://api.producthunt.com/v2/api/graphql"

QUERY = """
query GetAIProducts($postedAfter: DateTime!, $first: Int!) {
  posts(
    first: $first,
    postedAfter: $postedAfter,
    topic: "artificial-intelligence"
  ) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        website
        thumbnail {
          url
        }
        votesCount
        topics {
          edges {
            node {
              name
            }
          }
        }
        makers {
          name
        }
        createdAt
      }
    }
  }
}
"""

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
async def crawl_producthunt(self, days_back: int = 1, min_votes: int = 50):
    """
    Crawl Product Hunt for new AI tools.

    Args:
        days_back: How many days back to search
        min_votes: Minimum votes threshold for inclusion
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PRODUCTHUNT_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.PRODUCTHUNT_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": QUERY,
                    "variables": {
                        "postedAfter": (datetime.utcnow() - timedelta(days=days_back)).isoformat(),
                        "first": 50,
                    }
                }
            )
            response.raise_for_status()
            data = response.json()

        products = data.get("data", {}).get("posts", {}).get("edges", [])

        ingested_count = 0
        async with async_session() as session:
            for edge in products:
                product = edge["node"]

                # Filter by votes
                if product["votesCount"] < min_votes:
                    continue

                # Check if already exists
                existing = await session.execute(
                    select(IngestionQueue).where(
                        IngestionQueue.source == "producthunt",
                        IngestionQueue.source_id == product["id"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Create ingestion record
                ingestion = IngestionQueue(
                    source="producthunt",
                    source_id=product["id"],
                    source_url=product["website"] or product["url"],
                    raw_data={
                        "name": product["name"],
                        "tagline": product["tagline"],
                        "description": product["description"],
                        "thumbnail_url": product.get("thumbnail", {}).get("url"),
                        "votes": product["votesCount"],
                        "topics": [t["node"]["name"] for t in product.get("topics", {}).get("edges", [])],
                        "makers": [m["name"] for m in product.get("makers", [])],
                    },
                    status="pending",
                    discovered_at=datetime.utcnow(),
                )
                session.add(ingestion)
                ingested_count += 1

            await session.commit()

        return {"ingested": ingested_count, "source": "producthunt"}

    except Exception as e:
        self.retry(exc=e)
```

### 2.2 GitHub Trending Scraper

```python
# services/automation-service/app/workers/github.py

import httpx
from bs4 import BeautifulSoup
from celery import shared_task
from app.models import IngestionQueue

GITHUB_TRENDING_URL = "https://github.com/trending/{language}?since=daily"
LANGUAGES = ["python", "javascript", "typescript"]
AI_KEYWORDS = [
    "llm", "gpt", "ai", "ml", "machine-learning", "deep-learning",
    "neural", "transformer", "agent", "rag", "embedding", "chatbot",
    "diffusion", "stable-diffusion", "langchain", "openai"
]

@shared_task(bind=True, max_retries=3)
async def scrape_github_trending(self, min_stars: int = 100):
    """
    Scrape GitHub Trending for AI-related repositories.
    """
    try:
        async with httpx.AsyncClient() as client:
            all_repos = []

            for language in LANGUAGES:
                response = await client.get(
                    GITHUB_TRENDING_URL.format(language=language),
                    headers={"User-Agent": "AINav Bot/1.0"}
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                repo_elements = soup.select("article.Box-row")

                for elem in repo_elements:
                    # Extract repo info
                    repo_link = elem.select_one("h2 a")
                    if not repo_link:
                        continue

                    repo_path = repo_link.get("href", "").strip("/")
                    repo_name = repo_path.split("/")[-1] if "/" in repo_path else repo_path

                    # Extract description
                    desc_elem = elem.select_one("p.col-9")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # Extract stars
                    stars_elem = elem.select_one("a[href$='/stargazers']")
                    stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
                    stars = parse_stars(stars_text)

                    # Filter by stars and AI keywords
                    if stars < min_stars:
                        continue

                    text_to_check = f"{repo_name} {description}".lower()
                    if not any(kw in text_to_check for kw in AI_KEYWORDS):
                        continue

                    all_repos.append({
                        "repo_path": repo_path,
                        "name": repo_name,
                        "description": description,
                        "stars": stars,
                        "language": language,
                        "url": f"https://github.com/{repo_path}",
                    })

        # Fetch additional info via GitHub API
        ingested_count = 0
        async with async_session() as session:
            for repo in all_repos:
                # Check for duplicates
                existing = await session.execute(
                    select(IngestionQueue).where(
                        IngestionQueue.source == "github",
                        IngestionQueue.source_id == repo["repo_path"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Get full repo info from API
                repo_info = await fetch_github_repo_info(repo["repo_path"])

                ingestion = IngestionQueue(
                    source="github",
                    source_id=repo["repo_path"],
                    source_url=repo["url"],
                    raw_data={
                        **repo,
                        "readme_url": f"https://raw.githubusercontent.com/{repo['repo_path']}/main/README.md",
                        "topics": repo_info.get("topics", []),
                        "homepage": repo_info.get("homepage"),
                        "license": repo_info.get("license", {}).get("spdx_id"),
                    },
                    status="pending",
                    discovered_at=datetime.utcnow(),
                )
                session.add(ingestion)
                ingested_count += 1

            await session.commit()

        return {"ingested": ingested_count, "source": "github"}

    except Exception as e:
        self.retry(exc=e)


def parse_stars(stars_text: str) -> int:
    """Parse stars text like '1.2k' to integer."""
    stars_text = stars_text.strip().replace(",", "")
    if "k" in stars_text.lower():
        return int(float(stars_text.lower().replace("k", "")) * 1000)
    return int(stars_text) if stars_text.isdigit() else 0


async def fetch_github_repo_info(repo_path: str) -> dict:
    """Fetch detailed repo info from GitHub API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo_path}",
            headers={
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
        )
        if response.status_code == 200:
            return response.json()
        return {}
```

### 2.3 ArXiv Paper Fetcher

```python
# services/automation-service/app/workers/arxiv.py

import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from celery import shared_task
from app.models import ArxivPaper
from app.services.llm import generate_paper_summary

ARXIV_API_URL = "http://export.arxiv.org/api/query"
CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV"]

@shared_task(bind=True, max_retries=3)
async def fetch_arxiv_papers(self, days_back: int = 1, max_results: int = 50):
    """
    Fetch recent papers from ArXiv in AI categories.
    """
    try:
        # Build date range query
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=days_back)

        papers_fetched = 0

        for category in CATEGORIES:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    ARXIV_API_URL,
                    params={
                        "search_query": f"cat:{category}",
                        "start": 0,
                        "max_results": max_results,
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                    }
                )
                response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            async with async_session() as session:
                for entry in root.findall("atom:entry", ns):
                    arxiv_id = extract_arxiv_id(entry.find("atom:id", ns).text)

                    # Check if already exists
                    existing = await session.execute(
                        select(ArxivPaper).where(ArxivPaper.arxiv_id == arxiv_id)
                    )
                    if existing.scalar_one_or_none():
                        continue

                    title = entry.find("atom:title", ns).text.strip()
                    abstract = entry.find("atom:summary", ns).text.strip()
                    authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
                    categories = [c.get("term") for c in entry.findall("atom:category", ns)]
                    published = entry.find("atom:published", ns).text
                    pdf_link = next(
                        (l.get("href") for l in entry.findall("atom:link", ns) if l.get("title") == "pdf"),
                        f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    )

                    paper = ArxivPaper(
                        arxiv_id=arxiv_id,
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        categories=categories,
                        pdf_url=pdf_link,
                        submitted_date=datetime.fromisoformat(published.replace("Z", "+00:00")).date(),
                        is_processed=False,
                        is_published=False,
                    )
                    session.add(paper)
                    papers_fetched += 1

                await session.commit()

        # Queue papers for LLM processing
        await enqueue_paper_processing.delay()

        return {"fetched": papers_fetched, "source": "arxiv"}

    except Exception as e:
        self.retry(exc=e)


@shared_task
async def process_paper_with_llm(paper_id: str):
    """
    Process paper with LLM to generate summary and translations.
    """
    async with async_session() as session:
        paper = await session.get(ArxivPaper, paper_id)
        if not paper or paper.is_processed:
            return

        # Generate summary using DeepSeek
        prompt = f"""请分析以下学术论文，并提供：
1. 中文标题翻译
2. 100字以内的中文摘要
3. 3个核心发现（要点）
4. 2-3个实际应用场景

论文标题: {paper.title}
论文摘要: {paper.abstract}
"""

        result = await generate_paper_summary(prompt)

        paper.title_cn = result.get("title_cn")
        paper.abstract_cn = result.get("abstract_cn")
        paper.summary_cn = result.get("summary_cn")
        paper.key_findings = result.get("key_findings", [])
        paper.practical_applications = result.get("practical_applications", [])
        paper.is_processed = True

        await session.commit()


def extract_arxiv_id(url: str) -> str:
    """Extract ArXiv ID from URL."""
    # http://arxiv.org/abs/2401.12345v1 -> 2401.12345
    import re
    match = re.search(r"(\d{4}\.\d{4,5})", url)
    return match.group(1) if match else url.split("/")[-1]
```

---

## 3. Content Enrichment Services

### 3.1 Screenshot Generator

```python
# services/automation-service/app/workers/screenshot.py

from playwright.async_api import async_playwright
from celery import shared_task
from app.storage import upload_to_oss
import asyncio

@shared_task(bind=True, max_retries=2)
async def generate_screenshot(self, url: str, tool_slug: str):
    """
    Generate screenshot and thumbnail for a tool's website.

    Returns:
        dict: URLs of generated images
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
            )
            page = await context.new_page()

            # Navigate with timeout
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for content to load
            await asyncio.sleep(2)

            # Close any popups/modals
            await close_popups(page)

            # Take full page screenshot
            screenshot_bytes = await page.screenshot(
                full_page=False,
                type="webp",
                quality=85,
            )

            # Generate thumbnail (smaller size)
            await page.set_viewport_size({"width": 800, "height": 600})
            thumbnail_bytes = await page.screenshot(
                type="webp",
                quality=80,
            )

            await browser.close()

        # Upload to OSS
        screenshot_url = await upload_to_oss(
            screenshot_bytes,
            f"screenshots/{tool_slug}/full.webp",
            content_type="image/webp"
        )

        thumbnail_url = await upload_to_oss(
            thumbnail_bytes,
            f"screenshots/{tool_slug}/thumb.webp",
            content_type="image/webp"
        )

        return {
            "screenshot_url": screenshot_url,
            "thumbnail_url": thumbnail_url,
        }

    except Exception as e:
        self.retry(exc=e, countdown=60)


async def close_popups(page):
    """Attempt to close common popup patterns."""
    popup_selectors = [
        '[aria-label="Close"]',
        '[data-testid="close-button"]',
        '.modal-close',
        '.popup-close',
        'button:has-text("Accept")',
        'button:has-text("Got it")',
        'button:has-text("OK")',
    ]

    for selector in popup_selectors:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                await element.click()
                await asyncio.sleep(0.5)
        except:
            pass
```

### 3.2 LLM Content Generator

```python
# services/automation-service/app/services/llm.py

import httpx
from typing import Optional

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def generate_tool_content(
    name: str,
    tagline: str,
    description: str,
    website_url: str,
) -> dict:
    """
    Generate Chinese content and classifications for a tool using DeepSeek.
    """
    prompt = f"""你是一个AI工具专家。请分析以下AI工具信息，并提供结构化的中文内容。

工具名称: {name}
英文简介: {tagline}
英文描述: {description}
官网: {website_url}

请以JSON格式返回以下信息：
1. tagline_cn: 一句话中文介绍（15字以内）
2. description_cn: 中文详细描述（100-150字）
3. suggested_category: 建议的分类（text-generation/image-generation/video-generation/audio-speech/coding-dev/productivity/research/design/education/business 中选一个）
4. suggested_scenarios: 适用场景数组（如：["写周报", "AI写代码"]）
5. suggested_tags: 推荐标签数组（如：["大模型", "免费", "国产"]）
6. pricing_type: 定价类型（free/freemium/paid/beta_free/open_source）
7. pricing_analysis: 定价分析说明

只返回JSON，不要其他文字。"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=60.0,
        )
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return json.loads(content)


async def generate_paper_summary(prompt: str) -> dict:
    """Generate paper summary using DeepSeek."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=90.0,
        )
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return json.loads(content)
```

### 3.3 Embedding Generator

```python
# services/automation-service/app/services/embedding.py

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

# Use BGE-M3 for multilingual embeddings (Chinese + English)
model = SentenceTransformer("BAAI/bge-m3")

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        List of 384-dimensional embedding vectors
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.tolist()


def generate_tool_embedding(
    name: str,
    name_cn: str = None,
    tagline: str = None,
    tagline_cn: str = None,
    description: str = None,
    description_cn: str = None,
    tags: List[str] = None,
) -> List[float]:
    """
    Generate a combined embedding for a tool using all available text.
    """
    # Combine all text with weights
    text_parts = []

    # Names (high weight)
    if name:
        text_parts.extend([name] * 2)
    if name_cn:
        text_parts.extend([name_cn] * 2)

    # Taglines
    if tagline:
        text_parts.append(tagline)
    if tagline_cn:
        text_parts.append(tagline_cn)

    # Descriptions
    if description:
        text_parts.append(description[:500])  # Limit length
    if description_cn:
        text_parts.append(description_cn[:500])

    # Tags
    if tags:
        text_parts.extend(tags)

    combined_text = " ".join(text_parts)

    embedding = model.encode(
        combined_text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


async def find_similar_tools(
    query_embedding: List[float],
    limit: int = 10,
    exclude_ids: List[str] = None,
) -> List[dict]:
    """
    Find similar tools using vector similarity search.
    """
    async with async_session() as session:
        # Use pgvector for similarity search
        query = """
            SELECT id, slug, name, name_cn,
                   1 - (embedding <=> $1::vector) as similarity
            FROM tools
            WHERE status = 'published'
            AND ($2::uuid[] IS NULL OR id != ALL($2))
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """

        result = await session.execute(
            text(query),
            {
                "$1": query_embedding,
                "$2": exclude_ids,
                "$3": limit,
            }
        )

        return [
            {
                "id": row.id,
                "slug": row.slug,
                "name": row.name,
                "name_cn": row.name_cn,
                "similarity": row.similarity,
            }
            for row in result
        ]
```

### 3.4 Access Checker

```python
# services/automation-service/app/workers/access_checker.py

import httpx
import asyncio
from celery import shared_task

CHINA_TEST_SERVERS = [
    "https://api.chinaz.com/",  # China-based ping service
]

@shared_task(bind=True)
async def check_china_accessibility(self, url: str, timeout: int = 10):
    """
    Check if a URL is accessible from China without VPN.

    Returns:
        dict: Accessibility status and details
    """
    results = {
        "is_accessible": False,
        "requires_vpn": True,
        "response_time_ms": None,
        "status_code": None,
        "error": None,
    }

    try:
        # Direct check (from Hong Kong server)
        async with httpx.AsyncClient(timeout=timeout) as client:
            start = asyncio.get_event_loop().time()
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; AINav Bot/1.0)"}
            )
            elapsed = (asyncio.get_event_loop().time() - start) * 1000

            results["status_code"] = response.status_code
            results["response_time_ms"] = round(elapsed)

            if response.status_code == 200:
                results["is_accessible"] = True

                # Check for common VPN-required patterns
                content = response.text[:5000].lower()
                vpn_indicators = [
                    "blocked", "403 forbidden", "access denied",
                    "great firewall", "gfw", "connection reset"
                ]

                if not any(indicator in content for indicator in vpn_indicators):
                    results["requires_vpn"] = False

    except httpx.ConnectTimeout:
        results["error"] = "Connection timeout"
    except httpx.ConnectError:
        results["error"] = "Connection error (likely blocked)"
    except Exception as e:
        results["error"] = str(e)

    return results


@shared_task
async def batch_check_accessibility(tool_ids: List[str]):
    """
    Batch check accessibility for multiple tools.
    """
    async with async_session() as session:
        for tool_id in tool_ids:
            tool = await session.get(Tool, tool_id)
            if not tool:
                continue

            result = await check_china_accessibility(tool.website_url)

            tool.is_china_accessible = result["is_accessible"] and not result["requires_vpn"]
            tool.requires_vpn = result["requires_vpn"]
            tool.last_verified_at = datetime.utcnow()

        await session.commit()
```

---

## 4. Enrichment Pipeline Orchestration

### 4.1 Main Enrichment Pipeline

```python
# services/automation-service/app/pipelines/enrich.py

from celery import chain, group
from app.workers import (
    generate_screenshot,
    generate_tool_content,
    generate_tool_embedding,
    check_china_accessibility,
)

@shared_task(bind=True)
async def enrich_ingestion_item(self, ingestion_id: str):
    """
    Full enrichment pipeline for an ingested item.
    """
    async with async_session() as session:
        item = await session.get(IngestionQueue, ingestion_id)
        if not item or item.status != "pending":
            return

        item.status = "processing"
        await session.commit()

    try:
        # Step 1: Extract basic info
        raw = item.raw_data
        name = raw.get("name", "")
        tagline = raw.get("tagline", "")
        description = raw.get("description", "")
        url = item.source_url

        # Step 2: Run enrichment tasks in parallel
        results = await asyncio.gather(
            # Screenshot generation
            generate_screenshot.delay(url, slugify(name)).get(),

            # LLM content generation
            generate_tool_content(name, tagline, description, url),

            # Accessibility check
            check_china_accessibility.delay(url).get(),

            return_exceptions=True,
        )

        screenshot_result, llm_result, access_result = results

        # Step 3: Generate embedding
        embedding = generate_tool_embedding(
            name=name,
            name_cn=llm_result.get("tagline_cn"),
            tagline=tagline,
            tagline_cn=llm_result.get("tagline_cn"),
            description=description,
            description_cn=llm_result.get("description_cn"),
            tags=llm_result.get("suggested_tags", []),
        )

        # Step 4: Update ingestion record
        async with async_session() as session:
            item = await session.get(IngestionQueue, ingestion_id)

            item.extracted_name = name
            item.extracted_tagline = tagline

            # LLM-generated content
            item.ai_description_cn = llm_result.get("description_cn")
            item.ai_category_suggestion = await lookup_category_id(
                llm_result.get("suggested_category")
            )
            item.ai_scenario_suggestions = llm_result.get("suggested_scenarios", [])
            item.ai_tags = llm_result.get("suggested_tags", [])

            # Screenshots
            if not isinstance(screenshot_result, Exception):
                item.screenshot_url = screenshot_result.get("screenshot_url")
                item.logo_url = screenshot_result.get("thumbnail_url")

            # Pricing
            item.extracted_pricing = llm_result.get("pricing_type")

            # Access info
            if not isinstance(access_result, Exception):
                item.raw_data["china_accessible"] = access_result.get("is_accessible")
                item.raw_data["requires_vpn"] = access_result.get("requires_vpn")

            # Embedding
            item.raw_data["embedding"] = embedding

            # Mark as ready for review
            item.status = "review"
            item.processed_at = datetime.utcnow()

            await session.commit()

        return {"status": "success", "ingestion_id": ingestion_id}

    except Exception as e:
        async with async_session() as session:
            item = await session.get(IngestionQueue, ingestion_id)
            item.status = "error"
            item.error_message = str(e)
            item.retry_count += 1
            await session.commit()

        raise


async def lookup_category_id(category_slug: str) -> Optional[str]:
    """Look up category ID from slug."""
    async with async_session() as session:
        result = await session.execute(
            select(Category.id).where(Category.slug == category_slug)
        )
        row = result.scalar_one_or_none()
        return str(row) if row else None
```

---

## 5. Scheduled Tasks

### 5.1 Celery Beat Schedule

```python
# services/automation-service/app/celery_config.py

from celery.schedules import crontab

beat_schedule = {
    # Product Hunt crawler - Daily at 2 AM HKT
    "crawl-producthunt-daily": {
        "task": "app.workers.producthunt.crawl_producthunt",
        "schedule": crontab(hour=2, minute=0),
        "kwargs": {"days_back": 1, "min_votes": 50},
    },

    # GitHub trending - Every 6 hours
    "scrape-github-trending": {
        "task": "app.workers.github.scrape_github_trending",
        "schedule": crontab(hour="*/6", minute=30),
        "kwargs": {"min_stars": 100},
    },

    # ArXiv papers - Daily at 3 AM HKT
    "fetch-arxiv-papers": {
        "task": "app.workers.arxiv.fetch_arxiv_papers",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {"days_back": 1, "max_results": 50},
    },

    # RSS aggregation - Every hour
    "aggregate-rss-feeds": {
        "task": "app.workers.rss.aggregate_feeds",
        "schedule": crontab(minute=15),
    },

    # Process pending enrichments - Every 10 minutes
    "process-pending-enrichments": {
        "task": "app.pipelines.enrich.process_pending_queue",
        "schedule": crontab(minute="*/10"),
    },

    # Refresh tool accessibility - Weekly
    "refresh-accessibility": {
        "task": "app.workers.access_checker.batch_refresh_all",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),  # Monday 4 AM
    },

    # Update search index - Every 5 minutes
    "sync-meilisearch-index": {
        "task": "app.workers.search.sync_index",
        "schedule": crontab(minute="*/5"),
    },

    # Cleanup old ingestion records - Daily
    "cleanup-old-ingestions": {
        "task": "app.workers.cleanup.remove_old_records",
        "schedule": crontab(hour=5, minute=0),
        "kwargs": {"days_retention": 30},
    },

    # Generate daily stats - Daily at midnight
    "generate-daily-stats": {
        "task": "app.workers.analytics.generate_daily_stats",
        "schedule": crontab(hour=0, minute=5),
    },
}
```

---

## 6. Quality Scoring System

### 6.1 Tool Quality Score Calculator

```python
# services/automation-service/app/services/quality.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class QualityScore:
    total: float
    breakdown: dict

    @property
    def grade(self) -> str:
        if self.total >= 90:
            return "A"
        elif self.total >= 80:
            return "B"
        elif self.total >= 70:
            return "C"
        elif self.total >= 60:
            return "D"
        return "F"


def calculate_tool_quality_score(
    name: str,
    name_cn: Optional[str],
    tagline: Optional[str],
    tagline_cn: Optional[str],
    description: Optional[str],
    description_cn: Optional[str],
    logo_url: Optional[str],
    screenshot_url: Optional[str],
    pricing_type: Optional[str],
    is_china_accessible: bool,
    producthunt_votes: Optional[int],
    github_stars: Optional[int],
    rating_count: int,
    rating_avg: float,
) -> QualityScore:
    """
    Calculate a quality score (0-100) for a tool based on completeness
    and popularity metrics.
    """
    breakdown = {}

    # Completeness (40 points)
    completeness_score = 0

    # Required fields
    if name:
        completeness_score += 5
    if tagline or tagline_cn:
        completeness_score += 5
    if description or description_cn:
        completeness_score += 5

    # Chinese content (important for target audience)
    if name_cn:
        completeness_score += 3
    if tagline_cn:
        completeness_score += 4
    if description_cn:
        completeness_score += 4

    # Media
    if logo_url:
        completeness_score += 5
    if screenshot_url:
        completeness_score += 5

    # Metadata
    if pricing_type:
        completeness_score += 4

    breakdown["completeness"] = completeness_score

    # Accessibility (20 points)
    accessibility_score = 0
    if is_china_accessible:
        accessibility_score = 20
    breakdown["accessibility"] = accessibility_score

    # Popularity (25 points)
    popularity_score = 0

    if producthunt_votes:
        if producthunt_votes >= 500:
            popularity_score += 10
        elif producthunt_votes >= 200:
            popularity_score += 7
        elif producthunt_votes >= 100:
            popularity_score += 5
        else:
            popularity_score += 2

    if github_stars:
        if github_stars >= 10000:
            popularity_score += 10
        elif github_stars >= 1000:
            popularity_score += 7
        elif github_stars >= 100:
            popularity_score += 4
        else:
            popularity_score += 1

    if rating_count >= 10:
        popularity_score += 5
    elif rating_count >= 5:
        popularity_score += 3

    breakdown["popularity"] = min(popularity_score, 25)

    # User satisfaction (15 points)
    satisfaction_score = 0
    if rating_count >= 5:
        # Scale rating (1-5) to (0-15)
        satisfaction_score = (rating_avg - 1) * 15 / 4
    breakdown["satisfaction"] = round(satisfaction_score, 1)

    # Total
    total = sum(breakdown.values())

    return QualityScore(
        total=round(total, 1),
        breakdown=breakdown,
    )
```

---

## 7. Admin Dashboard Integration

### 7.1 Review Queue API

```python
# services/content-service/app/routers/admin/ingestion.py

from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_admin
from app.models import IngestionQueue, Tool
from app.schemas import IngestionReviewRequest, ToolCreateFromIngestion

router = APIRouter(prefix="/admin/ingestion", tags=["admin"])

@router.get("/queue")
async def get_review_queue(
    status: str = "review",
    source: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    admin = Depends(require_admin),
):
    """Get items in the review queue."""
    async with async_session() as session:
        query = select(IngestionQueue).where(IngestionQueue.status == status)

        if source:
            query = query.where(IngestionQueue.source == source)

        query = query.order_by(IngestionQueue.discovered_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await session.execute(query)
        items = result.scalars().all()

        return {
            "data": [item.to_review_dict() for item in items],
            "meta": {"page": page, "per_page": per_page}
        }


@router.patch("/{ingestion_id}")
async def review_ingestion(
    ingestion_id: str,
    review: IngestionReviewRequest,
    admin = Depends(require_admin),
):
    """
    Review and approve/reject an ingestion item.
    """
    async with async_session() as session:
        item = await session.get(IngestionQueue, ingestion_id)
        if not item:
            raise HTTPException(404, "Item not found")

        if review.status == "approved":
            # Create tool from ingestion
            tool = Tool(
                slug=slugify(review.overrides.get("name") or item.extracted_name),
                name=review.overrides.get("name") or item.extracted_name,
                name_cn=review.overrides.get("name_cn") or item.ai_description_cn,
                tagline=item.extracted_tagline,
                tagline_cn=review.overrides.get("tagline_cn"),
                description=item.raw_data.get("description"),
                description_cn=item.ai_description_cn,
                website_url=item.source_url,
                logo_url=item.logo_url,
                screenshot_url=item.screenshot_url,
                pricing_type=item.extracted_pricing,
                is_china_accessible=item.raw_data.get("china_accessible", True),
                requires_vpn=item.raw_data.get("requires_vpn", False),
                primary_category_id=review.overrides.get("category_id") or item.ai_category_suggestion,
                tags=review.overrides.get("tags") or item.ai_tags,
                source=item.source,
                producthunt_id=item.source_id if item.source == "producthunt" else None,
                producthunt_votes=item.raw_data.get("votes"),
                github_stars=item.raw_data.get("stars"),
                embedding=item.raw_data.get("embedding"),
                status="published",
                published_at=datetime.utcnow(),
            )
            session.add(tool)

            item.status = "approved"
            item.created_tool_id = tool.id

        elif review.status == "rejected":
            item.status = "rejected"

        item.reviewed_by = admin.id
        item.reviewed_at = datetime.utcnow()
        item.review_notes = review.notes

        await session.commit()

        # Trigger search index update
        if review.status == "approved":
            await sync_tool_to_search.delay(str(tool.id))

        return {"status": "success"}
```

---

## 8. Monitoring & Alerts

### 8.1 Pipeline Metrics

```python
# services/automation-service/app/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Ingestion metrics
ingestion_total = Counter(
    "ainav_ingestion_total",
    "Total ingestion attempts",
    ["source", "status"]
)

ingestion_duration = Histogram(
    "ainav_ingestion_duration_seconds",
    "Time spent processing ingestion",
    ["source"]
)

# Enrichment metrics
enrichment_llm_calls = Counter(
    "ainav_enrichment_llm_calls_total",
    "Total LLM API calls for enrichment",
    ["model", "status"]
)

enrichment_llm_latency = Histogram(
    "ainav_enrichment_llm_latency_seconds",
    "LLM API call latency"
)

# Queue metrics
queue_depth = Gauge(
    "ainav_queue_depth",
    "Current queue depth",
    ["queue_name", "status"]
)

# Screenshot metrics
screenshot_success_rate = Gauge(
    "ainav_screenshot_success_rate",
    "Screenshot generation success rate (30min window)"
)
```

### 8.2 Alert Rules

```yaml
# alerts/pipeline.yml

groups:
  - name: pipeline_alerts
    rules:
      - alert: HighIngestionFailureRate
        expr: |
          sum(rate(ainav_ingestion_total{status="error"}[1h]))
          / sum(rate(ainav_ingestion_total[1h])) > 0.1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High ingestion failure rate"
          description: "More than 10% of ingestions are failing"

      - alert: LLMApiErrors
        expr: |
          sum(rate(ainav_enrichment_llm_calls_total{status="error"}[30m])) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "LLM API errors detected"
          description: "DeepSeek API is returning errors"

      - alert: QueueBacklog
        expr: ainav_queue_depth{status="pending"} > 100
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Large queue backlog"
          description: "{{ $value }} items waiting in queue"

      - alert: CrawlerStalled
        expr: |
          increase(ainav_ingestion_total{source="producthunt"}[24h]) == 0
        for: 2h
        labels:
          severity: critical
        annotations:
          summary: "Product Hunt crawler may be stalled"
          description: "No new items ingested in 24 hours"
```

---

## 9. Summary

This content automation pipeline provides:

1. **Multi-Source Discovery**: Product Hunt, GitHub Trending, ArXiv, RSS feeds
2. **Intelligent Enrichment**: LLM-powered translations, categorization, embeddings
3. **Quality Assurance**: Automated scoring + human review workflow
4. **Accessibility Testing**: China network accessibility verification
5. **Visual Assets**: Automated screenshot and thumbnail generation
6. **Scalable Architecture**: Celery-based distributed task processing
7. **Monitoring**: Prometheus metrics + alerting for pipeline health

The pipeline is designed to maintain content freshness while ensuring quality through a hybrid automation + curation approach.

---

*This automation system enables the AI Navigator platform to stay current with the rapidly evolving AI tool landscape while maintaining high content quality standards.*
