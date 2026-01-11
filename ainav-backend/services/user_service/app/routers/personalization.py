from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ..dependencies import get_db, get_current_active_user
from shared.models import UserInteraction, Tool, AgentWorkflow, User

router = APIRouter()

class InteractionCreate(BaseModel):
    item_type: str
    item_id: UUID
    action: str
    meta_data: Optional[dict] = None

class RecommendationResponse(BaseModel):
    tools: List[dict]
    agents: List[dict]

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

@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized recommendations based on interaction history.
    Simple heuristic: recently interacted categories/tags.
    """
    # 1. Get recent interactions
    result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == current_user.id)
        .order_by(desc(UserInteraction.created_at))
        .limit(20)
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
