---
name: add-tool
description: Workflow for adding new AI tools to the platform
triggers:
  - "/workflow add-tool"
  - "add new tool"
  - "add ai tool"
---

# Add AI Tool Workflow

添加新AI工具到平台的标准流程。

## Prerequisites

- Tool name and URL
- Category information
- Pricing model (free/freemium/paid/enterprise)
- China accessibility status

## Phase 1: Information Collection

### 1.1 Basic Information
```yaml
name: ""           # English name
name_zh: ""        # Chinese name (required)
url: ""            # Official website
tagline: ""        # Short description (< 100 chars)
description: ""    # Full description (Chinese)
```

### 1.2 Classification
```yaml
category: ""       # Primary category
scenarios: []      # Use case scenarios
tags: []           # Related tags
```

### 1.3 Pricing & Access
```yaml
pricing: "free|freemium|paid|enterprise"
china_accessible: true|false|"proxy"
access_method: "direct|proxy|vpn|none"
free_tier: true|false
```

## Phase 2: Content Enrichment

### 2.1 Screenshot Generation
```bash
cd ainav-backend
python -m app.scripts.generate_screenshot --url "https://tool-url.com"
```

Or using Playwright directly:
```python
from playwright.async_api import async_playwright

async def capture_screenshot(url: str, output_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=output_path, full_page=False)
        await browser.close()
```

### 2.2 Description Generation (LLM)
```bash
python -m app.scripts.generate_description --url "https://tool-url.com"
```

Uses DeepSeek API to generate:
- Chinese description
- Feature highlights
- Use case suggestions
- Comparison notes

### 2.3 Embedding Generation
```bash
python -m app.scripts.generate_embedding --tool-id "uuid"
```

Generates BGE-M3 embedding for semantic search.

## Phase 3: Database Entry

### 3.1 Using Admin Script
```bash
cd ainav-backend
python -m app.scripts.add_tool \
  --name "Claude" \
  --name-zh "Claude AI助手" \
  --url "https://claude.ai" \
  --category "AI Assistant" \
  --pricing "freemium" \
  --china-accessible "proxy"
```

### 3.2 Using Admin API
```bash
curl -X POST "http://localhost:8000/api/v1/admin/tools" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Claude",
    "name_zh": "Claude AI助手",
    "url": "https://claude.ai",
    "tagline": "Anthropic打造的AI助手",
    "description": "Claude是由Anthropic开发的大语言模型...",
    "category_id": "uuid-of-ai-assistant",
    "pricing": "freemium",
    "china_accessible": "proxy",
    "features": ["对话", "代码生成", "文档分析"]
  }'
```

### 3.3 Bulk Import
```bash
# From JSON file
python -m app.scripts.import_tools --file new_tools.json

# From CSV
python -m app.scripts.import_tools --file new_tools.csv --format csv
```

**JSON Format:**
```json
[
  {
    "name": "Claude",
    "name_zh": "Claude AI助手",
    "url": "https://claude.ai",
    "category": "AI Assistant",
    "pricing": "freemium"
  }
]
```

## Phase 4: Quality Assurance

### 4.1 Verification Checklist
- [ ] URL accessible
- [ ] Screenshot quality OK
- [ ] Description accurate
- [ ] Category correct
- [ ] Pricing information accurate
- [ ] China accessibility verified

### 4.2 Accessibility Check
```bash
python -m app.scripts.check_accessibility --url "https://tool-url.com"
```

Tests:
- Direct access from China server
- Response time
- SSL certificate
- Blocked status

### 4.3 Search Index Update
```bash
# Update Meilisearch index
python -m app.scripts.reindex_search
```

## Phase 5: Publication

### 5.1 Review Queue
New tools enter review queue:
```bash
# Check pending tools
python -m app.scripts.list_pending_tools

# Approve tool
python -m app.scripts.approve_tool --id "uuid"

# Reject tool
python -m app.scripts.reject_tool --id "uuid" --reason "Duplicate"
```

### 5.2 Post-Publication
- [ ] Verify appears in search results
- [ ] Verify category listing
- [ ] Check SEO metadata
- [ ] Monitor analytics

## Quick Add Template

For rapid addition, copy this template:

```python
# Quick add script
from app.services.tool_service import ToolService

tool_data = {
    "name": "ToolName",
    "name_zh": "工具中文名",
    "url": "https://tool.com",
    "tagline": "一句话介绍",
    "description": "详细描述...",
    "category_slug": "ai-assistant",
    "scenarios": ["writing", "coding"],
    "pricing": "freemium",
    "china_accessible": True,
    "features": ["Feature 1", "Feature 2"]
}

await ToolService.create_tool(tool_data)
```

## Common Issues

### Screenshot Fails
- Check if site blocks automated browsers
- Try adding User-Agent header
- Use stealth mode in Playwright

### Embedding Generation Slow
- Batch process during off-peak hours
- Use GPU-accelerated inference if available

### Duplicate Detection
```bash
# Check for duplicates before adding
python -m app.scripts.check_duplicate --url "https://tool.com"
```
