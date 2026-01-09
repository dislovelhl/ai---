# AI Navigator Platform - API Specification

> Version: 1.0.0
> Created: 2026-01-09
> Base URL: `https://api.ainav.cn/v1`
> Format: REST + JSON

---

## 1. API Overview

### 1.1 Design Principles

| Principle | Implementation |
|-----------|----------------|
| RESTful | Resource-based URLs with standard HTTP methods |
| Consistent | Uniform response format across all endpoints |
| Paginated | Cursor-based pagination for large datasets |
| Cacheable | ETag/Last-Modified headers for CDN caching |
| Localized | Accept-Language header for i18n content |
| Versioned | URL-based versioning (/v1/) |

### 1.2 Authentication

```
Authorization: Bearer <access_token>
```

- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Optional API keys for server-to-server integration

### 1.3 Standard Response Format

**Success Response:**
```json
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "has_more": true,
        "cursor": "eyJpZCI6MTAwfQ=="
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "error": {
        "code": "TOOL_NOT_FOUND",
        "message": "The requested tool does not exist",
        "details": {}
    }
}
```

### 1.4 Common Headers

| Header | Description |
|--------|-------------|
| `Accept-Language` | Content language (zh-CN, en-US) |
| `X-Request-ID` | Unique request identifier for tracing |
| `X-Rate-Limit-Remaining` | Remaining requests in current window |
| `X-Rate-Limit-Reset` | Unix timestamp when rate limit resets |

---

## 2. Tools API

### 2.1 List Tools

```
GET /v1/tools
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (full-text) |
| `category` | string | Category slug filter |
| `scenario` | string | Scenario slug filter |
| `pricing` | enum | `free`, `freemium`, `paid`, `beta_free`, `open_source` |
| `china_accessible` | boolean | Filter for China-accessible tools |
| `has_api` | boolean | Filter for tools with API |
| `is_open_source` | boolean | Filter for open source tools |
| `tags` | string[] | Filter by tags (comma-separated) |
| `sort` | enum | `popularity`, `rating`, `newest`, `name` |
| `page` | integer | Page number (1-indexed) |
| `per_page` | integer | Items per page (max 50, default 20) |

**Example Request:**
```http
GET /v1/tools?category=text-generation&pricing=free&china_accessible=true&sort=popularity&per_page=20
Accept-Language: zh-CN
```

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "deepseek",
            "name": "DeepSeek",
            "name_cn": "深度求索",
            "tagline": "Advanced AI assistant for reasoning and coding",
            "tagline_cn": "强大的推理和编程AI助手",
            "website_url": "https://www.deepseek.com/",
            "logo_url": "https://cdn.ainav.cn/logos/deepseek.png",
            "screenshot_url": "https://cdn.ainav.cn/screenshots/deepseek.png",
            "pricing_type": "beta_free",
            "free_tier_limits": "公测期间完全免费使用",
            "is_china_accessible": true,
            "requires_vpn": false,
            "requires_signup": true,
            "has_api": true,
            "is_open_source": true,
            "category": {
                "slug": "text-generation",
                "name": "Text Generation",
                "name_cn": "文本生成"
            },
            "tags": ["大模型", "LLM", "推理", "代码生成"],
            "rating_avg": 4.8,
            "rating_count": 1250,
            "view_count": 125000,
            "featured": true
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 156,
        "has_more": true
    }
}
```

### 2.2 Get Tool Detail

```
GET /v1/tools/{slug}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `slug` | string | Tool slug (URL-friendly identifier) |

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "slug": "deepseek",
        "name": "DeepSeek",
        "name_cn": "深度求索",
        "tagline": "Advanced AI assistant for reasoning and coding",
        "tagline_cn": "强大的推理和编程AI助手",
        "description": "DeepSeek is a powerful AI model...",
        "description_cn": "DeepSeek（深度求索）是国产顶级大模型...",
        "website_url": "https://www.deepseek.com/",
        "logo_url": "https://cdn.ainav.cn/logos/deepseek.png",
        "screenshot_url": "https://cdn.ainav.cn/screenshots/deepseek.png",
        "video_url": null,
        "pricing": {
            "type": "beta_free",
            "details": {
                "free_tier": "公测期间完全免费",
                "api_pricing": "按token计费，价格极低"
            },
            "free_tier_limits": "公测期间完全免费使用"
        },
        "access": {
            "is_china_accessible": true,
            "requires_vpn": false,
            "requires_signup": true,
            "signup_url": "https://www.deepseek.com/signup"
        },
        "developer": {
            "has_api": true,
            "api_docs_url": "https://platform.deepseek.com/docs",
            "is_open_source": true,
            "github_url": "https://github.com/deepseek-ai",
            "github_stars": 45000
        },
        "category": {
            "id": "...",
            "slug": "text-generation",
            "name": "Text Generation",
            "name_cn": "文本生成"
        },
        "scenarios": [
            {
                "slug": "ai-code-assistant",
                "name": "AI Coding",
                "name_cn": "AI写代码"
            },
            {
                "slug": "write-weekly-report",
                "name": "Write Weekly Report",
                "name_cn": "写周报"
            }
        ],
        "tags": ["大模型", "LLM", "推理", "代码生成", "数学", "开源"],
        "metrics": {
            "rating_avg": 4.8,
            "rating_count": 1250,
            "view_count": 125000,
            "click_count": 45000
        },
        "related_tools": [
            {
                "slug": "kimi",
                "name": "Kimi",
                "name_cn": "Kimi",
                "logo_url": "...",
                "pricing_type": "freemium"
            }
        ],
        "created_at": "2024-12-01T00:00:00Z",
        "updated_at": "2026-01-08T12:00:00Z",
        "last_verified_at": "2026-01-08T12:00:00Z"
    }
}
```

### 2.3 Compare Tools

```
POST /v1/tools/compare
```

**Request Body:**
```json
{
    "tool_slugs": ["deepseek", "kimi", "doubao"]
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "tools": [
            {
                "slug": "deepseek",
                "name_cn": "深度求索",
                "logo_url": "...",
                "pricing_type": "beta_free",
                "is_china_accessible": true,
                "has_api": true,
                "is_open_source": true,
                "rating_avg": 4.8,
                "strengths": ["推理能力强", "代码生成", "开源免费"]
            },
            {
                "slug": "kimi",
                "name_cn": "Kimi",
                "logo_url": "...",
                "pricing_type": "freemium",
                "is_china_accessible": true,
                "has_api": true,
                "is_open_source": false,
                "rating_avg": 4.6,
                "strengths": ["超长上下文", "研报分析", "长篇写作"]
            }
        ],
        "comparison_matrix": {
            "context_length": {
                "deepseek": "128K tokens",
                "kimi": "200K+ tokens",
                "doubao": "128K tokens"
            },
            "api_availability": {
                "deepseek": true,
                "kimi": true,
                "doubao": true
            },
            "pricing_model": {
                "deepseek": "公测免费 / API按量计费",
                "kimi": "每日免费额度 / 会员订阅",
                "doubao": "免费使用"
            }
        }
    }
}
```

### 2.4 Track Tool Click

```
POST /v1/tools/{slug}/click
```

**Request Body:**
```json
{
    "session_id": "abc123",
    "referrer": "search",
    "search_query": "AI写代码"
}
```

**Response:** `204 No Content`

---

## 3. Search API

### 3.1 Instant Search

```
GET /v1/search
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (required, min 1 char) |
| `limit` | integer | Max results (default 10, max 50) |
| `type` | enum | `all`, `tools`, `prompts`, `papers` |

**Example Request:**
```http
GET /v1/search?q=写周报&limit=10&type=all
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "tools": [
            {
                "slug": "notion-ai",
                "name_cn": "Notion AI",
                "tagline_cn": "AI驱动的笔记和文档工具",
                "logo_url": "...",
                "pricing_type": "freemium",
                "is_china_accessible": true,
                "highlight": "帮你<em>写周报</em>、写文档..."
            }
        ],
        "scenarios": [
            {
                "slug": "write-weekly-report",
                "name_cn": "写周报",
                "tool_count": 15
            }
        ],
        "prompts": [
            {
                "id": "...",
                "title_cn": "高效周报生成提示词",
                "preview": "请帮我根据以下工作内容生成周报..."
            }
        ],
        "query_suggestions": [
            "写周报 AI工具",
            "周报自动生成",
            "工作总结"
        ]
    },
    "meta": {
        "query": "写周报",
        "took_ms": 12
    }
}
```

### 3.2 Semantic Search

```
POST /v1/search/semantic
```

**Request Body:**
```json
{
    "query": "把图片背景变成透明的",
    "limit": 10,
    "filters": {
        "pricing": ["free", "freemium"],
        "china_accessible": true
    }
}
```

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "slug": "remove-bg",
            "name": "Remove.bg",
            "name_cn": "Remove.bg",
            "tagline_cn": "AI自动抠图去背景",
            "logo_url": "...",
            "similarity_score": 0.92,
            "pricing_type": "freemium",
            "is_china_accessible": true
        },
        {
            "slug": "clipdrop",
            "name": "Clipdrop",
            "name_cn": "Clipdrop",
            "tagline_cn": "AI图片编辑工具套件",
            "logo_url": "...",
            "similarity_score": 0.87,
            "pricing_type": "freemium",
            "is_china_accessible": false
        }
    ],
    "meta": {
        "query": "把图片背景变成透明的",
        "search_type": "semantic",
        "took_ms": 45
    }
}
```

### 3.3 Autocomplete Suggestions

```
GET /v1/search/suggest
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Partial query (min 1 char) |
| `limit` | integer | Max suggestions (default 5) |

**Example Response:**
```json
{
    "success": true,
    "data": {
        "suggestions": [
            {
                "text": "DeepSeek",
                "type": "tool",
                "slug": "deepseek"
            },
            {
                "text": "AI写代码",
                "type": "scenario",
                "slug": "ai-code-assistant"
            },
            {
                "text": "深度学习入门",
                "type": "query"
            }
        ]
    }
}
```

---

## 4. Categories & Scenarios API

### 4.1 List Categories

```
GET /v1/categories
```

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "...",
            "slug": "text-generation",
            "name": "Text Generation",
            "name_cn": "文本生成",
            "icon": "pen-line",
            "color": "#3B82F6",
            "tool_count": 45,
            "children": [
                {
                    "slug": "chatbots",
                    "name_cn": "聊天机器人",
                    "tool_count": 20
                },
                {
                    "slug": "writing-assistants",
                    "name_cn": "写作助手",
                    "tool_count": 25
                }
            ]
        }
    ]
}
```

### 4.2 Get Category Detail

```
GET /v1/categories/{slug}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "...",
        "slug": "text-generation",
        "name": "Text Generation",
        "name_cn": "文本生成",
        "description_cn": "利用AI生成各类文本内容...",
        "icon": "pen-line",
        "color": "#3B82F6",
        "tool_count": 45,
        "featured_tools": [
            {
                "slug": "deepseek",
                "name_cn": "深度求索",
                "logo_url": "..."
            }
        ],
        "related_scenarios": [
            {
                "slug": "write-weekly-report",
                "name_cn": "写周报"
            }
        ]
    }
}
```

### 4.3 List Scenarios

```
GET /v1/scenarios
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `featured` | boolean | Only featured scenarios |
| `limit` | integer | Max results |

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "slug": "write-weekly-report",
            "name": "Write Weekly Report",
            "name_cn": "写周报",
            "icon": "file-text",
            "color": "#10B981",
            "tool_count": 15,
            "is_featured": true,
            "top_tools": [
                {
                    "slug": "notion-ai",
                    "name_cn": "Notion AI",
                    "logo_url": "..."
                }
            ]
        }
    ]
}
```

---

## 5. Learning Hub API

### 5.1 List Roadmaps

```
GET /v1/roadmaps
```

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "...",
            "slug": "ai-video-creator-2026",
            "title": "2026 AI Video Creator Path",
            "title_cn": "2026 AI视频创作者成长之路",
            "description_cn": "从零开始成为AI视频创作者...",
            "difficulty_level": "beginner",
            "estimated_hours": 40,
            "view_count": 5600,
            "thumbnail_url": "..."
        }
    ]
}
```

### 5.2 Get Roadmap Detail

```
GET /v1/roadmaps/{slug}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": "...",
        "slug": "ai-video-creator-2026",
        "title_cn": "2026 AI视频创作者成长之路",
        "description_cn": "从零开始成为AI视频创作者...",
        "difficulty_level": "beginner",
        "estimated_hours": 40,
        "svg_content": "<svg>...</svg>",
        "structure": [
            {
                "id": "node-1",
                "title": "基础概念",
                "children": [
                    {
                        "id": "node-1-1",
                        "title": "什么是AI视频生成",
                        "resources": [
                            {
                                "type": "article",
                                "title": "AI视频生成入门指南",
                                "url": "...",
                                "estimated_time": "15min"
                            }
                        ],
                        "related_tools": ["jimeng", "runway"]
                    }
                ]
            }
        ]
    }
}
```

### 5.3 List Prompts

```
GET /v1/prompts
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model type (chatgpt, midjourney, etc.) |
| `category` | string | Prompt category |
| `q` | string | Search query |
| `featured` | boolean | Only featured prompts |

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "...",
            "title": "Weekly Report Generator",
            "title_cn": "高效周报生成器",
            "model_type": "chatgpt",
            "category": "writing",
            "prompt_text": "请根据以下工作内容，帮我生成一份专业的周报...",
            "preview_image_url": null,
            "example_output": "本周工作总结：\n1. 完成...",
            "copy_count": 2340,
            "like_count": 156,
            "tags": ["周报", "工作总结", "职场"]
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 450
    }
}
```

### 5.4 Get Prompt Detail

```
GET /v1/prompts/{id}
```

### 5.5 Copy Prompt (Track)

```
POST /v1/prompts/{id}/copy
```

**Response:** `204 No Content`

### 5.6 List ArXiv Papers

```
GET /v1/papers
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | ArXiv category (cs.AI, cs.CL) |
| `date_from` | date | Filter by submission date |
| `date_to` | date | Filter by submission date |

**Example Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "...",
            "arxiv_id": "2501.12345",
            "title": "Advances in Large Language Model Reasoning",
            "title_cn": "大型语言模型推理能力的进展",
            "abstract_cn": "本文探讨了大型语言模型...",
            "summary_cn": "这篇论文提出了一种新的...",
            "key_findings": [
                "提出了新的推理框架",
                "在数学任务上提升30%"
            ],
            "practical_applications": [
                "可用于代码生成",
                "适合复杂问题解决"
            ],
            "authors": ["John Doe", "Jane Smith"],
            "categories": ["cs.AI", "cs.CL"],
            "submitted_date": "2025-01-15",
            "pdf_url": "https://arxiv.org/pdf/2501.12345.pdf",
            "view_count": 450
        }
    ]
}
```

---

## 6. User API

### 6.1 Authentication

#### Login with Phone OTP

```
POST /v1/auth/phone/send-code
```

**Request Body:**
```json
{
    "phone": "+8613800138000"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "expires_in": 300,
        "message": "验证码已发送"
    }
}
```

#### Verify Phone OTP

```
POST /v1/auth/phone/verify
```

**Request Body:**
```json
{
    "phone": "+8613800138000",
    "code": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGc...",
        "refresh_token": "dGhpcy...",
        "expires_in": 86400,
        "user": {
            "id": "...",
            "phone": "+8613800138000",
            "nickname": null,
            "is_new_user": true
        }
    }
}
```

#### WeChat OAuth

```
GET /v1/auth/wechat/authorize
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `redirect_uri` | string | Callback URL after auth |
| `state` | string | CSRF protection state |

#### GitHub OAuth

```
GET /v1/auth/github/authorize
```

#### Refresh Token

```
POST /v1/auth/refresh
```

**Request Body:**
```json
{
    "refresh_token": "dGhpcy..."
}
```

### 6.2 User Profile

#### Get Current User

```
GET /v1/users/me
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "...",
        "phone": "+8613800138000",
        "email": null,
        "nickname": "AI爱好者",
        "avatar_url": "...",
        "bio": "热爱探索AI工具",
        "preferences": {
            "theme": "dark",
            "language": "zh-CN",
            "email_notifications": true
        },
        "stats": {
            "collections_count": 3,
            "ratings_count": 12,
            "prompts_saved": 45
        },
        "created_at": "2025-12-01T00:00:00Z"
    }
}
```

#### Update Profile

```
PATCH /v1/users/me
```

**Request Body:**
```json
{
    "nickname": "AI探索者",
    "bio": "专注于AI生产力工具",
    "preferences": {
        "theme": "dark"
    }
}
```

### 6.3 Collections

#### List My Collections

```
GET /v1/users/me/collections
```

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "...",
            "name": "写作工具",
            "description": "常用的AI写作工具",
            "is_public": false,
            "is_default": false,
            "tool_count": 8,
            "cover_image_url": "...",
            "created_at": "2025-12-15T00:00:00Z"
        }
    ]
}
```

#### Create Collection

```
POST /v1/users/me/collections
```

**Request Body:**
```json
{
    "name": "效率工具箱",
    "description": "提升工作效率的AI工具",
    "is_public": false
}
```

#### Add Tool to Collection

```
POST /v1/users/me/collections/{collection_id}/tools
```

**Request Body:**
```json
{
    "tool_slug": "deepseek",
    "notes": "推理能力很强，适合写代码"
}
```

#### Remove Tool from Collection

```
DELETE /v1/users/me/collections/{collection_id}/tools/{tool_slug}
```

### 6.4 Ratings

#### Submit Rating

```
POST /v1/tools/{slug}/ratings
```

**Request Body:**
```json
{
    "rating": 5,
    "review_text": "DeepSeek的推理能力非常强，代码生成质量很高，而且完全免费！"
}
```

#### Get My Ratings

```
GET /v1/users/me/ratings
```

---

## 7. Admin API

> Requires admin role authentication

### 7.1 Ingestion Queue

#### List Pending Items

```
GET /v1/admin/ingestion
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | enum | Filter by status |
| `source` | enum | Filter by source |

#### Review Item

```
PATCH /v1/admin/ingestion/{id}
```

**Request Body:**
```json
{
    "status": "approved",
    "review_notes": "Quality tool, approved for publication",
    "overrides": {
        "name_cn": "自定义中文名",
        "primary_category_id": "..."
    }
}
```

### 7.2 Tool Management

#### Create Tool (Manual)

```
POST /v1/admin/tools
```

#### Update Tool

```
PATCH /v1/admin/tools/{slug}
```

#### Publish Tool

```
POST /v1/admin/tools/{slug}/publish
```

#### Archive Tool

```
POST /v1/admin/tools/{slug}/archive
```

### 7.3 Analytics

#### Dashboard Stats

```
GET /v1/admin/stats/dashboard
```

**Response:**
```json
{
    "success": true,
    "data": {
        "today": {
            "pageviews": 15000,
            "unique_visitors": 8500,
            "searches": 4200,
            "new_users": 120
        },
        "trends": {
            "pageviews_change": 12.5,
            "visitors_change": 8.3
        },
        "top_tools": [
            {
                "slug": "deepseek",
                "name_cn": "深度求索",
                "views": 2500,
                "clicks": 800
            }
        ],
        "top_searches": [
            {
                "query": "AI写代码",
                "count": 450
            }
        ]
    }
}
```

---

## 8. Rate Limiting

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Public (no auth) | 60 requests | 1 minute |
| Authenticated | 300 requests | 1 minute |
| Search | 30 requests | 1 minute |
| Admin | 600 requests | 1 minute |

**Rate Limit Headers:**
```
X-Rate-Limit-Limit: 60
X-Rate-Limit-Remaining: 45
X-Rate-Limit-Reset: 1704067200
```

**Rate Limit Exceeded Response:**
```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests. Please try again later.",
        "retry_after": 45
    }
}
```

---

## 9. Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## 10. Webhooks (Future)

For integrations requiring real-time updates:

```
POST https://your-server.com/webhook
```

**Event Types:**
- `tool.created` - New tool published
- `tool.updated` - Tool information updated
- `paper.published` - New ArXiv paper summary

**Webhook Payload:**
```json
{
    "event": "tool.created",
    "timestamp": "2026-01-09T12:00:00Z",
    "data": {
        "tool": {
            "slug": "new-tool",
            "name_cn": "新工具"
        }
    }
}
```

---

*This API specification is designed for the AI Navigator platform MVP. Additional endpoints will be added as features expand.*
