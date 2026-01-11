from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List
from ..dependencies import get_db, require_admin
from ..repository import ToolRepository, CategoryRepository, ScenarioRepository
from ..schemas import (
    ToolRead, ToolCreate, ToolUpdate,
    CategoryRead, CategoryCreate, CategoryUpdate,
    ScenarioRead, ScenarioCreate, ScenarioUpdate
)
from shared.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

# ==================== Tool Admin Endpoints ====================

@router.post("/tools", response_model=ToolRead)
async def create_tool_admin(
    tool_in: ToolCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Create a new tool (Admin only).

    Validates that the slug is unique before creating.
    """
    repo = ToolRepository(db)

    # Check if slug already exists
    existing = await repo.get_by_slug(tool_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    # Extract scenario_ids and create tool with relations
    dict_data = tool_in.model_dump()
    scenario_ids = dict_data.pop("scenario_ids", [])

    return await repo.create_with_relations(scenario_ids=scenario_ids, **dict_data)


@router.put("/tools/{tool_id}", response_model=ToolRead)
async def update_tool_admin(
    tool_id: UUID4,
    tool_in: ToolUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Update an existing tool (Admin only).

    Supports partial updates and updating scenario associations.
    """
    repo = ToolRepository(db)

    # Check if tool exists
    existing_tool = await repo.get_by_id(tool_id)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Extract update data
    update_data = tool_in.model_dump(exclude_unset=True)
    scenario_ids = update_data.pop("scenario_ids", None)

    # Update tool fields
    if update_data:
        tool = await repo.update(tool_id, **update_data)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")

    # Update scenario associations if provided
    if scenario_ids is not None:
        await repo.associate_scenarios(tool_id, scenario_ids)

    return await repo.get_by_id_with_relations(tool_id)


@router.delete("/tools/{tool_id}")
async def delete_tool_admin(
    tool_id: UUID4,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Delete a tool (Admin only).
    """
    repo = ToolRepository(db)

    # Check if tool exists
    existing_tool = await repo.get_by_id(tool_id)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    success = await repo.delete(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")

    return {"message": "Tool deleted successfully", "id": str(tool_id)}


# ==================== Category Admin Endpoints ====================

@router.post("/categories", response_model=CategoryRead)
async def create_category_admin(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Create a new category (Admin only).

    Validates that the slug is unique before creating.
    """
    repo = CategoryRepository(db)

    # Check if slug already exists
    existing = await repo.get_by_slug(category_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    # Create category
    dict_data = category_in.model_dump()
    return await repo.create(**dict_data)


@router.put("/categories/{category_id}", response_model=CategoryRead)
async def update_category_admin(
    category_id: UUID4,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Update an existing category (Admin only).

    Supports partial updates.
    """
    repo = CategoryRepository(db)

    # Check if category exists
    existing_category = await repo.get_by_id(category_id)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Extract update data (exclude unset fields for partial updates)
    update_data = category_in.model_dump(exclude_unset=True)

    # Update category
    if update_data:
        category = await repo.update(category_id, **update_data)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    # If no updates, return existing category
    return existing_category


@router.delete("/categories/{category_id}")
async def delete_category_admin(
    category_id: UUID4,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Delete a category (Admin only).
    """
    repo = CategoryRepository(db)

    # Check if category exists
    existing_category = await repo.get_by_id(category_id)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    success = await repo.delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category deleted successfully", "id": str(category_id)}
