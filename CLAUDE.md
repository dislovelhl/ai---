# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Navigation Platform (ai 导航)** - An AI tool directory and agentic platform for the Chinese market. Built as a microservices architecture with automated content pipelines and LangGraph-based agent orchestration.

## Development Commands

### Full Stack (Docker)
```bash
# Start all services
docker-compose up -d

# View logs for specific service
docker-compose logs -f agent_service

# Restart a service
docker-compose restart content_service
```

### Backend Development
```bash
cd ainav-backend

# Install dependencies
pip install -r requirements.txt

# Run a specific service (from ainav-backend directory)
uvicorn services.agent_service.app.main:app --reload --port 8005
uvicorn services.content_service.app.main:app --reload --port 8001
uvicorn services.search_service.app.main:app --reload --port 8002
uvicorn services.user_service.app.main:app --reload --port 8003

# Run Celery worker
celery -A services.automation_service.app.celery_app worker --loglevel=info

# Run Celery beat scheduler
celery -A services.automation_service.app.celery_app beat --loglevel=info

# Database migrations
alembic upgrade head                              # Apply all migrations
alembic revision --autogenerate -m "description"  # Generate migration
alembic downgrade -1                              # Rollback one version
```

### Frontend Development
```bash
cd ainav-web
npm install
npm run dev      # Start dev server on port 3000
npm run build    # Production build
npm run lint     # ESLint check
```

## Architecture

### Service Ports
| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Next.js web application |
| Content Service | 8001 | Tool & category CRUD |
| Search Service | 8002 | Meilisearch full-text search |
| User Service | 8003 | Auth & user profiles (JWT) |
| Automation Service | 8004 | GitHub/ProductHunt crawlers |
| Agent Service | 8005 | LangGraph workflow orchestration |
| PostgreSQL | 5433 | Primary database (pgvector) |
| Redis | 6379 | Cache & Celery broker |
| Meilisearch | 7700 | Search engine |

### Backend Structure
```
ainav-backend/
├── services/
│   ├── agent_service/      # LangGraph workflows, skills, executions
│   ├── automation_service/ # Celery tasks, content crawlers
│   ├── content_service/    # Tools, categories, scenarios
│   ├── search_service/     # Meilisearch integration
│   └── user_service/       # Authentication, user management
├── shared/
│   ├── models.py           # SQLAlchemy ORM models (all services share)
│   ├── database.py         # Async database connection
│   └── config.py           # Pydantic settings
└── alembic/                # Database migrations
```

### Frontend Structure
```
ainav-web/src/
├── app/                    # Next.js App Router pages
│   ├── agents/            # Agent workflow builder
│   ├── learn/             # Learning paths & roadmaps
│   ├── studio/            # AI workspace
│   └── tools/             # Tool directory
├── components/
│   ├── ui/                # shadcn/ui primitives
│   └── [feature]/         # Feature-specific components
├── lib/
│   ├── api.ts             # Backend API client
│   └── types.ts           # TypeScript definitions
└── stores/                # Zustand state stores
```

### Key Data Models
- **Tool** - AI tools with categories, pricing, China accessibility flags
- **Skill** - Tool API capabilities (OpenAPI-style definitions)
- **AgentWorkflow** - User-created agent blueprints (React Flow graph JSON)
- **AgentExecution** - Runtime logs with step-by-step execution traces
- **AgentMemory** - Vector embeddings for RAG (pgvector, 384 dimensions)

## Technology Stack

**Backend:** FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16 + pgvector, Redis, Celery, LangGraph, Meilisearch

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, TanStack Query, Zustand, @xyflow/react (flow diagrams)

## Environment Variables

Backend services expect:
```
DATABASE_URL=postgresql+asyncpg://ainav:ainavpassword@localhost:5433/ainav_db
REDIS_URL=redis://localhost:6379/0
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=masterKey
DEEPSEEK_API_KEY=...  # For agent LLM
```

Frontend expects:
```
NEXT_PUBLIC_API_URL=http://localhost:8001/v1
NEXT_PUBLIC_SEARCH_API=http://localhost:8002/v1
NEXT_PUBLIC_USER_API=http://localhost:8003/v1
```

### OAuth2 Social Login (Optional)

**GitHub OAuth:**
```bash
# 1. Create OAuth App at: https://github.com/settings/developers
# 2. Set callback URL: http://localhost:8003/v1/oauth/github/callback
# 3. Add to .env:
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8003/v1/oauth/github/callback
```

**WeChat OAuth (for Chinese users):**
```bash
# 1. Register at: https://open.weixin.qq.com/
# 2. Create Web Application, set callback domain
# 3. Add to .env:
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_REDIRECT_URI=http://localhost:8003/v1/oauth/wechat/callback
```

### Email Service (Optional)

For password reset and welcome emails:

```bash
# QQ Mail (recommended for Chinese users):
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_qq_email@qq.com
SMTP_PASSWORD=your_qq_authorization_code  # Get from QQ Mail settings
SMTP_FROM_EMAIL=your_qq_email@qq.com
SMTP_FROM_NAME=AI导航
SMTP_USE_SSL=true
SMTP_USE_TLS=false

# Gmail alternative:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_app_password  # Use App Password, not regular password
SMTP_FROM_EMAIL=your_gmail@gmail.com
SMTP_FROM_NAME=AI Navigation
SMTP_USE_SSL=false
SMTP_USE_TLS=true
```

### Production Security

For production deployment, ensure these are set:

```bash
# REQUIRED: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_32_char_minimum_secret_key

# Set to production
ENVIRONMENT=production

# Update frontend URL
FRONTEND_URL=https://your-production-domain.com
```

Security features enabled:
- CSRF protection for OAuth flows (Redis-based, 10-min TTL)
- Rate limiting on auth endpoints (5 login/min, 3 password reset/5min)
- JWT tokens expire in 1 hour (refresh tokens: 7 days)
- SECRET_KEY validation enforced in production mode

## API Patterns

All services expose:
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- Routes under `/v1/` prefix

Agent Service specific:
- `/v1/skills/` - Skill management
- `/v1/workflows/` - Workflow CRUD
- `/v1/executions/` - Workflow execution
- `/v1/agents/` - Agent chat interactions

## Database Conventions

- All models use UUID primary keys
- `TimestampMixin` adds `created_at` and `updated_at` columns
- Chinese translations use `_zh` suffix (e.g., `name_zh`, `description_zh`)
- Junction tables follow `{table1}_{table2}` naming (e.g., `tool_scenarios`)
