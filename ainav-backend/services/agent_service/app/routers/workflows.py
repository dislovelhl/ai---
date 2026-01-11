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
from ..schemas import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowSummary,
    PaginatedWorkflowsResponse,
    WorkflowRevert,
    VersionComparison,
    VersionSnapshot,
    NodeDiff,
    EdgeDiff,
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
    db: AsyncSession = Depends(get_async_session),
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
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific workflow by ID.
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
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
        select(AgentWorkflow).where(AgentWorkflow.slug == slug)
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
    
    # Convert graph_json from Pydantic model to dict
    data = workflow_data.model_dump()
    data['graph_json'] = workflow_data.graph_json.model_dump()
    data['user_id'] = user.id
    
    workflow = AgentWorkflow(**data)
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing workflow.
    Increments version and records complete graph snapshot in history when graph changes.
    """
    from datetime import datetime

    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check ownership

    update_data = workflow_data.model_dump(exclude_unset=True)

    # Handle graph_json conversion if present and track versioning
    if 'graph_json' in update_data and update_data['graph_json']:
        # Save the CURRENT graph state to version history BEFORE updating
        current_version = workflow.version or 1
        history_entry = {
            "version": current_version,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": workflow_data.version_notes or "Graph updated",
            "graph_json": workflow.graph_json,  # Save the current (old) graph
            "user_id": str(workflow.user_id)
        }

        # Initialize version_history if needed
        if workflow.version_history is None:
            workflow.version_history = []

        # Append the current version snapshot to history
        workflow.version_history = workflow.version_history + [history_entry]

        # Now increment version and apply the new graph
        workflow.version = current_version + 1
        update_data['graph_json'] = workflow_data.graph_json.model_dump()

    # Apply all updates
    for field, value in update_data.items():
        setattr(workflow, field, value)

    await db.commit()
    await db.refresh(workflow)

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
    # Get original workflow
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
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


@router.post("/{workflow_id}/revert", response_model=WorkflowResponse)
async def revert_workflow_version(
    workflow_id: UUID,
    revert_data: WorkflowRevert,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Revert a workflow to a previous version.
    Creates a new version entry documenting the revert operation.
    """
    from datetime import datetime

    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check ownership

    # Find the target version in history
    target_version = revert_data.target_version
    version_history = workflow.version_history or []

    target_snapshot = None
    for entry in version_history:
        if entry.get("version") == target_version:
            target_snapshot = entry
            break

    if not target_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Version {target_version} not found in workflow history"
        )

    # Save the CURRENT state to version history before reverting
    current_version = workflow.version or 1
    history_entry = {
        "version": current_version,
        "timestamp": datetime.utcnow().isoformat(),
        "notes": f"Version before reverting to v{target_version}",
        "graph_json": workflow.graph_json,
        "user_id": str(workflow.user_id)
    }

    # Append current state to history
    workflow.version_history = version_history + [history_entry]

    # Revert to the target version's graph_json
    workflow.graph_json = target_snapshot.get("graph_json")

    # Increment version number
    workflow.version = current_version + 1

    await db.commit()
    await db.refresh(workflow)

    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}/versions/compare", response_model=VersionComparison)
async def compare_workflow_versions(
    workflow_id: UUID,
    v1: int = Query(..., ge=1, description="First version number to compare"),
    v2: int = Query(..., ge=1, description="Second version number to compare"),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Compare two versions of a workflow.
    Returns both version snapshots with detailed differences in nodes and edges.
    """
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check permissions

    version_history = workflow.version_history or []

    # Find both version snapshots
    v1_snapshot = None
    v2_snapshot = None

    for entry in version_history:
        if entry.get("version") == v1:
            v1_snapshot = entry
        if entry.get("version") == v2:
            v2_snapshot = entry

    if not v1_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Version {v1} not found in workflow history"
        )

    if not v2_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Version {v2} not found in workflow history"
        )

    # Extract nodes and edges from both versions
    v1_graph = v1_snapshot.get("graph_json", {})
    v2_graph = v2_snapshot.get("graph_json", {})

    v1_nodes = {node["id"]: node for node in v1_graph.get("nodes", [])}
    v2_nodes = {node["id"]: node for node in v2_graph.get("nodes", [])}

    v1_edges = {edge["id"]: edge for edge in v1_graph.get("edges", [])}
    v2_edges = {edge["id"]: edge for edge in v2_graph.get("edges", [])}

    # Compare nodes
    nodes_added = []
    nodes_removed = []
    nodes_modified = []

    # Find added and modified nodes
    for node_id, node_data in v2_nodes.items():
        if node_id not in v1_nodes:
            nodes_added.append(NodeDiff(
                node_id=node_id,
                change_type="added",
                new_data=node_data
            ))
        elif node_data != v1_nodes[node_id]:
            nodes_modified.append(NodeDiff(
                node_id=node_id,
                change_type="modified",
                old_data=v1_nodes[node_id],
                new_data=node_data
            ))

    # Find removed nodes
    for node_id, node_data in v1_nodes.items():
        if node_id not in v2_nodes:
            nodes_removed.append(NodeDiff(
                node_id=node_id,
                change_type="removed",
                old_data=node_data
            ))

    # Compare edges
    edges_added = []
    edges_removed = []
    edges_modified = []

    # Find added and modified edges
    for edge_id, edge_data in v2_edges.items():
        if edge_id not in v1_edges:
            edges_added.append(EdgeDiff(
                edge_id=edge_id,
                change_type="added",
                new_data=edge_data
            ))
        elif edge_data != v1_edges[edge_id]:
            edges_modified.append(EdgeDiff(
                edge_id=edge_id,
                change_type="modified",
                old_data=v1_edges[edge_id],
                new_data=edge_data
            ))

    # Find removed edges
    for edge_id, edge_data in v1_edges.items():
        if edge_id not in v2_edges:
            edges_removed.append(EdgeDiff(
                edge_id=edge_id,
                change_type="removed",
                old_data=edge_data
            ))

    return VersionComparison(
        workflow_id=str(workflow_id),
        version1=VersionSnapshot(**v1_snapshot),
        version2=VersionSnapshot(**v2_snapshot),
        nodes_added=nodes_added,
        nodes_removed=nodes_removed,
        nodes_modified=nodes_modified,
        edges_added=edges_added,
        edges_removed=edges_removed,
        edges_modified=edges_modified,
    )
