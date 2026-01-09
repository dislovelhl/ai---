---
name: backend-dev
description: Backend development skill for FastAPI/Python
triggers:
  - "backend"
  - "api"
  - "fastapi"
---

# Backend Development Skill

后端开发技能配置。

## Tech Stack
- **Framework:** FastAPI 0.100+
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 16 + pgvector
- **Cache:** Redis 7+
- **Task Queue:** Celery 5+

## Project Structure
```
ainav-backend/
├── app/
│   ├── api/
│   │   └── v1/                 # API版本1
│   │       ├── __init__.py     # Router aggregation
│   │       ├── tools.py        # Tools endpoints
│   │       ├── search.py       # Search endpoints
│   │       └── users.py        # User endpoints
│   ├── core/
│   │   ├── config.py           # Settings
│   │   ├── database.py         # DB connection
│   │   └── security.py         # Auth utilities
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── workers/                # Celery tasks
│   └── main.py                 # FastAPI app
├── alembic/                    # Migrations
├── tests/                      # Test files
└── pyproject.toml              # Dependencies
```

## Model Template
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from datetime import datetime

from app.core.database import Base


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    name_zh = Column(String(200))
    slug = Column(String(200), unique=True, nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(String(5000))
    tagline = Column(String(200))

    # Classification
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    tags = Column(ARRAY(String), default=[])

    # Metadata
    pricing = Column(String(50), default="free")
    china_accessible = Column(Boolean, default=True)
    features = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="tools")
    ratings = relationship("Rating", back_populates="tool")

    @hybrid_property
    def average_rating(self):
        if not self.ratings:
            return 0
        return sum(r.score for r in self.ratings) / len(self.ratings)
```

## Schema Template
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class PricingType(str, Enum):
    free = "free"
    freemium = "freemium"
    paid = "paid"
    enterprise = "enterprise"


class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, max_length=200)
    url: HttpUrl
    description: Optional[str] = Field(None, max_length=5000)
    tagline: Optional[str] = Field(None, max_length=200)
    pricing: PricingType = PricingType.free
    features: List[str] = Field(default_factory=list)


class ToolCreate(ToolBase):
    category_id: UUID
    tags: List[str] = Field(default_factory=list)


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = None
    description: Optional[str] = None
    pricing: Optional[PricingType] = None


class ToolResponse(ToolBase):
    id: UUID
    slug: str
    category_id: UUID
    china_accessible: bool
    average_rating: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ToolListResponse(BaseModel):
    items: List[ToolResponse]
    total: int
    page: int
    limit: int
    pages: int
```

## Service Template
```python
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        pricing: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Tool], int]:
        """Get paginated list of tools with filters"""
        offset = (page - 1) * limit

        query = select(Tool).options(selectinload(Tool.category))

        # Apply filters
        if category:
            query = query.join(Tool.category).where(Category.slug == category)
        if pricing:
            query = query.where(Tool.pricing == pricing)
        if search:
            query = query.where(
                or_(
                    Tool.name.ilike(f"%{search}%"),
                    Tool.name_zh.ilike(f"%{search}%"),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Get paginated results
        query = query.offset(offset).limit(limit).order_by(Tool.created_at.desc())
        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_by_slug(self, slug: str) -> Optional[Tool]:
        """Get tool by slug"""
        result = await self.db.execute(
            select(Tool)
            .options(selectinload(Tool.category), selectinload(Tool.ratings))
            .where(Tool.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ToolCreate) -> Tool:
        """Create new tool"""
        slug = self._generate_slug(data.name)
        tool = Tool(**data.model_dump(), slug=slug)
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def update(self, tool_id: UUID, data: ToolUpdate) -> Optional[Tool]:
        """Update tool"""
        tool = await self.get_by_id(tool_id)
        if not tool:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tool, field, value)

        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name"""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
```

## Router Template
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.schemas.tool import (
    ToolCreate, ToolUpdate, ToolResponse, ToolListResponse
)
from app.services.tool_service import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/", response_model=ToolListResponse)
async def list_tools(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    pricing: str = Query(None),
    search: str = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """获取工具列表"""
    service = ToolService(db)
    items, total = await service.get_list(
        page=page, limit=limit,
        category=category, pricing=pricing, search=search,
    )
    return ToolListResponse(
        items=items, total=total,
        page=page, limit=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/{slug}", response_model=ToolResponse)
async def get_tool(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取工具详情"""
    service = ToolService(db)
    tool = await service.get_by_slug(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.post("/", response_model=ToolResponse, status_code=201)
async def create_tool(
    data: ToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """创建新工具（需要认证）"""
    service = ToolService(db)
    return await service.create(data)
```

## Common Patterns

### Caching with Redis
```python
from app.core.redis import redis_client
import json

async def get_tool_cached(slug: str) -> Optional[dict]:
    # Try cache first
    cached = await redis_client.get(f"tool:{slug}")
    if cached:
        return json.loads(cached)

    # Fetch from DB
    tool = await service.get_by_slug(slug)
    if tool:
        # Cache for 1 hour
        await redis_client.setex(
            f"tool:{slug}",
            3600,
            json.dumps(tool.dict())
        )
    return tool
```

### Background Tasks
```python
from fastapi import BackgroundTasks

@router.post("/tools/{tool_id}/click")
async def track_click(
    tool_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Track tool click (non-blocking)"""
    background_tasks.add_task(track_click_async, tool_id)
    return {"status": "ok"}
```

### Error Handling
```python
from fastapi import HTTPException
from app.core.exceptions import ToolNotFoundError, ValidationError

@router.get("/{slug}")
async def get_tool(slug: str, db: AsyncSession = Depends(get_db)):
    try:
        tool = await service.get_by_slug(slug)
        if not tool:
            raise ToolNotFoundError(slug)
        return tool
    except ToolNotFoundError:
        raise HTTPException(status_code=404, detail="Tool not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```
