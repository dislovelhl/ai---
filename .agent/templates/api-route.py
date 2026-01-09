"""
FastAPI Router Template
Usage: /gen api <resource_name>
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.__RESOURCE__ import (
    __RESOURCE_PASCAL__Create,
    __RESOURCE_PASCAL__Update,
    __RESOURCE_PASCAL__Response,
    __RESOURCE_PASCAL__ListResponse,
)
from app.services.__RESOURCE___service import __RESOURCE_PASCAL__Service


# =============================================================================
# Router Configuration
# =============================================================================

router = APIRouter(
    prefix="/__RESOURCE_PLURAL__",
    tags=["__RESOURCE_PLURAL__"],
    responses={404: {"description": "Not found"}},
)


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=__RESOURCE_PASCAL__ListResponse)
async def list___RESOURCE_PLURAL__(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, min_length=1, description="Search query"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取__RESOURCE__列表

    - **page**: 页码（默认1）
    - **limit**: 每页数量（默认20，最大100）
    - **search**: 搜索关键词
    - **sort_by**: 排序字段
    - **sort_order**: 排序方向 (asc/desc)
    """
    service = __RESOURCE_PASCAL__Service(db)
    items, total = await service.get_list(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return __RESOURCE_PASCAL__ListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/{__RESOURCE___id}", response_model=__RESOURCE_PASCAL__Response)
async def get___RESOURCE__(
    __RESOURCE___id: UUID = Path(..., description="__RESOURCE_PASCAL__ ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个__RESOURCE__详情

    - **__RESOURCE___id**: __RESOURCE_PASCAL__ UUID
    """
    service = __RESOURCE_PASCAL__Service(db)
    item = await service.get_by_id(__RESOURCE___id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="__RESOURCE_PASCAL__ not found"
        )

    return item


@router.post("/", response_model=__RESOURCE_PASCAL__Response, status_code=201)
async def create___RESOURCE__(
    data: __RESOURCE_PASCAL__Create = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建新__RESOURCE__

    需要认证
    """
    service = __RESOURCE_PASCAL__Service(db)
    return await service.create(data, user_id=current_user.id)


@router.patch("/{__RESOURCE___id}", response_model=__RESOURCE_PASCAL__Response)
async def update___RESOURCE__(
    __RESOURCE___id: UUID = Path(..., description="__RESOURCE_PASCAL__ ID"),
    data: __RESOURCE_PASCAL__Update = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新__RESOURCE__

    需要认证，只能更新自己创建的或有权限的
    """
    service = __RESOURCE_PASCAL__Service(db)
    item = await service.update(__RESOURCE___id, data, user_id=current_user.id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="__RESOURCE_PASCAL__ not found or no permission"
        )

    return item


@router.delete("/{__RESOURCE___id}", status_code=204)
async def delete___RESOURCE__(
    __RESOURCE___id: UUID = Path(..., description="__RESOURCE_PASCAL__ ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除__RESOURCE__

    需要认证，只能删除自己创建的或有权限的
    """
    service = __RESOURCE_PASCAL__Service(db)
    success = await service.delete(__RESOURCE___id, user_id=current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="__RESOURCE_PASCAL__ not found or no permission"
        )


# =============================================================================
# Additional Endpoints
# =============================================================================

@router.get("/slug/{slug}", response_model=__RESOURCE_PASCAL__Response)
async def get___RESOURCE___by_slug(
    slug: str = Path(..., description="URL slug"),
    db: AsyncSession = Depends(get_db),
):
    """
    通过slug获取__RESOURCE__
    """
    service = __RESOURCE_PASCAL__Service(db)
    item = await service.get_by_slug(slug)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="__RESOURCE_PASCAL__ not found"
        )

    return item
