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
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
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
    user_interactions = user_interactions_result.scalars().all()

    # Track items the user has already interacted with
    user_item_ids: Set[UUID] = {interaction.item_id for interaction in user_interactions}

    # If no history, return trending items
    if not user_interactions:
        trending_recs = await _get_trending_recommendations(db, limit, user_item_ids)
        recommendations = await _fetch_recommendation_details(db, trending_recs)
        return RecommendationsResponse(
            items=recommendations,
            total=len(recommendations),
            based_on="Trending items (no interaction history)"
        )

    # Step 1: Find similar users using collaborative filtering
    similar_user_scores = await _find_similar_users(db, current_user.id, user_interactions)

    # Step 2: Get recommendations from similar users
    collaborative_recs = await _get_collaborative_recommendations(
        db, similar_user_scores, user_item_ids, limit
    )

    # Step 3: Get category-based recommendations
    category_recs = await _get_category_based_recommendations(
        db, user_interactions, user_item_ids, limit
    )

    # Step 4: Get trending items for diversity
    trending_recs = await _get_trending_recommendations(db, limit // 2, user_item_ids)

    # Combine and rank recommendations
    combined_recs = _combine_recommendations(
        collaborative_recs, category_recs, trending_recs, limit
    )

    # Fetch full item details
    recommendations = await _fetch_recommendation_details(db, combined_recs)

    return RecommendationsResponse(
        items=recommendations,
        total=len(recommendations),
        based_on="Collaborative filtering, user interests, and trending items"
    )


async def _find_similar_users(
    db: AsyncSession,
    user_id: UUID,
    user_interactions: List[UserInteraction]
) -> Dict[UUID, float]:
    """
    Find users with similar interaction patterns using Jaccard similarity.
    Returns dict of user_id -> similarity_score
    """
    # Get items the current user has interacted with
    user_item_ids = {interaction.item_id for interaction in user_interactions}

    if not user_item_ids:
        return {}

    # Find other users who interacted with the same items
    other_users_result = await db.execute(
        select(UserInteraction)
        .where(
            and_(
                UserInteraction.item_id.in_(list(user_item_ids)),
                UserInteraction.user_id != user_id
            )
        )
    )
    other_interactions = other_users_result.scalars().all()

    # Group interactions by user
    user_items_map: Dict[UUID, Set[UUID]] = defaultdict(set)
    for interaction in other_interactions:
        user_items_map[interaction.user_id].add(interaction.item_id)

    # Calculate Jaccard similarity: |intersection| / |union|
    similarity_scores: Dict[UUID, float] = {}
    for other_user_id, other_items in user_items_map.items():
        intersection = len(user_item_ids & other_items)
        union = len(user_item_ids | other_items)
        if union > 0:
            similarity = intersection / union
            # Only consider users with at least 2 overlapping items
            if intersection >= 2:
                similarity_scores[other_user_id] = similarity

    return similarity_scores


async def _get_collaborative_recommendations(
    db: AsyncSession,
    similar_user_scores: Dict[UUID, float],
    user_item_ids: Set[UUID],
    limit: int
) -> List[Dict]:
    """
    Get recommendations from similar users' interactions.
    Returns list of dicts with item info and recommendation score.
    """
    if not similar_user_scores:
        return []

    # Get interactions from similar users
    similar_user_ids = list(similar_user_scores.keys())
    similar_interactions_result = await db.execute(
        select(UserInteraction)
        .where(
            and_(
                UserInteraction.user_id.in_(similar_user_ids),
                # Prioritize positive actions
                UserInteraction.action.in_(['star', 'run', 'fork', 'like'])
            )
        )
    )
    similar_interactions = similar_interactions_result.scalars().all()

    # Score items based on how many similar users interacted with them
    item_scores: Dict[UUID, Dict] = defaultdict(lambda: {"score": 0.0, "type": None, "reasons": []})

    action_weights = {'star': 2.0, 'fork': 1.8, 'run': 1.5, 'like': 1.2}

    for interaction in similar_interactions:
        # Skip items the user has already seen
        if interaction.item_id in user_item_ids:
            continue

        # Weight by user similarity and action type
        user_similarity = similar_user_scores.get(interaction.user_id, 0.0)
        action_weight = action_weights.get(interaction.action, 1.0)
        score = user_similarity * action_weight

        item_scores[interaction.item_id]["score"] += score
        item_scores[interaction.item_id]["type"] = interaction.item_type
        item_scores[interaction.item_id]["reasons"].append(f"Similar users {interaction.action}ed this")

    # Sort by score and return top items
    sorted_items = sorted(item_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:limit]

    return [
        {"item_id": item_id, "score": data["score"], "type": data["type"], "reason": data["reasons"][0]}
        for item_id, data in sorted_items
    ]


async def _get_category_based_recommendations(
    db: AsyncSession,
    user_interactions: List[UserInteraction],
    user_item_ids: Set[UUID],
    limit: int
) -> List[Dict]:
    """
    Recommend items from categories the user has shown interest in.
    """
    # Get tools the user has interacted with
    tool_interactions = [i for i in user_interactions if i.item_type == 'tool']
    if not tool_interactions:
        return []

    interacted_tool_ids = [i.item_id for i in tool_interactions[:20]]  # Recent 20 tools

    # Fetch categories of interacted tools
    tools_result = await db.execute(
        select(Tool)
        .where(Tool.id.in_(interacted_tool_ids))
    )
    tools = tools_result.scalars().all()

    # Count category frequencies
    category_counts: Dict[UUID, int] = defaultdict(int)
    for tool in tools:
        if tool.category_id:
            category_counts[tool.category_id] += 1

    if not category_counts:
        return []

    # Get top 3 categories
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_category_ids = [cat_id for cat_id, _ in top_categories]

    # Find tools in these categories that user hasn't seen
    category_tools_result = await db.execute(
        select(Tool)
        .where(
            and_(
                Tool.category_id.in_(top_category_ids),
                Tool.id.notin_(list(user_item_ids)) if user_item_ids else True
            )
        )
        .order_by(desc(Tool.avg_rating), desc(Tool.review_count))
        .limit(limit)
    )
    category_tools = category_tools_result.scalars().all()

    return [
        {
            "item_id": tool.id,
            "score": 0.8,  # Fixed score for category-based recs
            "type": "tool",
            "reason": "Based on your interest in similar tools"
        }
        for tool in category_tools
    ]


async def _get_trending_recommendations(
    db: AsyncSession,
    limit: int,
    user_item_ids: Set[UUID]
) -> List[Dict]:
    """
    Get trending/popular items that the user hasn't interacted with.
    """
    # Get trending tools
    trending_tools_result = await db.execute(
        select(Tool)
        .where(Tool.id.notin_(list(user_item_ids)) if user_item_ids else True)
        .order_by(desc(Tool.avg_rating), desc(Tool.review_count), desc(Tool.github_stars))
        .limit(limit // 2)
    )
    trending_tools = trending_tools_result.scalars().all()

    # Get trending workflows
    trending_workflows_result = await db.execute(
        select(AgentWorkflow)
        .where(
            and_(
                AgentWorkflow.is_public == True,
                AgentWorkflow.id.notin_(list(user_item_ids)) if user_item_ids else True
            )
        )
        .order_by(desc(AgentWorkflow.star_count), desc(AgentWorkflow.run_count))
        .limit(limit // 2)
    )
    trending_workflows = trending_workflows_result.scalars().all()

    recommendations = []

    for tool in trending_tools:
        recommendations.append({
            "item_id": tool.id,
            "score": 0.6,
            "type": "tool",
            "reason": "Trending tool with high ratings"
        })

    for workflow in trending_workflows:
        recommendations.append({
            "item_id": workflow.id,
            "score": 0.6,
            "type": "workflow",
            "reason": "Popular workflow in the community"
        })

    return recommendations


def _combine_recommendations(
    collaborative: List[Dict],
    category_based: List[Dict],
    trending: List[Dict],
    limit: int
) -> List[Dict]:
    """
    Combine different recommendation sources with proper mixing and deduplication.
    Returns list of recommendation dicts with item_id, score, type, and reason.
    """
    # Combine all recommendations
    all_recs: Dict[UUID, Dict] = {}

    # Add collaborative filtering results (highest priority)
    for rec in collaborative:
        item_id = rec["item_id"]
        if item_id not in all_recs:
            all_recs[item_id] = rec

    # Add category-based recommendations
    for rec in category_based:
        item_id = rec["item_id"]
        if item_id not in all_recs:
            all_recs[item_id] = rec

    # Add trending items for diversity
    for rec in trending:
        item_id = rec["item_id"]
        if item_id not in all_recs:
            all_recs[item_id] = rec

    # Sort by score and take top N
    sorted_recs = sorted(all_recs.values(), key=lambda x: x["score"], reverse=True)[:limit]

    return sorted_recs


async def _fetch_recommendation_details(
    db: AsyncSession,
    recommendations: List[Dict]
) -> List[RecommendationItemResponse]:
    """
    Fetch full details for recommended items and build response objects.
    """
    if not recommendations:
        return []

    # Separate tool and workflow IDs
    tool_ids = [rec["item_id"] for rec in recommendations if rec["type"] == "tool"]
    workflow_ids = [rec["item_id"] for rec in recommendations if rec["type"] == "workflow"]

    # Batch fetch tools
    tools_map = {}
    if tool_ids:
        tools_result = await db.execute(
            select(Tool).where(Tool.id.in_(tool_ids))
        )
        tools = tools_result.scalars().all()
        tools_map = {tool.id: tool for tool in tools}

    # Batch fetch workflows
    workflows_map = {}
    if workflow_ids:
        workflows_result = await db.execute(
            select(AgentWorkflow).where(AgentWorkflow.id.in_(workflow_ids))
        )
        workflows = workflows_result.scalars().all()
        workflows_map = {workflow.id: workflow for workflow in workflows}

    # Build recommendation response objects
    response_items = []
    for rec in recommendations:
        item_id = rec["item_id"]
        item_type = rec["type"]

        if item_type == "tool" and item_id in tools_map:
            tool = tools_map[item_id]
            response_items.append(RecommendationItemResponse(
                id=tool.id,
                type="tool",
                name=tool.name,
                name_zh=tool.name_zh,
                description=tool.description,
                description_zh=tool.description_zh,
                slug=tool.slug,
                logo_url=tool.logo_url,
                icon=None,
                reason=rec["reason"],
                score=rec["score"]
            ))
        elif item_type == "workflow" and item_id in workflows_map:
            workflow = workflows_map[item_id]
            response_items.append(RecommendationItemResponse(
                id=workflow.id,
                type="workflow",
                name=workflow.name,
                name_zh=workflow.name_zh,
                description=workflow.description,
                description_zh=workflow.description_zh,
                slug=workflow.slug,
                logo_url=None,
                icon=workflow.icon,
                reason=rec["reason"],
                score=rec["score"]
            ))

    return response_items
