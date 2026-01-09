---
name: database-migration
description: Workflow for database schema changes
triggers:
  - "/workflow database-migration"
  - "db migration"
  - "change database"
---

# Database Migration Workflow

数据库结构变更的标准流程。

## Phase 1: Planning

### 1.1 Change Assessment
- [ ] 明确需要的变更
- [ ] 评估对现有数据的影响
- [ ] 确定是否需要数据迁移
- [ ] 评估停机时间需求

### 1.2 Migration Types
| Type | Description | Risk Level |
|------|-------------|------------|
| Add column | 添加新列 | Low |
| Add table | 添加新表 | Low |
| Add index | 添加索引 | Low-Medium |
| Modify column | 修改列类型 | Medium-High |
| Drop column | 删除列 | High |
| Drop table | 删除表 | High |

## Phase 2: Development

### 2.1 Create Model Changes
```python
# app/models/resource.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(String(2000))

    # New column to add
    priority = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    metadata = Column(JSONB, default={})
    tags = Column(ARRAY(String), default=[])

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2.2 Generate Migration
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# Auto-generate migration
alembic revision --autogenerate -m "add_priority_and_featured_to_resources"
```

### 2.3 Review Migration File
```python
# alembic/versions/xxxx_add_priority_and_featured_to_resources.py
"""add priority and featured to resources

Revision ID: xxxx
Revises: yyyy
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('resources',
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0')
    )
    op.add_column('resources',
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false')
    )
    op.add_column('resources',
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default='{}')
    )
    op.add_column('resources',
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}')
    )

    # Create index for featured items
    op.create_index('idx_resources_is_featured', 'resources', ['is_featured'])
    op.create_index('idx_resources_priority', 'resources', ['priority'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_resources_priority', table_name='resources')
    op.drop_index('idx_resources_is_featured', table_name='resources')

    # Drop columns
    op.drop_column('resources', 'tags')
    op.drop_column('resources', 'metadata')
    op.drop_column('resources', 'is_featured')
    op.drop_column('resources', 'priority')
```

## Phase 3: Testing

### 3.1 Test Locally
```bash
# Apply migration
alembic upgrade head

# Verify changes
docker exec -it ainav-postgres psql -U postgres ainav -c "\d resources"

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 3.2 Test Data Migration
```python
# If data migration needed
def upgrade() -> None:
    # Schema changes first
    op.add_column('resources',
        sa.Column('priority', sa.Integer(), nullable=True)
    )

    # Data migration
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE resources
            SET priority = CASE
                WHEN category = 'featured' THEN 100
                WHEN category = 'popular' THEN 50
                ELSE 0
            END
        """)
    )

    # Make column non-nullable after data migration
    op.alter_column('resources', 'priority',
        nullable=False,
        server_default='0'
    )
```

### 3.3 Run Tests
```bash
# Ensure tests pass with new schema
pytest tests/ -v

# Test specific migration scenarios
pytest tests/test_migrations.py -v
```

## Phase 4: Staging Deployment

### 4.1 Apply to Staging
```bash
# Backup staging database first
ssh staging "docker exec ainav-postgres pg_dump -U postgres ainav > /backup/pre_migration_$(date +%Y%m%d).sql"

# Apply migration
ssh staging "cd /app && docker-compose exec api alembic upgrade head"

# Verify
ssh staging "docker exec ainav-postgres psql -U postgres ainav -c '\d resources'"
```

### 4.2 Staging Verification
- [ ] Migration applied successfully
- [ ] Application starts without errors
- [ ] API endpoints work correctly
- [ ] No data corruption

## Phase 5: Production Deployment

### 5.1 Pre-Production Checklist
- [ ] Staging verification complete
- [ ] Backup production database
- [ ] Downtime window scheduled (if needed)
- [ ] Rollback plan ready
- [ ] Team notified

### 5.2 Production Backup
```bash
# Full backup before migration
ssh production "docker exec ainav-postgres pg_dump -U postgres ainav | gzip > /backup/pre_migration_$(date +%Y%m%d_%H%M).sql.gz"
```

### 5.3 Apply Migration
```bash
# Apply to production
ssh production "cd /app && docker-compose exec api alembic upgrade head"

# Verify immediately
ssh production "docker exec ainav-postgres psql -U postgres ainav -c 'SELECT count(*) FROM resources'"
```

### 5.4 Post-Migration Verification
- [ ] All tables accessible
- [ ] Row counts match pre-migration
- [ ] Application healthy
- [ ] API responding correctly
- [ ] No error spikes in monitoring

## Rollback Procedures

### Automatic Rollback
```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Manual Rollback
```sql
-- If automatic rollback fails
-- Restore from backup
psql -U postgres ainav < pre_migration_backup.sql
```

## Best Practices

### DO
- Always test migrations locally first
- Always backup before applying to production
- Use `server_default` for new NOT NULL columns
- Create indexes concurrently in production
- Review auto-generated migrations

### DON'T
- Don't run `alembic downgrade base` in production
- Don't modify already-applied migrations
- Don't drop columns without data backup
- Don't add NOT NULL columns without defaults

## Common Patterns

### Add Column with Default
```python
op.add_column('table',
    sa.Column('new_col', sa.String(100), server_default='default_value')
)
```

### Rename Column
```python
op.alter_column('table', 'old_name', new_column_name='new_name')
```

### Create Index Concurrently (Production)
```python
# For production without downtime
op.execute('CREATE INDEX CONCURRENTLY idx_name ON table(column)')
```

### Add Foreign Key
```python
op.add_column('table',
    sa.Column('ref_id', sa.UUID(), sa.ForeignKey('other_table.id'))
)
```
