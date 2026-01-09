---
name: gen
description: Generate code scaffolding
usage: /gen <type> <name>
args:
  - name: type
    description: "component | page | api | model | service | worker"
    required: true
  - name: name
    description: "Name of the item to generate"
    required: true
---

# Generate Command

生成代码脚手架。

## Usage

```bash
/gen component ToolCard       # 生成React组件
/gen page tools/[id]          # 生成Next.js页面
/gen api tools                # 生成API路由
/gen model Tool               # 生成数据库模型
/gen service ToolService      # 生成业务服务
/gen worker screenshot        # 生成Celery任务
```

## Templates

### React Component
```bash
/gen component ToolComparison
```

Creates: `ainav-web/src/components/tools/ToolComparison.tsx`
```typescript
import { cn } from "@/lib/utils"

interface ToolComparisonProps {
  className?: string
}

export function ToolComparison({ className }: ToolComparisonProps) {
  return (
    <div className={cn("", className)}>
      {/* TODO: Implement ToolComparison */}
    </div>
  )
}
```

### Next.js Page
```bash
/gen page tools/compare
```

Creates: `ainav-web/src/app/tools/compare/page.tsx`
```typescript
import { Metadata } from "next"

export const metadata: Metadata = {
  title: "工具对比 - AI导航",
  description: "对比AI工具功能和价格",
}

export default function ToolsComparePage() {
  return (
    <main className="container py-8">
      <h1 className="text-3xl font-bold">工具对比</h1>
      {/* TODO: Implement page content */}
    </main>
  )
}
```

### API Endpoint (Backend)
```bash
/gen api compare
```

Creates: `ainav-backend/app/api/v1/compare.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import CompareService

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("/", response_model=CompareResponse)
async def compare_tools(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db),
):
    """对比多个AI工具"""
    service = CompareService(db)
    return await service.compare(request.tool_ids)
```

### Database Model
```bash
/gen model Comparison
```

Creates: `ainav-backend/app/models/comparison.py`
```python
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tool_ids = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="comparisons")
```

### Service Class
```bash
/gen service CompareService
```

Creates: `ainav-backend/app/services/compare_service.py`
```python
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.tool import Tool
from app.schemas.compare import CompareResponse, ToolComparison


class CompareService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compare(self, tool_ids: List[str]) -> CompareResponse:
        """对比多个工具"""
        stmt = select(Tool).where(Tool.id.in_(tool_ids))
        result = await self.db.execute(stmt)
        tools = result.scalars().all()

        comparisons = [
            ToolComparison(
                id=str(tool.id),
                name=tool.name,
                name_zh=tool.name_zh,
                pricing=tool.pricing,
                features=tool.features,
            )
            for tool in tools
        ]

        return CompareResponse(tools=comparisons)
```

### Celery Worker
```bash
/gen worker generate_comparison_report
```

Creates: `ainav-backend/app/workers/tasks/generate_comparison_report.py`
```python
from celery import shared_task
from app.core.database import SessionLocal
from app.services.compare_service import CompareService


@shared_task(bind=True, max_retries=3)
def generate_comparison_report(self, tool_ids: list[str]) -> dict:
    """生成工具对比报告"""
    try:
        with SessionLocal() as db:
            service = CompareService(db)
            # TODO: Implement report generation
            return {"status": "success", "tool_ids": tool_ids}
    except Exception as e:
        self.retry(countdown=60, exc=e)
```

## Options

- `--dry-run`: Preview generated code without creating files
- `--force`: Overwrite existing files
- `--with-test`: Also generate test file
