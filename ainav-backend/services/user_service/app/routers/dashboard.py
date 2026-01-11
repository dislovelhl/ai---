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


@router.get("/activity", response_model=ActivityFeedResponse)
async def get_recent_activity(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent user activity feed with pagination.

    Returns a paginated list of recent user interactions (views, clicks, runs, likes, etc.)
    with details about the interacted items (tools, workflows, etc.).
    """
    # Calculate offset for pagination
    offset = (page - 1) * page_size

    # Get total count of user interactions
    count_result = await db.execute(
        select(func.count(UserInteraction.id))
        .where(UserInteraction.user_id == current_user.id)
    )
    total = count_result.scalar() or 0

    # Fetch paginated interactions ordered by most recent first
    interactions_result = await db.execute(
        select(UserInteraction)
        .where(UserInteraction.user_id == current_user.id)
        .order_by(desc(UserInteraction.created_at))
        .limit(page_size)
        .offset(offset)
    )
    interactions = interactions_result.scalars().all()

    if not interactions:
        return ActivityFeedResponse(
            total=total,
            items=[],
            page=page,
            page_size=page_size
        )

    # Group item IDs by type for batch fetching
    tool_ids = []
    workflow_ids = []

    for interaction in interactions:
        if interaction.item_type == 'tool':
            tool_ids.append(interaction.item_id)
        elif interaction.item_type == 'agent':
            workflow_ids.append(interaction.item_id)
        # Note: 'roadmap' type doesn't have a table yet, will be handled later

    # Batch fetch tools
    tools_map = {}
    if tool_ids:
        tools_result = await db.execute(
            select(Tool)
            .where(Tool.id.in_(tool_ids))
        )
        tools = tools_result.scalars().all()
        tools_map = {tool.id: tool for tool in tools}

    # Batch fetch workflows
    workflows_map = {}
    if workflow_ids:
        workflows_result = await db.execute(
            select(AgentWorkflow)
            .where(AgentWorkflow.id.in_(workflow_ids))
        )
        workflows = workflows_result.scalars().all()
        workflows_map = {workflow.id: workflow for workflow in workflows}

    # Build activity items with item details
    activity_items = []
    for interaction in interactions:
        item_name = None
        item_name_zh = None

        if interaction.item_type == 'tool':
            tool = tools_map.get(interaction.item_id)
            if tool:
                item_name = tool.name
                item_name_zh = tool.name_zh
        elif interaction.item_type == 'agent':
            workflow = workflows_map.get(interaction.item_id)
            if workflow:
                item_name = workflow.name
                item_name_zh = workflow.name_zh
        # For roadmap or other types, item_name will be None for now

        activity_item = ActivityItemResponse(
            id=interaction.id,
            item_type=interaction.item_type,
            item_id=interaction.item_id,
            item_name=item_name,
            item_name_zh=item_name_zh,
            action=interaction.action,
            timestamp=interaction.created_at,
            meta_data=interaction.meta_data
        )
        activity_items.append(activity_item)

    return ActivityFeedResponse(
        total=total,
        items=activity_items,
        page=page,
        page_size=page_size
    )


@router.get("/saved", response_model=SavedItemsResponse)
async def get_saved_items(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all saved/starred tools and workflows for the current user.

    Returns tools and workflows that the user has starred, grouped by type.
    """
    # Query all starred interactions for this user
    starred_result = await db.execute(
        select(UserInteraction)
        .where(
            and_(
                UserInteraction.user_id == current_user.id,
                UserInteraction.action == 'star'
            )
        )
        .order_by(desc(UserInteraction.created_at))
    )
    starred_interactions = starred_result.scalars().all()

    # Separate tool IDs and workflow IDs
    tool_ids = [
        interaction.item_id
        for interaction in starred_interactions
        if interaction.item_type == 'tool'
    ]
    workflow_ids = [
        interaction.item_id
        for interaction in starred_interactions
        if interaction.item_type == 'agent'
    ]

    # Create timestamp maps for starred_at dates
    tool_starred_at = {
        interaction.item_id: interaction.created_at
        for interaction in starred_interactions
        if interaction.item_type == 'tool'
    }
    workflow_starred_at = {
        interaction.item_id: interaction.created_at
        for interaction in starred_interactions
        if interaction.item_type == 'agent'
    }

    # Fetch tools
    saved_tools = []
    if tool_ids:
        tools_result = await db.execute(
            select(Tool)
            .where(Tool.id.in_(tool_ids))
        )
        tools = tools_result.scalars().all()

        for tool in tools:
            saved_tools.append(SavedToolResponse(
                id=tool.id,
                name=tool.name,
                name_zh=tool.name_zh,
                description=tool.description,
                description_zh=tool.description_zh,
                slug=tool.slug,
                url=tool.url,
                logo_url=tool.logo_url,
                pricing_type=tool.pricing_type,
                is_china_accessible=tool.is_china_accessible,
                requires_vpn=tool.requires_vpn,
                starred_at=tool_starred_at[tool.id]
            ))

    # Fetch workflows
    saved_workflows = []
    if workflow_ids:
        workflows_result = await db.execute(
            select(AgentWorkflow)
            .where(AgentWorkflow.id.in_(workflow_ids))
        )
        workflows = workflows_result.scalars().all()

        for workflow in workflows:
            saved_workflows.append(SavedWorkflowResponse(
                id=workflow.id,
                name=workflow.name,
                name_zh=workflow.name_zh,
                description=workflow.description,
                description_zh=workflow.description_zh,
                slug=workflow.slug,
                icon=workflow.icon,
                is_public=workflow.is_public,
                starred_at=workflow_starred_at[workflow.id]
            ))

    return SavedItemsResponse(
        tools=saved_tools,
        workflows=saved_workflows,
        total_count=len(saved_tools) + len(saved_workflows)
    )


@router.post("/star", response_model=ToggleStarResponse)
async def toggle_star(
    request: ToggleStarRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle star status for a tool or workflow.

    If the item is not starred, create a star interaction.
    If the item is already starred, remove the star interaction.
    """
    # Check if item is already starred
    existing_star_result = await db.execute(
        select(UserInteraction)
        .where(
            and_(
                UserInteraction.user_id == current_user.id,
                UserInteraction.item_type == request.item_type,
                UserInteraction.item_id == request.item_id,
                UserInteraction.action == 'star'
            )
        )
    )
    existing_star = existing_star_result.scalar_one_or_none()

    if existing_star:
        # Unstar: Remove the interaction
        await db.delete(existing_star)
        await db.commit()

        # Update star count on the item if it's a workflow
        if request.item_type == 'agent':
            workflow_result = await db.execute(
                select(AgentWorkflow)
                .where(AgentWorkflow.id == request.item_id)
            )
            workflow = workflow_result.scalar_one_or_none()
            if workflow and workflow.star_count > 0:
                workflow.star_count -= 1
                await db.commit()

        return ToggleStarResponse(
            success=True,
            starred=False,
            item_type=request.item_type,
            item_id=request.item_id
        )
    else:
        # Star: Create new interaction
        new_star = UserInteraction(
            user_id=current_user.id,
            item_type=request.item_type,
            item_id=request.item_id,
            action='star',
            weight=1.0
        )
        db.add(new_star)
        await db.commit()

        # Update star count on the item if it's a workflow
        if request.item_type == 'agent':
            workflow_result = await db.execute(
                select(AgentWorkflow)
                .where(AgentWorkflow.id == request.item_id)
            )
            workflow = workflow_result.scalar_one_or_none()
            if workflow:
                workflow.star_count += 1
                await db.commit()

        return ToggleStarResponse(
            success=True,
            starred=True,
            item_type=request.item_type,
            item_id=request.item_id
        )


@router.get("/learning-progress", response_model=LearningProgressResponse)
async def get_learning_progress(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get learning progress tracking for roadmaps, learning paths, and prompts.

    Tracks user completion of learning content based on UserInteraction records
    with item_type='roadmap' or 'prompt'.

    Note: This endpoint is prepared for future learning path infrastructure.
    Currently returns empty results as Roadmap/LearningPath models don't exist yet.
    Once those models are added, this endpoint will be enhanced to return actual progress.
    """
    # Query UserInteractions for learning-related items
    # Using item_type='roadmap' as per the design (prompts could be a future item_type)
    learning_interactions_result = await db.execute(
        select(UserInteraction)
        .where(
            and_(
                UserInteraction.user_id == current_user.id,
                UserInteraction.item_type.in_(['roadmap', 'prompt'])
            )
        )
        .order_by(desc(UserInteraction.created_at))
    )
    learning_interactions = learning_interactions_result.scalars().all()

    # Group interactions by item_id to track progress per learning path
    # Key: item_id, Value: list of interactions for that path
    path_interactions = {}
    for interaction in learning_interactions:
        if interaction.item_id not in path_interactions:
            path_interactions[interaction.item_id] = []
        path_interactions[interaction.item_id].append(interaction)

    # Build learning path progress
    # TODO: Once Roadmap/LearningPath models are added, fetch actual path details
    # For now, we'll return an empty list since those models don't exist yet
    learning_paths = []

    # Future implementation (when Roadmap model exists):
    # 1. Fetch Roadmap records by IDs from path_interactions.keys()
    # 2. For each roadmap:
    #    - Count total items (steps/lessons in the roadmap)
    #    - Count completed items (interactions with action='complete' or 'finished')
    #    - Calculate progress_percentage
    #    - Get last_activity timestamp from most recent interaction
    # 3. Build LearningPathProgress objects
    #
    # Example future code:
    # if path_interactions:
    #     roadmap_ids = list(path_interactions.keys())
    #     roadmaps_result = await db.execute(
    #         select(Roadmap).where(Roadmap.id.in_(roadmap_ids))
    #     )
    #     roadmaps = roadmaps_result.scalars().all()
    #
    #     for roadmap in roadmaps:
    #         interactions = path_interactions[roadmap.id]
    #         completed_count = sum(1 for i in interactions if i.action in ['complete', 'finished'])
    #         total_items = roadmap.total_steps or 10  # From roadmap.total_steps
    #         progress_pct = (completed_count / total_items * 100) if total_items > 0 else 0
    #
    #         learning_paths.append(LearningPathProgress(
    #             path_id=roadmap.id,
    #             path_name=roadmap.name,
    #             path_name_zh=roadmap.name_zh,
    #             total_items=total_items,
    #             completed_items=completed_count,
    #             progress_percentage=progress_pct,
    #             last_activity=max(i.created_at for i in interactions)
    #         ))

    # Calculate overall statistics
    total_paths = len(learning_paths)
    completed_paths = sum(1 for path in learning_paths if path.progress_percentage >= 100.0)
    active_paths = sum(1 for path in learning_paths if 0 < path.progress_percentage < 100.0)

    # Calculate overall progress percentage
    if total_paths > 0:
        overall_progress = sum(path.progress_percentage for path in learning_paths) / total_paths
    else:
        overall_progress = 0.0

    return LearningProgressResponse(
        paths=learning_paths,
        overall_progress=overall_progress,
        total_paths=total_paths,
        completed_paths=completed_paths,
        active_paths=active_paths
    )


# Note: The following endpoints will be implemented in subsequent subtasks:
# - GET /executions - Get recent workflow executions
