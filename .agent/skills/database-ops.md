---
name: database-ops
description: Database operations skill for PostgreSQL
triggers:
  - "database"
  - "postgresql"
  - "sql"
  - "migration"
---

# Database Operations Skill

数据库操作技能配置。

## Tech Stack
- **Database:** PostgreSQL 16
- **Extensions:** pgvector, pg_trgm
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic

## Connection Configuration
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/ainav"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Common Queries

### Full Text Search (Chinese)
```sql
-- Create text search configuration for Chinese
CREATE TEXT SEARCH CONFIGURATION chinese (COPY = simple);

-- Add index
CREATE INDEX idx_tools_fts ON tools
USING gin(to_tsvector('chinese', name || ' ' || COALESCE(name_zh, '') || ' ' || COALESCE(description, '')));

-- Search query
SELECT * FROM tools
WHERE to_tsvector('chinese', name || ' ' || COALESCE(name_zh, '') || ' ' || COALESCE(description, ''))
      @@ plainto_tsquery('chinese', '人工智能');
```

### Vector Similarity Search (pgvector)
```sql
-- Create vector index
CREATE INDEX idx_tools_embedding ON tools
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Similarity search
SELECT id, name, name_zh,
       1 - (embedding <=> $1::vector) as similarity
FROM tools
WHERE embedding IS NOT NULL
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

### Pagination Pattern
```sql
-- Offset pagination (simple, less efficient for large offsets)
SELECT * FROM tools
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;

-- Cursor pagination (more efficient)
SELECT * FROM tools
WHERE created_at < $1
ORDER BY created_at DESC
LIMIT 20;
```

### Aggregations
```sql
-- Tools count by category
SELECT c.name, c.name_zh, COUNT(t.id) as tool_count
FROM categories c
LEFT JOIN tools t ON t.category_id = c.id
GROUP BY c.id
ORDER BY tool_count DESC;

-- Average rating by tool
SELECT t.name, t.name_zh,
       AVG(r.score) as avg_rating,
       COUNT(r.id) as rating_count
FROM tools t
LEFT JOIN ratings r ON r.tool_id = t.id
GROUP BY t.id
HAVING COUNT(r.id) > 0
ORDER BY avg_rating DESC;
```

## SQLAlchemy Async Patterns

### Basic CRUD
```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Create
tool = Tool(name="Example", url="https://example.com")
db.add(tool)
await db.commit()
await db.refresh(tool)

# Read
result = await db.execute(select(Tool).where(Tool.id == tool_id))
tool = result.scalar_one_or_none()

# Update
await db.execute(
    update(Tool)
    .where(Tool.id == tool_id)
    .values(name="Updated Name")
)
await db.commit()

# Delete
await db.execute(delete(Tool).where(Tool.id == tool_id))
await db.commit()
```

### Eager Loading
```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload for one-to-many
result = await db.execute(
    select(Tool)
    .options(selectinload(Tool.ratings))
    .where(Tool.slug == slug)
)

# joinedload for many-to-one
result = await db.execute(
    select(Tool)
    .options(joinedload(Tool.category))
    .where(Tool.slug == slug)
)
```

### Complex Queries
```python
from sqlalchemy import func, case, and_, or_

# Conditional aggregation
result = await db.execute(
    select(
        Category.name,
        func.count(Tool.id).label("total"),
        func.count(case((Tool.pricing == "free", 1))).label("free_count"),
    )
    .join(Tool, Category.id == Tool.category_id)
    .group_by(Category.id)
)

# Subqueries
top_rated_subq = (
    select(Rating.tool_id, func.avg(Rating.score).label("avg_score"))
    .group_by(Rating.tool_id)
    .subquery()
)

result = await db.execute(
    select(Tool, top_rated_subq.c.avg_score)
    .outerjoin(top_rated_subq, Tool.id == top_rated_subq.c.tool_id)
    .order_by(top_rated_subq.c.avg_score.desc().nullslast())
)
```

## Migration Patterns

### Create Table
```python
def upgrade():
    op.create_table(
        'new_table',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_new_table_name', 'new_table', ['name'])
```

### Add Column with Default
```python
def upgrade():
    op.add_column('tools',
        sa.Column('priority', sa.Integer(), server_default='0', nullable=False)
    )
```

### Data Migration
```python
def upgrade():
    # Add column
    op.add_column('tools',
        sa.Column('slug', sa.String(200), nullable=True)
    )

    # Populate data
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE tools
        SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
        WHERE slug IS NULL
    """))

    # Make non-nullable
    op.alter_column('tools', 'slug', nullable=False)
    op.create_unique_constraint('uq_tools_slug', 'tools', ['slug'])
```

## Performance Optimization

### Indexes
```sql
-- B-tree for equality and range
CREATE INDEX idx_tools_category ON tools(category_id);
CREATE INDEX idx_tools_created ON tools(created_at DESC);

-- GIN for array containment
CREATE INDEX idx_tools_tags ON tools USING gin(tags);

-- Partial index
CREATE INDEX idx_tools_featured ON tools(priority DESC)
WHERE is_featured = true;

-- Composite index
CREATE INDEX idx_tools_category_pricing ON tools(category_id, pricing);
```

### Query Analysis
```sql
-- Explain with analysis
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM tools WHERE category_id = 'xxx';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Backup & Restore
```bash
# Backup
pg_dump -U postgres -h localhost -d ainav -F c -f backup.dump

# Restore
pg_restore -U postgres -h localhost -d ainav -c backup.dump

# Backup with compression
pg_dump -U postgres ainav | gzip > backup.sql.gz

# Restore from compressed
gunzip -c backup.sql.gz | psql -U postgres ainav
```
