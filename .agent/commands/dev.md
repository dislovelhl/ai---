---
name: dev
description: Start development environment
usage: /dev [service]
args:
  - name: service
    description: "all | frontend | backend | db | redis"
    default: "all"
---

# Development Server Command

启动开发环境服务器。

## Usage

```bash
/dev           # 启动所有服务
/dev frontend  # 仅启动前端
/dev backend   # 仅启动后端
/dev db        # 仅启动数据库
```

## Actions

### All Services
```bash
cd "/home/dislove/document/ai 导航"
docker-compose up -d postgres redis meilisearch
cd ainav-backend && source ../.venv/bin/activate && uvicorn app.main:app --reload --port 8000 &
cd ainav-web && pnpm dev &
```

### Frontend Only
```bash
cd "/home/dislove/document/ai 导航/ainav-web"
pnpm dev
```

### Backend Only
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Database Only
```bash
cd "/home/dislove/document/ai 导航"
docker-compose up -d postgres redis
```

## Environment Check

Before starting, verify:
1. Docker is running
2. Port 3000 (frontend) is available
3. Port 8000 (backend) is available
4. Port 5432 (PostgreSQL) is available
5. Port 6379 (Redis) is available

## Output

Display URLs after startup:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Meilisearch: http://localhost:7700
