from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from pydantic import UUID4
from ..dependencies import get_db
from ..repository import ScenarioRepository, ToolRepository
from ..schemas import ScenarioRead, ScenarioCreate, ToolRead, ScenarioUpdate
from shared.models import Scenario, Tool, tool_scenarios

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("/", response_model=List[ScenarioRead])
async def list_scenarios(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all scenarios."""
    repo = ScenarioRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{slug}", response_model=ScenarioRead)
async def get_scenario(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a scenario by slug."""
    repo = ScenarioRepository(db)
    scenario = await repo.get_by_slug(slug)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.get("/{slug}/tools", response_model=List[ToolRead])
async def get_tools_by_scenario(
    slug: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """Get all tools associated with a scenario."""
    repo = ScenarioRepository(db)
    scenario = await repo.get_by_slug(slug)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Query tools through the junction table
    query = (
        select(Tool)
        .join(tool_scenarios, Tool.id == tool_scenarios.c.tool_id)
        .where(tool_scenarios.c.scenario_id == scenario.id)
        .options(selectinload(Tool.category), selectinload(Tool.scenarios))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ScenarioRead)
async def create_scenario(scenario_in: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    """Create a new scenario."""
    repo = ScenarioRepository(db)
    existing = await repo.get_by_slug(scenario_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    return await repo.create(**scenario_in.model_dump())

@router.put("/{scenario_id}", response_model=ScenarioRead)
async def update_scenario(scenario_id: UUID4, scenario_in: ScenarioUpdate, db: AsyncSession = Depends(get_db)):
    repo = ScenarioRepository(db)
    scenario = await repo.update(scenario_id, **scenario_in.model_dump(exclude_unset=True))
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: UUID4, db: AsyncSession = Depends(get_db)):
    repo = ScenarioRepository(db)
    success = await repo.delete(scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"message": "Scenario deleted successfully"}
