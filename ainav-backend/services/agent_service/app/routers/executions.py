"""
Executions Router - Run workflows and track execution history.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional, Any
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel
import math

from shared.database import get_async_session
from shared.models import AgentExecution, AgentWorkflow, User
from ..schemas import (
    ExecutionCreate, ExecutionResponse, ExecutionSummary,
    ExecutionDetailsResponse, PaginatedExecutionsResponse,
    ReactFlowNode, ReactFlowEdge
)
from ..core.executor import WorkflowExecutor

# Try to import LangGraph engine (optional dependency)
try:
    from ..engine.langgraph_engine import LangGraphWorkflowEngine
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

router = APIRouter()


# Direct execution request (no saved workflow needed)
class DirectExecutionRequest(BaseModel):
    """Execute a workflow directly from JSON without saving."""
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    input: str = "Start workflow"
    use_langgraph: bool = False  # Use LangGraph engine if available


class DirectExecutionResponse(BaseModel):
    """Response from direct execution."""
    status: str
    output: Any
    trace: dict[str, Any]
    token_usage: int = 0
    api_calls: int = 0
    duration_ms: int = 0


@router.get("", response_model=PaginatedExecutionsResponse)
async def list_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    workflow_id: Optional[UUID] = None,
    status: Optional[str] = None,
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
):
    """
    List execution history with optional filtering.
    """
    query = select(AgentExecution)
    count_query = select(func.count(AgentExecution.id))
    
    if workflow_id:
        query = query.where(AgentExecution.workflow_id == workflow_id)
        count_query = count_query.where(AgentExecution.workflow_id == workflow_id)
    
    if status:
        query = query.where(AgentExecution.status == status)
        count_query = count_query.where(AgentExecution.status == status)
    
    # TODO: Filter by user_id from auth
    
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    offset = (page - 1) * page_size
    query = query.order_by(AgentExecution.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return PaginatedExecutionsResponse(
        items=[ExecutionSummary.model_validate(e) for e in executions],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get detailed execution information including logs.
    """
    result = await db.execute(
        select(AgentExecution).where(AgentExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return ExecutionResponse.model_validate(execution)


@router.get("/{execution_id}/details", response_model=ExecutionDetailsResponse)
async def get_execution_details(
    execution_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get detailed execution information with step-by-step execution data.

    Returns comprehensive execution details including:
    - Overall execution status and metadata
    - Detailed step-by-step execution data for each node
    - Input/output data for each step
    - Error messages and token usage per step
    - Timing information (started_at, completed_at) for each step
    """
    result = await db.execute(
        select(AgentExecution).where(AgentExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return ExecutionDetailsResponse.model_validate(execution)


@router.post("/run", response_model=ExecutionResponse, status_code=201)
async def run_workflow(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Execute a workflow. Creates an execution record and runs in background.
    """
    # Get workflow
    workflow_result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == execution_data.workflow_id)
    )
    workflow = workflow_result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # TODO: Get user_id from auth
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="No user available")
    
    # Create execution record
    execution = AgentExecution(
        workflow_id=workflow.id,
        user_id=user.id,
        status="pending",
        input_data=execution_data.input_data,
        trigger_type=execution_data.trigger_type,
        trigger_metadata=execution_data.trigger_metadata,
        execution_log=[],
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Execute in background
    background_tasks.add_task(
        execute_workflow_background,
        execution_id=execution.id,
        workflow_graph=workflow.graph_json,
        input_data=execution_data.input_data,
        llm_model=workflow.llm_model,
        system_prompt=workflow.system_prompt,
        temperature=workflow.temperature,
    )
    
    return ExecutionResponse.model_validate(execution)


async def execute_workflow_background(
    execution_id: UUID,
    workflow_graph: dict,
    input_data: dict | None,
    llm_model: str,
    system_prompt: str | None,
    temperature: float,
):
    """
    Background task to execute workflow.
    """
    from shared.database import async_session_factory
    from ..websocket import manager

    start_time = datetime.now(timezone.utc)

    async with async_session_factory() as db:
        # Update status to running
        await db.execute(
            update(AgentExecution)
            .where(AgentExecution.id == execution_id)
            .values(status="running")
        )
        await db.commit()

        # Notify WebSocket clients that execution started
        await manager.send_execution_status(
            execution_id=str(execution_id),
            status="running"
        )
        
        try:
            # Create executor and run
            executor = WorkflowExecutor(
                graph_json=workflow_graph,
                llm_config={
                    "model": llm_model,
                    "system_prompt": system_prompt,
                    "temperature": temperature,
                },
                execution_id=execution_id
            )

            result = await executor.execute(input_data or {})
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update with success
            await db.execute(
                update(AgentExecution)
                .where(AgentExecution.id == execution_id)
                .values(
                    status="completed",
                    output_data=result.output,
                    execution_log=result.logs,
                    execution_steps=result.execution_steps,
                    token_usage=result.token_usage,
                    total_api_calls=result.api_calls,
                    duration_ms=duration_ms,
                )
            )
            
            # Increment workflow run count
            await db.execute(
                update(AgentWorkflow)
                .where(AgentWorkflow.id == AgentExecution.workflow_id)
                .values(run_count=AgentWorkflow.run_count + 1)
            )

            await db.commit()

            # Notify WebSocket clients that execution completed
            await manager.send_execution_status(
                execution_id=str(execution_id),
                status="completed"
            )
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Update with failure
            await db.execute(
                update(AgentExecution)
                .where(AgentExecution.id == execution_id)
                .values(
                    status="failed",
                    error_message=str(e),
                    duration_ms=duration_ms,
                )
            )
            await db.commit()

            # Notify WebSocket clients that execution failed
            await manager.send_execution_status(
                execution_id=str(execution_id),
                status="failed",
                error_message=str(e)
            )


@router.post("/{execution_id}/cancel", status_code=200)
async def cancel_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Cancel a running execution.
    """
    result = await db.execute(
        select(AgentExecution).where(AgentExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel execution with status: {execution.status}"
        )
    
    execution.status = "cancelled"
    await db.commit()
    
    return {"status": "cancelled", "execution_id": str(execution_id)}


@router.post("/run-sync", response_model=ExecutionResponse)
async def run_workflow_sync(
    execution_data: ExecutionCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Execute a workflow synchronously (wait for result).
    Useful for simple workflows or testing.
    """
    # Get workflow
    workflow_result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == execution_data.workflow_id)
    )
    workflow = workflow_result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # TODO: Get user_id from auth
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="No user available")
    
    start_time = datetime.now(timezone.utc)
    
    # Create execution record
    execution = AgentExecution(
        workflow_id=workflow.id,
        user_id=user.id,
        status="running",
        input_data=execution_data.input_data,
        trigger_type=execution_data.trigger_type,
        trigger_metadata=execution_data.trigger_metadata,
        execution_log=[],
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    try:
        # Create executor and run
        executor = WorkflowExecutor(
            graph_json=workflow.graph_json,
            llm_config={
                "model": workflow.llm_model,
                "system_prompt": workflow.system_prompt,
                "temperature": workflow.temperature,
            },
            execution_id=execution.id
        )

        result = await executor.execute(execution_data.input_data or {})
        
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Update with success
        execution.status = "completed"
        execution.output_data = result.output
        execution.execution_log = result.logs
        execution.execution_steps = result.execution_steps
        execution.token_usage = result.token_usage
        execution.total_api_calls = result.api_calls
        execution.duration_ms = duration_ms
        
        # Increment workflow run count
        workflow.run_count += 1
        
        await db.commit()
        await db.refresh(execution)
        
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        execution.status = "failed"
        execution.error_message = str(e)
        execution.duration_ms = duration_ms
        
        await db.commit()
        await db.refresh(execution)
    
    return ExecutionResponse.model_validate(execution)


@router.post("/run-direct", response_model=DirectExecutionResponse)
async def run_workflow_direct(request: DirectExecutionRequest):
    """
    Execute a workflow directly from JSON without saving to database.
    
    This is useful for:
    - Testing workflows in the Studio before saving
    - Quick one-off executions
    - Integration with external systems
    
    Supports two execution engines:
    - default: Custom WorkflowExecutor
    - langgraph: LangGraph-based engine (if available)
    """
    start_time = datetime.now(timezone.utc)
    
    workflow_config = {
        "nodes": request.nodes,
        "edges": request.edges,
    }
    
    try:
        if request.use_langgraph and LANGGRAPH_AVAILABLE:
            # Use LangGraph engine
            engine = LangGraphWorkflowEngine(workflow_config)
            result = await engine.run(request.input)
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return DirectExecutionResponse(
                status="success",
                output=result.get("output"),
                trace=result.get("trace", {}),
                token_usage=result.get("token_usage", 0),
                api_calls=result.get("api_calls", 0),
                duration_ms=duration_ms,
            )
        else:
            # Use custom executor
            executor = WorkflowExecutor(graph_json=workflow_config, llm_config={})
            result = await executor.execute({"input": request.input})
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return DirectExecutionResponse(
                status="success" if result.success else "failed",
                output=result.output,
                trace={"logs": result.logs},
                token_usage=result.token_usage,
                api_calls=result.api_calls,
                duration_ms=duration_ms,
            )
            
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return DirectExecutionResponse(
            status="failed",
            output=None,
            trace={"error": str(e)},
            token_usage=0,
            api_calls=0,
            duration_ms=duration_ms,
        )


@router.get("/engines")
async def list_engines():
    """
    List available execution engines.
    """
    engines = [
        {
            "id": "default",
            "name": "Custom Executor",
            "description": "Built-in workflow executor with template interpolation",
            "available": True,
        }
    ]
    
    if LANGGRAPH_AVAILABLE:
        engines.append({
            "id": "langgraph",
            "name": "LangGraph Engine",
            "description": "LangChain LangGraph-based state machine executor",
            "available": True,
        })
    
    return {"engines": engines}

