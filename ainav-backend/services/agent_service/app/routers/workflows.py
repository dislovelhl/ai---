"""
Workflows Router - CRUD operations for agent workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID, uuid4
import math
import re

from shared.database import get_async_session
from shared.models import AgentWorkflow, User
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from ..core.planner_agent import PlannerAgent, GeneratedGraph

router = APIRouter()
planner = PlannerAgent()

@router.post("/generate", response_model=GeneratedGraph)
async def generate_workflow_graph(
    payload: dict = Body(...),
):
    """
    Generate or refine a workflow graph structure from natural language.
    """
    prompt = payload.get("prompt")
    current_graph = payload.get("current_graph")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    return await planner.plan_workflow(prompt, current_graph)




def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from name."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug[:200]


@router.get("", response_model=PaginatedWorkflowsResponse)
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = None,  # TODO: Get from auth
    is_public: Optional[bool] = None,
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List agent workflows with optional filtering.
    """
    query = select(AgentWorkflow)
    count_query = select(func.count(AgentWorkflow.id))
    
    # For now, if no user_id provided, show public workflows only
    if user_id:
        query = query.where(
            (AgentWorkflow.user_id == user_id) |
            (AgentWorkflow.is_public == True)
        )
        count_query = count_query.where(
            (AgentWorkflow.user_id == user_id) |
            (AgentWorkflow.is_public == True)
        )
    else:
        query = query.where(AgentWorkflow.is_public == True)
        count_query = count_query.where(AgentWorkflow.is_public == True)
    
    if is_public is not None:
        query = query.where(AgentWorkflow.is_public == is_public)
        count_query = count_query.where(AgentWorkflow.is_public == is_public)
    
    if is_template is not None:
        query = query.where(AgentWorkflow.is_template == is_template)
        count_query = count_query.where(AgentWorkflow.is_template == is_template)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (AgentWorkflow.name.ilike(search_filter)) |
            (AgentWorkflow.name_zh.ilike(search_filter)) |
            (AgentWorkflow.description.ilike(search_filter))
        )
        count_query = count_query.where(
            (AgentWorkflow.name.ilike(search_filter)) |
            (AgentWorkflow.name_zh.ilike(search_filter)) |
            (AgentWorkflow.description.ilike(search_filter))
        )
    
    # Get total count
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Paginate and order by popularity (run_count + star_count)
    offset = (page - 1) * page_size
    query = query.options(selectinload(AgentWorkflow.tags)).order_by(
        (AgentWorkflow.run_count + AgentWorkflow.star_count).desc(),
        AgentWorkflow.created_at.desc()
    ).offset(offset).limit(page_size)

    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return PaginatedWorkflowsResponse(
        items=[WorkflowSummary.model_validate(w) for w in workflows],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/my", response_model=PaginatedWorkflowsResponse)
async def list_my_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
):
    """
    List current user's workflows.
    """
    # TODO: Get user_id from auth token
    # For now, return empty or all for testing
    query = select(AgentWorkflow).order_by(AgentWorkflow.updated_at.desc())
    count_query = select(func.count(AgentWorkflow.id))

    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    offset = (page - 1) * page_size
    query = query.options(selectinload(AgentWorkflow.tags)).offset(offset).limit(page_size)

    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return PaginatedWorkflowsResponse(
        items=[WorkflowSummary.model_validate(w) for w in workflows],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/public", response_model=PaginatedWorkflowsResponse)
async def list_public_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_template: Optional[bool] = None,
    category_id: Optional[UUID] = None,
    tag_ids: Optional[list[UUID]] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    List public/community workflows with optional filtering by category and tags.
    """
    from shared.models import WorkflowTag, workflow_workflow_tags

    query = select(AgentWorkflow).where(AgentWorkflow.is_public == True)
    count_query = select(func.count(AgentWorkflow.id)).where(AgentWorkflow.is_public == True)

    if is_template is not None:
        query = query.where(AgentWorkflow.is_template == is_template)
        count_query = count_query.where(AgentWorkflow.is_template == is_template)

    if category_id is not None:
        query = query.where(AgentWorkflow.category_id == category_id)
        count_query = count_query.where(AgentWorkflow.category_id == category_id)

    if tag_ids is not None and len(tag_ids) > 0:
        # Join with the junction table to filter by tags
        # Workflows must have ALL specified tags (AND logic)
        query = query.join(
            workflow_workflow_tags,
            AgentWorkflow.id == workflow_workflow_tags.c.workflow_id
        ).where(
            workflow_workflow_tags.c.tag_id.in_(tag_ids)
        ).group_by(AgentWorkflow.id).having(
            func.count(workflow_workflow_tags.c.tag_id) == len(tag_ids)
        )

        count_query = count_query.join(
            workflow_workflow_tags,
            AgentWorkflow.id == workflow_workflow_tags.c.workflow_id
        ).where(
            workflow_workflow_tags.c.tag_id.in_(tag_ids)
        ).group_by(AgentWorkflow.id).having(
            func.count(workflow_workflow_tags.c.tag_id) == len(tag_ids)
        )

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (AgentWorkflow.name.ilike(search_filter)) |
            (AgentWorkflow.name_zh.ilike(search_filter)) |
            (AgentWorkflow.description.ilike(search_filter))
        )
        count_query = count_query.where(
            (AgentWorkflow.name.ilike(search_filter)) |
            (AgentWorkflow.name_zh.ilike(search_filter)) |
            (AgentWorkflow.description.ilike(search_filter))
        )

    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    offset = (page - 1) * page_size
    query = query.options(selectinload(AgentWorkflow.tags)).order_by(
        AgentWorkflow.star_count.desc(),
        AgentWorkflow.run_count.desc()
    ).offset(offset).limit(page_size)

    result = await db.execute(query)
    workflows = result.scalars().all()

    return PaginatedWorkflowsResponse(
        items=[WorkflowSummary.model_validate(w) for w in workflows],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific workflow by ID.
    """
    result = await db.execute(
        select(AgentWorkflow)
        .options(selectinload(AgentWorkflow.tags))
        .where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check permissions (owner or public)

    return WorkflowResponse.model_validate(workflow)


@router.get("/by-slug/{slug}", response_model=WorkflowResponse)
async def get_workflow_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific workflow by slug.
    """
    result = await db.execute(
        select(AgentWorkflow)
        .options(selectinload(AgentWorkflow.tags))
        .where(AgentWorkflow.slug == slug)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return WorkflowResponse.model_validate(workflow)


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowCreate,
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new agent workflow.
    """
    from shared.models import WorkflowTag

    # TODO: Get user_id from auth
    # For now, use a placeholder or first user
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="No user available. Please create a user first.")

    # Check slug uniqueness
    existing = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.slug == workflow_data.slug)
    )
    if existing.scalar_one_or_none():
        # Append unique suffix
        workflow_data.slug = f"{workflow_data.slug}-{str(uuid4())[:8]}"

    # Convert graph_json from Pydantic model to dict and extract tag_ids
    data = workflow_data.model_dump(exclude={'tag_ids'})
    data['graph_json'] = workflow_data.graph_json.model_dump()
    data['user_id'] = user.id

    workflow = AgentWorkflow(**data)

    # Handle tags if provided
    if workflow_data.tag_ids:
        tag_result = await db.execute(
            select(WorkflowTag).where(WorkflowTag.id.in_(workflow_data.tag_ids))
        )
        tags = tag_result.scalars().all()
        workflow.tags = tags

    db.add(workflow)
    await db.commit()
    await db.refresh(workflow, attribute_names=['tags'])

    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing workflow.
    Increments version and records history when graph changes.
    """
    from datetime import datetime
    from shared.models import WorkflowTag

    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check ownership

    update_data = workflow_data.model_dump(exclude_unset=True, exclude={'tag_ids'})

    # Handle graph_json conversion if present and track versioning
    if 'graph_json' in update_data and update_data['graph_json']:
        update_data['graph_json'] = workflow_data.graph_json.model_dump()

        # Increment version and record history
        workflow.version = (workflow.version or 1) + 1
        history_entry = {
            "version": workflow.version,
            "timestamp": datetime.utcnow().isoformat(),
            "changes": "Graph updated"
        }
        if workflow.version_history is None:
            workflow.version_history = []
        workflow.version_history = workflow.version_history + [history_entry]

    # Handle tags update if provided
    if workflow_data.tag_ids is not None:
        tag_result = await db.execute(
            select(WorkflowTag).where(WorkflowTag.id.in_(workflow_data.tag_ids))
        )
        tags = tag_result.scalars().all()
        workflow.tags = tags

    for field, value in update_data.items():
        setattr(workflow, field, value)

    await db.commit()
    await db.refresh(workflow, attribute_names=['tags'])

    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a workflow.
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # TODO: Check ownership
    
    await db.delete(workflow)
    await db.commit()


@router.post("/{workflow_id}/fork", response_model=WorkflowResponse, status_code=201)
async def fork_workflow(
    workflow_id: UUID,
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
):
    """
    Fork (clone) a public workflow to user's collection.
    """
    # Get original workflow with tags
    result = await db.execute(
        select(AgentWorkflow)
        .options(selectinload(AgentWorkflow.tags))
        .where(AgentWorkflow.id == workflow_id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if not original.is_public:
        raise HTTPException(status_code=403, detail="Cannot fork private workflow")

    # TODO: Get user_id from auth
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="No user available")

    # Create fork
    forked = AgentWorkflow(
        user_id=user.id,
        name=f"{original.name} (Fork)",
        name_zh=f"{original.name_zh} (Fork)" if original.name_zh else None,
        slug=f"{original.slug}-fork-{str(uuid4())[:8]}",
        description=original.description,
        description_zh=original.description_zh,
        icon=original.icon,
        graph_json=original.graph_json,
        trigger_type=original.trigger_type,
        trigger_config=original.trigger_config,
        input_schema=original.input_schema,
        llm_model=original.llm_model,
        system_prompt=original.system_prompt,
        temperature=original.temperature,
        is_public=False,  # Forks start as private
        forked_from_id=original.id,
        category_id=original.category_id,  # Preserve category
    )

    # Preserve tags
    forked.tags = original.tags

    db.add(forked)

    # Increment fork count on original
    original.fork_count += 1

    await db.commit()
    await db.refresh(forked, attribute_names=['tags'])

    return WorkflowResponse.model_validate(forked)


@router.post("/{workflow_id}/star", status_code=200)
async def star_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Star/upvote a workflow.
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # TODO: Track user stars to prevent duplicate starring
    workflow.star_count += 1
    await db.commit()
    
    return {"star_count": workflow.star_count}


@router.get("/{workflow_id}/versions")
async def get_workflow_versions(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get version history for a workflow.
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "workflow_id": str(workflow.id),
        "current_version": workflow.version or 1,
        "history": workflow.version_history or []
    }
