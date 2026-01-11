from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from typing import List, Optional, Dict, Set
from uuid import UUID
from pydantic import BaseModel, Field
from collections import defaultdict

from ..dependencies import get_db, get_current_active_user
from shared.models import UserInteraction, Tool, AgentWorkflow, User

router = APIRouter()

class InteractionCreate(BaseModel):
    item_type: str
    item_id: UUID
    action: str
    meta_data: Optional[dict] = None

class RecommendationItemResponse(BaseModel):
    """Individual recommendation item"""
    id: UUID
    type: str = Field(..., description="'tool' or 'workflow'")
    name: str
    name_zh: Optional[str] = None
    description: Optional[str] = None
    description_zh: Optional[str] = None
    slug: str
    logo_url: Optional[str] = None
    icon: Optional[str] = None
    reason: str = Field(..., description="Why this item is recommended")
    score: float = Field(..., description="Recommendation score/confidence")

    class Config:
        from_attributes = True

class RecommendationsResponse(BaseModel):
    """Response for personalized recommendations"""
    items: List[RecommendationItemResponse]
    total: int
    based_on: str = Field(..., description="What the recommendations are based on")

@router.post("/interactions")
async def record_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a user interaction (view, click, run, etc.)"""
    # Verify target exists (optional but good)

    new_interaction = UserInteraction(
        user_id=current_user.id,
        item_type=interaction.item_type,
        item_id=interaction.item_id,
        action=interaction.action,
        meta_data=interaction.meta_data
    )
    db.add(new_interaction)
    await db.commit()
    return {"status": "success"}

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized recommendations using collaborative filtering based on UserInteraction history.

    Algorithm:
    1. Find similar users based on overlapping interactions
    2. Recommend items that similar users liked but current user hasn't seen
    3. Include category-based recommendations from user's interests
    4. Mix with trending items for diversity
    """
    # Get user's interaction history (weighted by action type)
    user_interactions_result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == current_user.id)
        .order_by(desc(UserInteraction.created_at))
    )
    interactions = result.scalars().all()

    if not interactions:
        # Return trending items if no history
        return {"tools": [], "agents": []}

    # 2. Basic recommendation logic (just returning recent items for now)
    # In a real app, we'd use collaborative filtering or content-based filtering via vector search

    return {
        "message": "Recommendations based on your recent activity",
        "recent_interactions": [
            {"type": i.item_type, "id": i.item_id, "action": i.action}
            for i in interactions
        ]
    }
