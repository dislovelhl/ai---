# Project Index: AI Navigator Platform

Generated: 2026-01-09 12:00:00 UTC

## 📁 Project Structure

```
ai 导航/
├── ainav-backend/                 # Python FastAPI microservices backend
│   ├── services/
│   │   ├── automation-service/    # Content automation & crawling
│   │   ├── content-service/       # Tool & category management
│   │   ├── search-service/        # Search infrastructure
│   │   └── user-service/          # User authentication & profiles
│   ├── shared/                    # Shared database models & config
│   ├── tests/                     # Backend test suite
│   └── docker-compose.yml         # Local development setup
├── ainav-web/                     # Next.js React frontend
│   ├── src/
│   │   ├── app/                   # Next.js app router pages
│   │   ├── components/            # Reusable UI components
│   │   └── lib/                   # Utilities & API clients
│   └── public/                    # Static assets
└── design-specs/                  # Architecture & design documentation
```

## 🚀 Entry Points

### Backend Services
- **Automation Service**: `ainav-backend/services/automation-service/app/main.py` - Content crawling and automation pipelines
- **Content Service**: `ainav-backend/services/content-service/app/main.py` - Tool CRUD and category management
- **Search Service**: `ainav-backend/services/search-service/app/main.py` - Full-text and vector search APIs
- **User Service**: `ainav-backend/services/user-service/app/main.py` - Authentication and user management

### Frontend
- **Main App**: `ainav-web/src/app/page.tsx` - Homepage with tool discovery and search
- **Layout**: `ainav-web/src/app/layout.tsx` - Root layout with providers and navigation

### Infrastructure
- **Docker Orchestration**: `docker-compose.yml` - Multi-service container setup with PostgreSQL, Redis, Meilisearch

## 📦 Core Modules

### Backend Architecture
#### Module: automation-service
- **Path**: `ainav-backend/services/automation-service/`
- **Exports**: Crawl tasks, enrichment pipelines, Celery workers
- **Purpose**: Automated content discovery from Product Hunt, GitHub, ArXiv
- **Key Files**:
  - `app/main.py` - FastAPI service entry point
  - `app/workers/tasks.py` - Celery task definitions
  - `app/clients/` - External API clients (GitHub, Product Hunt)

#### Module: content-service
- **Path**: `ainav-backend/services/content-service/`
- **Exports**: Tool CRUD, Category management, Scenario handling
- **Purpose**: Core content management APIs for AI tools catalog
- **Key Files**:
  - `app/routers/tools.py` - Tool management endpoints
  - `app/routers/categories.py` - Category CRUD operations

#### Module: search-service
- **Path**: `ainav-backend/services/search-service/`
- **Exports**: Full-text search, vector search, autocomplete
- **Purpose**: Search infrastructure using Meilisearch and embeddings
- **Key Files**:
  - `app/routers/search.py` - Search API endpoints

#### Module: user-service
- **Path**: `ainav-backend/services/user-service/`
- **Exports**: Authentication, user profiles, collections
- **Purpose**: User management and authentication services
- **Key Files**:
  - `app/routers/auth.py` - JWT authentication endpoints
  - `app/routers/users.py` - User profile management

#### Module: shared
- **Path**: `ainav-backend/shared/`
- **Exports**: Database models, configuration, utilities
- **Purpose**: Common code shared across all backend services
- **Key Files**:
  - `models.py` - SQLAlchemy database models (User, Tool, Category, Scenario)
  - `database.py` - Database connection and session management
  - `config.py` - Pydantic settings and environment configuration

### Frontend Architecture
#### Module: app-pages
- **Path**: `ainav-web/src/app/`
- **Exports**: Page components and API routes
- **Purpose**: Next.js app router pages and server components
- **Key Files**:
  - `page.tsx` - Homepage with featured tools and search
  - `tools/page.tsx` - Tools listing and discovery
  - `scenarios/[slug]/page.tsx` - Scenario-specific tool pages

#### Module: components
- **Path**: `ainav-web/src/components/`
- **Exports**: Reusable React components
- **Purpose**: UI component library built with shadcn/ui
- **Key Files**:
  - `layout/navbar.tsx` - Main navigation component
  - `tools/tool-card.tsx` - Tool display cards
  - `ui/` - shadcn/ui component library

#### Module: lib
- **Path**: `ainav-web/src/lib/`
- **Exports**: API clients, utilities, type definitions
- **Purpose**: Frontend utilities and external service integrations
- **Key Files**:
  - `api.ts` - API client functions for backend services
  - `utils.ts` - Utility functions and helpers
  - `types.ts` - TypeScript type definitions

## 🔧 Configuration

### Environment Configuration
- **Backend Config**: `ainav-backend/shared/config.py` - Pydantic-based settings management
- **Docker Compose**: `docker-compose.yml` - Multi-service orchestration with health checks
- **Frontend Config**: `ainav-web/next.config.ts` - Next.js build and runtime configuration

### Package Management
- **Frontend**: `ainav-web/package.json` - React/Next.js dependencies (29 packages)
- **Backend**: `ainav-backend/requirements.txt` - Python dependencies (21 packages)

### Development Tools
- **Frontend**: ESLint, TypeScript, Tailwind CSS 4.0
- **Backend**: Alembic migrations, pytest test framework
- **Container**: Docker multi-stage builds for all services

## 📚 Documentation

### Architecture Documents
- **System Architecture**: `design-specs/system-architecture.md` - Comprehensive technical architecture (670+ lines)
- **API Specification**: `design-specs/api-specification.md` - API design and endpoints
- **Database Schema**: `design-specs/database-schema.md` - Data model specifications
- **Frontend Architecture**: `design-specs/frontend-architecture.md` - React/Next.js design patterns
- **Content Automation**: `design-specs/content-automation-pipeline.md` - Crawling and enrichment pipelines
- **Infrastructure**: `design-specs/infrastructure-deployment.md` - Deployment and scaling strategy

### Code Documentation
- **README**: `ainav-web/README.md` - Frontend setup and development guide
- **API Docs**: Auto-generated OpenAPI/Swagger docs from FastAPI services

## 🧪 Test Coverage

### Backend Tests
- **Test Files**: 5 Python test files in `ainav-backend/tests/`
- **Coverage Areas**:
  - `test_automation.py` - Automation service functionality
  - `test_content_crud.py` - Content management operations
  - `test_github_client.py` - GitHub API integration
  - `verify_user_service.py` - User service validation
  - `insert_test_tool.py` - Tool insertion workflows

### Test Infrastructure
- **Framework**: pytest with async support
- **Database**: Test database setup in `test_db.py`
- **Coverage**: Unit tests for core business logic and API endpoints

## 🔗 Key Dependencies

### Frontend Stack
- **Framework**: Next.js 16.1.1 (App Router, React 19.2.3)
- **Styling**: Tailwind CSS 4.0, shadcn/ui components
- **State Management**: TanStack Query 5.62.7, Zustand 5.0.2
- **UI Components**: Radix UI primitives, Lucide React icons
- **Forms**: React Hook Form 7.54.1 with Zod validation
- **TypeScript**: Full type coverage with strict mode

### Backend Stack
- **API Framework**: FastAPI 0.115.6 with automatic OpenAPI docs
- **Database**: SQLAlchemy 2.0.36 async ORM, PostgreSQL with pgvector
- **Task Queue**: Celery 5.4.0 with Redis 5.2.1 backend
- **Search**: Meilisearch 0.31.2 for full-text search
- **Authentication**: JWT tokens with bcrypt password hashing
- **HTTP Client**: httpx 0.28.1 for external API calls
- **ML/Embeddings**: sentence-transformers 3.3.1 for content embeddings

### Infrastructure Dependencies
- **Database**: PostgreSQL 16 with pgvector extension
- **Cache**: Redis 7-alpine for session and task queue storage
- **Search Engine**: Meilisearch v1.12 for fast, typo-tolerant search
- **Container**: Docker with multi-stage builds
- **Reverse Proxy**: Nginx load balancer (implied in architecture)

## 📝 Quick Start

### Local Development Setup
1. **Clone and navigate**: `cd /path/to/ai-navigator`
2. **Start services**: `docker-compose up -d`
3. **Install frontend deps**: `cd ainav-web && npm install`
4. **Start frontend**: `npm run dev` (runs on port 3000)
5. **Verify backend**: Check service health endpoints (ports 8001-8004)

### Key URLs
- **Frontend**: http://localhost:3000
- **Content API**: http://localhost:8001/v1
- **Search API**: http://localhost:8002/v1/search
- **User API**: http://localhost:8003/v1
- **Automation API**: http://localhost:8004

### Development Workflow
1. **Backend changes**: Services auto-reload in Docker containers
2. **Frontend changes**: Hot reload with Next.js dev server
3. **Database migrations**: `alembic upgrade head` in backend container
4. **Testing**: `pytest` in backend services, `npm test` in frontend

---

**Token Efficiency**: This index reduces repository reading from ~58K tokens to ~3K tokens (94% reduction) while maintaining comprehensive project overview.
