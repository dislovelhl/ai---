from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel

from pydantic import UUID4
from ..dependencies import get_db
from ..repository import ScenarioRepository, ToolRepository
from ..schemas import ScenarioRead, ScenarioCreate, ToolRead, ScenarioUpdate
from ..utils.recommendations import (
    calculate_top_tools_by_interactions,
    find_tool_combinations,
    find_related_scenarios
)
from shared.models import Scenario, Tool, tool_scenarios

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


# Response schemas for recommendation endpoints
class ToolRecommendationRead(BaseModel):
    tool: ToolRead
    recommendation_score: float

    class Config:
        from_attributes = True


class ToolCombinationRead(BaseModel):
    tools: List[ToolRead]
    co_occurrence_count: int

    class Config:
        from_attributes = True


class RelatedScenarioRead(BaseModel):
    scenario: ScenarioRead
    similarity_score: float

    class Config:
        from_attributes = True


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


@router.get("/{slug}/recommendations", response_model=List[ToolRecommendationRead])
async def get_scenario_recommendations(
    slug: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get top recommended tools for a scenario based on user interactions.

    Returns the top N tools ranked by weighted user interactions (views, clicks, likes, etc.).
    Falls back to static metrics (GitHub stars, ratings) when interaction data is sparse.
    """
    repo = ScenarioRepository(db)
    scenario = await repo.get_by_slug(slug)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get recommended tools with scores
    recommendations = await calculate_top_tools_by_interactions(
        db=db,
        scenario_id=scenario.id,
        limit=limit
    )

    # Convert to response format
    return [
        ToolRecommendationRead(
            tool=ToolRead.from_orm(tool),
            recommendation_score=score
        )
        for tool, score in recommendations
    ]


@router.get("/{slug}/combinations", response_model=List[ToolCombinationRead])
async def get_tool_combinations(
    slug: str,
    min_co_occurrence: int = 2,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get commonly used tool combinations for a scenario.

    Returns pairs of tools that frequently appear together across multiple scenarios,
    indicating they work well together or complement each other.
    """
    repo = ScenarioRepository(db)
    scenario = await repo.get_by_slug(slug)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get tool combinations
    combinations = await find_tool_combinations(
        db=db,
        scenario_id=scenario.id,
        min_co_occurrence=min_co_occurrence,
        limit=limit
    )

    # Convert to response format
    return [
        ToolCombinationRead(
            tools=[ToolRead.from_orm(tool) for tool in combo['tools']],
            co_occurrence_count=combo['co_occurrence_count']
        )
        for combo in combinations
    ]


@router.get("/{slug}/related", response_model=List[RelatedScenarioRead])
async def get_related_scenarios(
    slug: str,
    limit: int = 5,
    min_similarity: float = 0.1,
    db: AsyncSession = Depends(get_db)
):
    """
    Get related scenarios based on shared tools.

    Uses Jaccard similarity to find scenarios that share tools with the current scenario.
    Higher similarity scores indicate more tool overlap.
    """
    repo = ScenarioRepository(db)
    scenario = await repo.get_by_slug(slug)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get related scenarios with similarity scores
    related = await find_related_scenarios(
        db=db,
        scenario_id=scenario.id,
        limit=limit,
        min_similarity=min_similarity
    )

    # Convert to response format
    return [
        RelatedScenarioRead(
            scenario=ScenarioRead.from_orm(related_scenario),
            similarity_score=similarity
        )
        for related_scenario, similarity in related
    ]


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
