"""
Workflow Categories Router - CRUD operations for workflow categories.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
import math

from shared.database import get_async_session
from shared.models import WorkflowCategory
from ..schemas import (
    WorkflowCategoryCreate,
    WorkflowCategoryUpdate,
    WorkflowCategoryResponse,
    PaginatedWorkflowCategoriesResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedWorkflowCategoriesResponse)
async def list_workflow_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List workflow categories with optional search.
    """
    query = select(WorkflowCategory)
    count_query = select(func.count(WorkflowCategory.id))

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (WorkflowCategory.name.ilike(search_filter)) |
            (WorkflowCategory.name_zh.ilike(search_filter)) |
            (WorkflowCategory.description.ilike(search_filter))
        )
        count_query = count_query.where(
            (WorkflowCategory.name.ilike(search_filter)) |
            (WorkflowCategory.name_zh.ilike(search_filter)) |
            (WorkflowCategory.description.ilike(search_filter))
        )

    # Get total count
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    # Paginate and order by order field, then by name
    offset = (page - 1) * page_size
    query = query.order_by(
        WorkflowCategory.order.asc(),
        WorkflowCategory.name.asc()
    ).offset(offset).limit(page_size)

    result = await db.execute(query)
    categories = result.scalars().all()

    return PaginatedWorkflowCategoriesResponse(
        items=[WorkflowCategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{category_id}", response_model=WorkflowCategoryResponse)
async def get_workflow_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific workflow category by ID.
    """
    result = await db.execute(
        select(WorkflowCategory).where(WorkflowCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Workflow category not found")

    return WorkflowCategoryResponse.model_validate(category)


@router.post("", response_model=WorkflowCategoryResponse, status_code=201)
async def create_workflow_category(
    category_data: WorkflowCategoryCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new workflow category.
    """
    # Check slug uniqueness
    existing = await db.execute(
        select(WorkflowCategory).where(WorkflowCategory.slug == category_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Category with slug '{category_data.slug}' already exists"
        )

    category = WorkflowCategory(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return WorkflowCategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=WorkflowCategoryResponse)
async def update_workflow_category(
    category_id: UUID,
    category_data: WorkflowCategoryUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing workflow category.
    """
    result = await db.execute(
        select(WorkflowCategory).where(WorkflowCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Workflow category not found")

    # Check slug uniqueness if slug is being updated
    update_data = category_data.model_dump(exclude_unset=True)
    if 'slug' in update_data and update_data['slug'] != category.slug:
        existing = await db.execute(
            select(WorkflowCategory).where(WorkflowCategory.slug == update_data['slug'])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Category with slug '{update_data['slug']}' already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return WorkflowCategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_workflow_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a workflow category.
    Note: This will fail if there are workflows using this category.
    """
    result = await db.execute(
        select(WorkflowCategory).where(WorkflowCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Workflow category not found")

    try:
        await db.delete(category)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category that is in use by workflows"
        )
