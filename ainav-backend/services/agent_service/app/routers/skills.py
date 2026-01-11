"""
Skills Router - CRUD operations for AI tool skills (API capabilities).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
import math

from shared.database import get_async_session
from shared.models import Skill, Tool
from ..schemas import (
    SkillCreate, SkillUpdate, SkillResponse,
    PaginatedSkillsResponse
)

router = APIRouter()


@router.get("", response_model=PaginatedSkillsResponse)
async def list_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tool_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List skills with optional filtering by tool, status, and search.
    """
    query = select(Skill)
    count_query = select(func.count(Skill.id))
    
    # Apply filters
    if tool_id:
        query = query.where(Skill.tool_id == tool_id)
        count_query = count_query.where(Skill.tool_id == tool_id)
    
    if is_active is not None:
        query = query.where(Skill.is_active == is_active)
        count_query = count_query.where(Skill.is_active == is_active)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Skill.name.ilike(search_filter)) |
            (Skill.name_zh.ilike(search_filter)) |
            (Skill.description.ilike(search_filter))
        )
        count_query = count_query.where(
            (Skill.name.ilike(search_filter)) |
            (Skill.name_zh.ilike(search_filter)) |
            (Skill.description.ilike(search_filter))
        )
    
    # Get total count
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(Skill.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    skills = result.scalars().all()
    
    return PaginatedSkillsResponse(
        items=[SkillResponse.model_validate(s) for s in skills],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/by-tool/{tool_id}", response_model=list[SkillResponse])
async def get_skills_by_tool(
    tool_id: UUID,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get all skills for a specific tool.
    """
    query = select(Skill).where(Skill.tool_id == tool_id)
    
    if active_only:
        query = query.where(Skill.is_active == True)
    
    query = query.order_by(Skill.name)
    result = await db.execute(query)
    skills = result.scalars().all()
    
    return [SkillResponse.model_validate(s) for s in skills]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific skill by ID.
    """
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return SkillResponse.model_validate(skill)


@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new skill for a tool.
    """
    # Verify tool exists
    tool_result = await db.execute(select(Tool).where(Tool.id == skill_data.tool_id))
    tool = tool_result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check for duplicate slug within the same tool
    existing = await db.execute(
        select(Skill).where(
            (Skill.tool_id == skill_data.tool_id) &
            (Skill.slug == skill_data.slug)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Skill with this slug already exists for this tool")
    
    skill = Skill(**skill_data.model_dump())
    db.add(skill)
    
    # Update tool's has_api flag
    tool.has_api = True
    
    await db.commit()
    await db.refresh(skill)
    
    return SkillResponse.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: UUID,
    skill_data: SkillUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing skill.
    """
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Update fields
    update_data = skill_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(skill, field, value)
    
    await db.commit()
    await db.refresh(skill)
    
    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a skill.
    """
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    tool_id = skill.tool_id
    await db.delete(skill)
    
    # Check if tool still has any skills
    remaining = await db.execute(
        select(func.count(Skill.id)).where(Skill.tool_id == tool_id)
    )
    if remaining.scalar() == 0:
        tool_result = await db.execute(select(Tool).where(Tool.id == tool_id))
        tool = tool_result.scalar_one_or_none()
        if tool:
            tool.has_api = False
    
    await db.commit()
