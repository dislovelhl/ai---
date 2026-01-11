from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List
from ..dependencies import get_db, get_current_admin_user
from ..repository import ToolRepository
from ..schemas import ToolRead, ToolCreate, ToolUpdate
from shared.models import User

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("/", response_model=List[ToolRead])
async def list_tools(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = ToolRepository(db)
    return await repo.get_all_with_relations(skip=skip, limit=limit)

@router.get("/{slug}", response_model=ToolRead)
async def get_tool(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a tool by slug with relations."""
    repo = ToolRepository(db)
    tool = await repo.get_by_slug_with_relations(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.post("/", response_model=ToolRead)
async def create_tool(
    tool_in: ToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new tool. Requires admin privileges."""
    repo = ToolRepository(db)
    existing = await repo.get_by_slug(tool_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    dict_data = tool_in.model_dump()
    scenario_ids = dict_data.pop("scenario_ids", [])

    return await repo.create_with_relations(scenario_ids=scenario_ids, **dict_data)

@router.put("/{tool_id}", response_model=ToolRead)
async def update_tool(
    tool_id: UUID4,
    tool_in: ToolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a tool and its scenario associations. Requires admin privileges."""
    repo = ToolRepository(db)

    update_data = tool_in.model_dump(exclude_unset=True)
    scenario_ids = update_data.pop("scenario_ids", None)

    tool = await repo.update(tool_id, **update_data)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    if scenario_ids is not None:
        await repo.associate_scenarios(tool_id, scenario_ids)

    return await repo.get_by_id_with_relations(tool_id)

@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: UUID4,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a tool. Requires admin privileges."""
    repo = ToolRepository(db)
    success = await repo.delete(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}
