from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from ..dependencies import get_db, get_current_active_user
from shared.models import (
    User,
    UserInteraction,
    Tool,
    AgentWorkflow,
    AgentExecution
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ============================================================================
# Pydantic Schemas for Dashboard Responses
# ============================================================================

class ActivityItemResponse(BaseModel):
    """Individual activity item in the feed"""
    id: UUID
    item_type: str = Field(..., description="Type of item: 'tool', 'agent', 'roadmap'")
    item_id: UUID
    item_name: Optional[str] = Field(None, description="Name of the interacted item")
    item_name_zh: Optional[str] = None
    action: str = Field(..., description="Action type: 'view', 'click', 'run', 'like', 'fork', 'star'")
    timestamp: datetime
    meta_data: Optional[dict] = None

    class Config:
        from_attributes = True


class ActivityFeedResponse(BaseModel):
    """Response for recent activity feed"""
    total: int
    items: List[ActivityItemResponse]
    page: int
    page_size: int


class SavedToolResponse(BaseModel):
    """Saved/starred tool information"""
    id: UUID
    name: str
    name_zh: Optional[str] = None
    description: Optional[str] = None
    description_zh: Optional[str] = None
    slug: str
    url: str
    logo_url: Optional[str] = None
    pricing_type: Optional[str] = None
    is_china_accessible: bool
    requires_vpn: bool
    starred_at: datetime

    class Config:
        from_attributes = True


class SavedWorkflowResponse(BaseModel):
    """Saved/starred workflow information"""
    id: UUID
    name: str
    name_zh: Optional[str] = None
    description: Optional[str] = None
    description_zh: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    is_public: bool = False
    starred_at: datetime

    class Config:
        from_attributes = True


class SavedItemsResponse(BaseModel):
    """Response for all saved/starred items"""
    tools: List[SavedToolResponse]
    workflows: List[SavedWorkflowResponse]
    total_count: int


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


class LearningPathProgress(BaseModel):
    """Progress for a single learning path"""
    path_id: UUID
    path_name: str
    path_name_zh: Optional[str] = None
    total_items: int
    completed_items: int
    progress_percentage: float
    last_activity: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningProgressResponse(BaseModel):
    """Response for overall learning progress"""
    paths: List[LearningPathProgress]
    overall_progress: float = Field(..., description="Overall learning progress percentage")
    total_paths: int
    completed_paths: int
    active_paths: int


class WorkflowExecutionSummary(BaseModel):
    """Summary of a workflow execution"""
    id: UUID
    workflow_id: UUID
    workflow_name: str
    workflow_name_zh: Optional[str] = None
    status: str = Field(..., description="'pending', 'running', 'completed', 'failed', 'cancelled'")
    created_at: datetime
    updated_at: datetime
    duration_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class RecentExecutionsResponse(BaseModel):
    """Response for recent workflow executions"""
    executions: List[WorkflowExecutionSummary]
    total: int
    page: int
    page_size: int


class DashboardStatsResponse(BaseModel):
    """Overall dashboard statistics"""
    total_workflows: int
    total_executions: int
    total_starred_items: int
    total_interactions: int
    recent_activity_count: int


class ToggleStarRequest(BaseModel):
    """Request to star/unstar an item"""
    item_type: str = Field(..., description="'tool' or 'workflow'")
    item_id: UUID


class ToggleStarResponse(BaseModel):
    """Response after toggling star status"""
    success: bool
    starred: bool = Field(..., description="New starred status")
    item_type: str
    item_id: UUID


# ============================================================================
# Dashboard Endpoints (Implementation stubs - to be completed in later tasks)
# ============================================================================

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall dashboard statistics for the current user.
    """
    # Count user's workflows
    workflows_result = await db.execute(
        select(func.count(AgentWorkflow.id))
        .where(AgentWorkflow.user_id == current_user.id)
    )
    total_workflows = workflows_result.scalar() or 0

    # Count user's executions
    executions_result = await db.execute(
        select(func.count(AgentExecution.id))
        .where(AgentExecution.user_id == current_user.id)
    )
    total_executions = executions_result.scalar() or 0

    # Count starred items (interactions with action='star')
    starred_result = await db.execute(
        select(func.count(UserInteraction.id))
        .where(
            and_(
                UserInteraction.user_id == current_user.id,
                UserInteraction.action == 'star'
            )
        )
    )
    total_starred = starred_result.scalar() or 0

    # Count total interactions
    interactions_result = await db.execute(
        select(func.count(UserInteraction.id))
        .where(UserInteraction.user_id == current_user.id)
    )
    total_interactions = interactions_result.scalar() or 0

    # Count recent activity (last 7 days is handled in activity endpoint)
    # For now, just use total interactions
    recent_activity_count = total_interactions

    return DashboardStatsResponse(
        total_workflows=total_workflows,
        total_executions=total_executions,
        total_starred_items=total_starred,
        total_interactions=total_interactions,
        recent_activity_count=recent_activity_count
    )


# Note: The following endpoints will be implemented in subsequent subtasks:
# - GET /activity - Get recent activity feed (subtask 1.2)
# - GET /saved - Get saved/starred items (subtask 1.3)
# - POST /star - Toggle star status (subtask 1.3)
# - GET /recommendations - Get personalized recommendations (subtask 1.4)
# - GET /learning-progress - Get learning progress (subtask 1.5)
# - GET /executions - Get recent workflow executions
