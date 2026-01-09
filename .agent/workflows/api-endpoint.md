---
name: api-endpoint
description: Workflow for creating new API endpoints
triggers:
  - "/workflow api-endpoint"
  - "create api"
  - "new endpoint"
---

# API Endpoint Development Workflow

创建新API端点的标准流程。

## Phase 1: Design

### 1.1 Endpoint Specification
```yaml
Method: GET|POST|PUT|PATCH|DELETE
Path: /api/v1/<resource>
Description: 端点功能描述
Authentication: required|optional|none
Rate Limit: 100/minute
```

### 1.2 Request/Response Design
```yaml
Request:
  Headers:
    - Authorization: Bearer <token>
    - Content-Type: application/json
  Query Parameters:
    - page: int (default: 1)
    - limit: int (default: 20)
  Body:
    field: type (required|optional)

Response:
  Success (200):
    data: object
    meta: pagination
  Error (4xx/5xx):
    error: string
    detail: string
```

## Phase 2: Implementation

### 2.1 Create Schema
```python
# app/schemas/resource.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ResourceCreate(ResourceBase):
    """Create request schema"""
    pass


class ResourceUpdate(BaseModel):
    """Update request schema (all optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class ResourceResponse(ResourceBase):
    """Response schema"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """List response with pagination"""
    items: List[ResourceResponse]
    total: int
    page: int
    limit: int
```

### 2.2 Create Service
```python
# app/services/resource_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate


class ResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        limit: int = 20,
        **filters
    ) -> tuple[List[Resource], int]:
        """Get paginated list of resources"""
        offset = (page - 1) * limit

        # Base query
        query = select(Resource)

        # Apply filters
        if filters.get("category"):
            query = query.where(Resource.category == filters["category"])

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Get paginated results
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total

    async def get_by_id(self, resource_id: UUID) -> Optional[Resource]:
        """Get single resource by ID"""
        result = await self.db.execute(
            select(Resource).where(Resource.id == resource_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ResourceCreate) -> Resource:
        """Create new resource"""
        resource = Resource(**data.model_dump())
        self.db.add(resource)
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def update(
        self,
        resource_id: UUID,
        data: ResourceUpdate
    ) -> Optional[Resource]:
        """Update existing resource"""
        resource = await self.get_by_id(resource_id)
        if not resource:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resource, field, value)

        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def delete(self, resource_id: UUID) -> bool:
        """Delete resource"""
        resource = await self.get_by_id(resource_id)
        if not resource:
            return False

        await self.db.delete(resource)
        await self.db.commit()
        return True
```

### 2.3 Create Router
```python
# app/api/v1/resources.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceListResponse,
)
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=ResourceListResponse)
async def list_resources(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取资源列表"""
    service = ResourceService(db)
    items, total = await service.get_list(
        page=page,
        limit=limit,
        category=category,
    )
    return ResourceListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取单个资源"""
    service = ResourceService(db)
    resource = await service.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """创建新资源（需要认证）"""
    service = ResourceService(db)
    return await service.create(data)


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """更新资源（需要认证）"""
    service = ResourceService(db)
    resource = await service.update(resource_id, data)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """删除资源（需要认证）"""
    service = ResourceService(db)
    if not await service.delete(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
```

### 2.4 Register Router
```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from .resources import router as resources_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(resources_router)
```

## Phase 3: Testing

### 3.1 Unit Tests
```python
# tests/unit/test_resource_service.py
import pytest
from app.services.resource_service import ResourceService


@pytest.mark.asyncio
async def test_create_resource(db_session):
    service = ResourceService(db_session)
    data = ResourceCreate(name="Test", description="Test description")

    result = await service.create(data)

    assert result.name == "Test"
    assert result.id is not None


@pytest.mark.asyncio
async def test_get_list_with_pagination(db_session, sample_resources):
    service = ResourceService(db_session)

    items, total = await service.get_list(page=1, limit=10)

    assert len(items) <= 10
    assert total >= len(items)
```

### 3.2 Integration Tests
```python
# tests/integration/test_api_resources.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_resources(client: AsyncClient):
    response = await client.get("/api/v1/resources/")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_resource_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/resources/",
        json={"name": "Test"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_resource_with_auth(
    client: AsyncClient,
    auth_headers
):
    response = await client.post(
        "/api/v1/resources/",
        json={"name": "Test", "description": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
```

## Phase 4: Documentation

### 4.1 OpenAPI Docstrings
Already included in router with:
- Endpoint descriptions
- Response models
- Query parameter documentation

### 4.2 Update API Docs
```markdown
## Resources API

### List Resources
GET /api/v1/resources/

Query Parameters:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `category` (string): Filter by category

Response: ResourceListResponse
```

## Checklist

- [ ] Schema定义完成
- [ ] Service层实现
- [ ] Router注册
- [ ] 单元测试 > 80%覆盖
- [ ] 集成测试通过
- [ ] OpenAPI文档完整
- [ ] 错误处理完善
- [ ] 速率限制配置
