---
name: deploy
description: Deployment operations
usage: /deploy <environment>
args:
  - name: environment
    description: "staging | production | rollback"
    required: true
---

# Deploy Command

部署到指定环境。

## Usage

```bash
/deploy staging     # 部署到预发布环境
/deploy production  # 部署到生产环境
/deploy rollback    # 回滚到上一版本
```

## Pre-deployment Checklist

1. [ ] All tests passing
2. [ ] Build successful
3. [ ] Database migrations ready
4. [ ] Environment variables updated
5. [ ] CDN cache purge prepared

## Actions

### Deploy to Staging
```bash
cd "/home/dislove/document/ai 导航"

# 1. Build images
docker build -t registry.cn-hongkong.aliyuncs.com/ainav/web:staging ainav-web/
docker build -t registry.cn-hongkong.aliyuncs.com/ainav/api:staging ainav-backend/

# 2. Push images
docker push registry.cn-hongkong.aliyuncs.com/ainav/web:staging
docker push registry.cn-hongkong.aliyuncs.com/ainav/api:staging

# 3. Update deployment
ssh staging "cd /app && docker-compose pull && docker-compose up -d"

# 4. Run migrations
ssh staging "cd /app && docker-compose exec api alembic upgrade head"

# 5. Health check
curl -f https://staging.ainav.com/api/health || echo "Health check failed!"
```

### Deploy to Production
```bash
cd "/home/dislove/document/ai 导航"

# 1. Tag release
VERSION=$(date +%Y%m%d%H%M)
git tag -a "v$VERSION" -m "Release $VERSION"
git push origin "v$VERSION"

# 2. Build images with version
docker build -t registry.cn-hongkong.aliyuncs.com/ainav/web:$VERSION ainav-web/
docker build -t registry.cn-hongkong.aliyuncs.com/ainav/api:$VERSION ainav-backend/

# 3. Push images
docker push registry.cn-hongkong.aliyuncs.com/ainav/web:$VERSION
docker push registry.cn-hongkong.aliyuncs.com/ainav/api:$VERSION

# 4. Rolling update
ssh production "cd /app && \
  export VERSION=$VERSION && \
  docker-compose pull && \
  docker-compose up -d --no-deps web api"

# 5. Database migrations
ssh production "cd /app && docker-compose exec api alembic upgrade head"

# 6. Purge CDN cache
# Cloudflare
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'

# 七牛云
# qshell cdnrefresh --dirs https://cdn.ainav.com/

# 7. Health check
curl -f https://ainav.com/api/health || echo "Health check failed!"

# 8. Smoke tests
pnpm test:smoke --env=production
```

### Rollback
```bash
# Get previous version
PREV_VERSION=$(ssh production "cd /app && docker-compose config | grep image | head -1 | sed 's/.*://'")

# Or specify version
PREV_VERSION="20240115"

# Rollback
ssh production "cd /app && \
  export VERSION=$PREV_VERSION && \
  docker-compose up -d --no-deps web api"

# Rollback database if needed
ssh production "cd /app && docker-compose exec api alembic downgrade -1"
```

## Environment Configuration

### Staging
```env
DATABASE_URL=postgresql://user:pass@staging-db:5432/ainav
REDIS_URL=redis://staging-redis:6379
MEILISEARCH_URL=http://staging-meilisearch:7700
NEXT_PUBLIC_API_URL=https://api.staging.ainav.com
```

### Production
```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/ainav
REDIS_URL=redis://prod-redis:6379
MEILISEARCH_URL=http://prod-meilisearch:7700
NEXT_PUBLIC_API_URL=https://api.ainav.com
```

## Monitoring After Deploy

```bash
# Check logs
ssh production "docker-compose logs -f --tail=100 web api"

# Check metrics
open https://grafana.ainav.com/d/ainav-overview

# Check error tracking
open https://sentry.io/organizations/ainav/
```

## Rollback Triggers

Automatically rollback if:
- Error rate > 5% for 5 minutes
- Response time P95 > 2s for 10 minutes
- Health check fails 3 consecutive times
