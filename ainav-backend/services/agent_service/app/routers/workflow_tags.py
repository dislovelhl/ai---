"""
Workflow Tags Router - CRUD operations for workflow tags.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
import math

from shared.database import get_async_session
from shared.models import WorkflowTag
from ..schemas import (
    WorkflowTagCreate,
    WorkflowTagUpdate,
    WorkflowTagResponse,
    PaginatedWorkflowTagsResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedWorkflowTagsResponse)
async def list_workflow_tags(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List workflow tags with optional search.
    """
    query = select(WorkflowTag)
    count_query = select(func.count(WorkflowTag.id))

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (WorkflowTag.name.ilike(search_filter)) |
            (WorkflowTag.name_zh.ilike(search_filter))
        )
        count_query = count_query.where(
            (WorkflowTag.name.ilike(search_filter)) |
            (WorkflowTag.name_zh.ilike(search_filter))
        )

    # Get total count
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    # Paginate and order by usage_count descending, then by name
    offset = (page - 1) * page_size
    query = query.order_by(
        WorkflowTag.usage_count.desc(),
        WorkflowTag.name.asc()
    ).offset(offset).limit(page_size)

    result = await db.execute(query)
    tags = result.scalars().all()

    return PaginatedWorkflowTagsResponse(
        items=[WorkflowTagResponse.model_validate(t) for t in tags],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/popular", response_model=list[WorkflowTagResponse])
async def get_popular_workflow_tags(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get popular workflow tags sorted by usage count.
    """
    query = select(WorkflowTag).order_by(
        WorkflowTag.usage_count.desc(),
        WorkflowTag.name.asc()
    ).limit(limit)

    result = await db.execute(query)
    tags = result.scalars().all()

    return [WorkflowTagResponse.model_validate(t) for t in tags]


@router.get("/{tag_id}", response_model=WorkflowTagResponse)
async def get_workflow_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific workflow tag by ID.
    """
    result = await db.execute(
        select(WorkflowTag).where(WorkflowTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Workflow tag not found")

    return WorkflowTagResponse.model_validate(tag)


@router.post("", response_model=WorkflowTagResponse, status_code=201)
async def create_workflow_tag(
    tag_data: WorkflowTagCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new workflow tag.
    """
    # Check slug uniqueness
    existing = await db.execute(
        select(WorkflowTag).where(WorkflowTag.slug == tag_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Tag with slug '{tag_data.slug}' already exists"
        )

    tag = WorkflowTag(**tag_data.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return WorkflowTagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=WorkflowTagResponse)
async def update_workflow_tag(
    tag_id: UUID,
    tag_data: WorkflowTagUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing workflow tag.
    """
    result = await db.execute(
        select(WorkflowTag).where(WorkflowTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Workflow tag not found")

    # Check slug uniqueness if slug is being updated
    update_data = tag_data.model_dump(exclude_unset=True)
    if 'slug' in update_data and update_data['slug'] != tag.slug:
        existing = await db.execute(
            select(WorkflowTag).where(WorkflowTag.slug == update_data['slug'])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Tag with slug '{update_data['slug']}' already exists"
            )

    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)

    return WorkflowTagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
async def delete_workflow_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a workflow tag.
    Note: This will fail if there are workflows using this tag.
    """
    result = await db.execute(
        select(WorkflowTag).where(WorkflowTag.id == tag_id)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Workflow tag not found")

    try:
        await db.delete(tag)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tag that is in use by workflows"
        )
