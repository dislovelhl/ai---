---
name: db
description: Database operations
usage: /db <action>
args:
  - name: action
    description: "migrate | rollback | seed | reset | backup | restore | shell"
    required: true
---

# Database Command

数据库管理操作。

## Usage

```bash
/db migrate    # 执行迁移
/db rollback   # 回滚迁移
/db seed       # 填充种子数据
/db reset      # 重置数据库
/db backup     # 备份数据库
/db restore    # 恢复数据库
/db shell      # 进入数据库Shell
```

## Actions

### Run Migrations
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Show current version
alembic current
```

### Rollback Migration
```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### Seed Data
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
python -m app.scripts.seed_data

# Seed specific data
python -m app.scripts.seed_categories
python -m app.scripts.seed_tools
```

### Reset Database
```bash
# Drop and recreate
docker-compose down -v postgres
docker-compose up -d postgres
sleep 5
alembic upgrade head
python -m app.scripts.seed_data
```

### Backup Database
```bash
# Local backup
docker exec ainav-postgres pg_dump -U postgres ainav > backup_$(date +%Y%m%d).sql

# Compressed backup
docker exec ainav-postgres pg_dump -U postgres ainav | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database
```bash
# From SQL file
cat backup.sql | docker exec -i ainav-postgres psql -U postgres ainav

# From compressed file
gunzip -c backup.sql.gz | docker exec -i ainav-postgres psql -U postgres ainav
```

### Database Shell
```bash
# PostgreSQL shell
docker exec -it ainav-postgres psql -U postgres ainav

# With pgcli (better UI)
pgcli postgresql://postgres:postgres@localhost:5432/ainav
```

## Common Queries

```sql
-- Check table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check vector similarity (pgvector)
SELECT name, name_zh,
       embedding <=> '[...]'::vector as distance
FROM tools
ORDER BY distance
LIMIT 10;
```
