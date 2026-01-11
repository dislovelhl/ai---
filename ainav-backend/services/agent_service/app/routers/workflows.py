"""
Workflows Router - CRUD operations for agent workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID, uuid4
import math
import re

from shared.models import AgentWorkflow, User
<<<<<<< HEAD
||||||| c16401e
from fastapi import APIRouter, Depends, HTTPException, Query, Body
=======
from ..dependencies import get_current_user_id, get_optional_user, get_db
from ..schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowSummary, PaginatedWorkflowsResponse
)
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
from ..core.planner_agent import PlannerAgent, GeneratedGraph
from ..dependencies import get_current_user_id, get_optional_current_user_id, get_current_active_user
from ..schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowSummary, PaginatedWorkflowsResponse
)

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
<<<<<<< HEAD
    user_id: Optional[UUID] = Depends(get_optional_current_user_id),
||||||| c16401e
    user_id: Optional[UUID] = None,  # TODO: Get from auth
=======
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    is_public: Optional[bool] = None,
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    List agent workflows with optional filtering.
<<<<<<< HEAD

    If authenticated, shows user's workflows + public workflows.
    If unauthenticated, shows public workflows only.
||||||| c16401e
=======
    Shows public workflows, plus authenticated user's private workflows.
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    """
    query = select(AgentWorkflow)
    count_query = select(func.count(AgentWorkflow.id))
<<<<<<< HEAD

    # If authenticated, show user's workflows + public workflows
    if user_id:
||||||| c16401e
    
    # For now, if no user_id provided, show public workflows only
    if user_id:
=======

    # If user is authenticated, show their workflows + public ones
    # If not authenticated, show only public workflows
    if current_user:
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
        query = query.where(
            (AgentWorkflow.user_id == current_user.id) |
            (AgentWorkflow.is_public == True)
        )
        count_query = count_query.where(
            (AgentWorkflow.user_id == current_user.id) |
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
    query = query.order_by(
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
<<<<<<< HEAD
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
=======
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    List current user's workflows (requires authentication).
    """
    query = select(AgentWorkflow).where(
        AgentWorkflow.user_id == user_id
    ).order_by(AgentWorkflow.updated_at.desc())
    count_query = select(func.count(AgentWorkflow.id)).where(
        AgentWorkflow.user_id == user_id
    )

    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

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
    db: AsyncSession = Depends(get_db),
):
    """
    List public/community workflows.
    """
    query = select(AgentWorkflow).where(AgentWorkflow.is_public == True)
    count_query = select(func.count(AgentWorkflow.id)).where(AgentWorkflow.is_public == True)
    
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
    
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    offset = (page - 1) * page_size
    query = query.order_by(
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
<<<<<<< HEAD
    user_id: Optional[UUID] = Depends(get_optional_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    db: AsyncSession = Depends(get_async_session),
=======
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Get a specific workflow by ID.
<<<<<<< HEAD

    Public workflows accessible without auth.
    Private workflows require authentication and ownership.
||||||| c16401e
=======
    Public workflows accessible to all, private workflows only to owner.
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
<<<<<<< HEAD

    # Check permissions: public workflows accessible to all, private only to owner
    if not workflow.is_public:
        if not user_id:
            raise HTTPException(status_code=403, detail="Authentication required to access private workflow")
        if workflow.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this workflow")

||||||| c16401e
    
    # TODO: Check permissions (owner or public)
    
=======

    # Check permissions: must be public or owned by current user
    if not workflow.is_public:
        if not current_user or workflow.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    return WorkflowResponse.model_validate(workflow)


@router.get("/by-slug/{slug}", response_model=WorkflowResponse)
async def get_workflow_by_slug(
    slug: str,
<<<<<<< HEAD
    user_id: Optional[UUID] = Depends(get_optional_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    db: AsyncSession = Depends(get_async_session),
=======
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Get a specific workflow by slug.
<<<<<<< HEAD

    Public workflows accessible without auth.
    Private workflows require authentication and ownership.
||||||| c16401e
=======
    Public workflows accessible to all, private workflows only to owner.
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.slug == slug)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
<<<<<<< HEAD

    # Check permissions: public workflows accessible to all, private only to owner
    if not workflow.is_public:
        if not user_id:
            raise HTTPException(status_code=403, detail="Authentication required to access private workflow")
        if workflow.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this workflow")

||||||| c16401e
    
=======

    # Check permissions: must be public or owned by current user
    if not workflow.is_public:
        if not current_user or workflow.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    return WorkflowResponse.model_validate(workflow)


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowCreate,
<<<<<<< HEAD
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
=======
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Create a new agent workflow (requires authentication).
    """
    # Check slug uniqueness
    existing = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.slug == workflow_data.slug)
    )
    if existing.scalar_one_or_none():
        # Append unique suffix
        workflow_data.slug = f"{workflow_data.slug}-{str(uuid4())[:8]}"

    # Convert graph_json from Pydantic model to dict
    data = workflow_data.model_dump()
    data['graph_json'] = workflow_data.graph_json.model_dump()
    data['user_id'] = user_id

    workflow = AgentWorkflow(**data)
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
<<<<<<< HEAD
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    db: AsyncSession = Depends(get_async_session),
=======
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Update an existing workflow (requires authentication).
    Increments version and records history when graph changes.
    """
    from datetime import datetime

    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
<<<<<<< HEAD

    # Verify ownership
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workflow")
||||||| c16401e
    
    # TODO: Check ownership
=======

    # Check ownership
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workflow")
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    
    update_data = workflow_data.model_dump(exclude_unset=True)
    
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
    
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    await db.commit()
    await db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
<<<<<<< HEAD
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    db: AsyncSession = Depends(get_async_session),
=======
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Delete a workflow (requires authentication and ownership).
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
<<<<<<< HEAD

    # Verify ownership
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workflow")

||||||| c16401e
    
    # TODO: Check ownership
    
=======

    # Check ownership
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workflow")

>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
    await db.delete(workflow)
    await db.commit()


@router.post("/{workflow_id}/fork", response_model=WorkflowResponse, status_code=201)
async def fork_workflow(
    workflow_id: UUID,
<<<<<<< HEAD
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session),
||||||| c16401e
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
=======
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
>>>>>>> auto-claude/004-consistent-user-id-handling-across-services
):
    """
    Fork (clone) a public workflow to user's collection (requires authentication).
    """
    # Get original workflow
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if not original.is_public:
        raise HTTPException(status_code=403, detail="Cannot fork private workflow")

    # Create fork
    forked = AgentWorkflow(
        user_id=user_id,
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
    )
    
    db.add(forked)
    
    # Increment fork count on original
    original.fork_count += 1
    
    await db.commit()
    await db.refresh(forked)
    
    return WorkflowResponse.model_validate(forked)


@router.post("/{workflow_id}/star", status_code=200)
async def star_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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
