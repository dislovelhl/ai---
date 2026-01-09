---
name: build
description: Build for production
usage: /build [target]
args:
  - name: target
    description: "all | frontend | backend | docker"
    default: "all"
---

# Build Command

构建生产环境部署包。

## Usage

```bash
/build           # 构建所有
/build frontend  # 构建前端
/build backend   # 构建后端
/build docker    # 构建Docker镜像
```

## Actions

### Build Frontend
```bash
cd "/home/dislove/document/ai 导航/ainav-web"
pnpm build
pnpm export  # 如果是静态导出
```

### Build Backend
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
pip install build
python -m build
```

### Build Docker Images
```bash
cd "/home/dislove/document/ai 导航"

# Frontend
docker build -t ainav-web:latest -f ainav-web/Dockerfile ainav-web/

# Backend
docker build -t ainav-backend:latest -f ainav-backend/Dockerfile ainav-backend/
```

## Pre-build Checks

1. Run linting: `pnpm lint` / `ruff check`
2. Run tests: `pnpm test` / `pytest`
3. Check types: `pnpm type-check` / `mypy`
4. Verify environment variables

## Output

- Frontend: `ainav-web/.next/` or `ainav-web/out/`
- Backend: `ainav-backend/dist/`
- Docker: Images tagged and ready for push
