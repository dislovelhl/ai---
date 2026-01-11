"""
Schedules Router - CRUD operations for workflow schedules.
Supports cron-based scheduling with timezone awareness.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
import math

from shared.database import get_async_session
from shared.models import WorkflowSchedule, AgentWorkflow, User
from ..schemas.schedules import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleSummary,
    PaginatedSchedulesResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedSchedulesResponse)
async def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    workflow_id: Optional[UUID] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List workflow schedules with optional filtering.
    """
    query = select(WorkflowSchedule)
    count_query = select(func.count(WorkflowSchedule.id))

    # Filter by workflow_id if provided
    if workflow_id:
        query = query.where(WorkflowSchedule.workflow_id == workflow_id)
        count_query = count_query.where(WorkflowSchedule.workflow_id == workflow_id)

    # Filter by enabled status if provided
    if enabled is not None:
        query = query.where(WorkflowSchedule.enabled == enabled)
        count_query = count_query.where(WorkflowSchedule.enabled == enabled)

    # Get total count
    total = (await db.execute(count_query)).scalar() or 0
    pages = math.ceil(total / page_size) if total > 0 else 1

    # Paginate and order by next_run_at
    offset = (page - 1) * page_size
    query = query.order_by(
        WorkflowSchedule.next_run_at.asc().nullsfirst(),
        WorkflowSchedule.created_at.desc()
    ).offset(offset).limit(page_size)

    result = await db.execute(query)
    schedules = result.scalars().all()

    return PaginatedSchedulesResponse(
        items=[ScheduleSummary.model_validate(s) for s in schedules],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific schedule by ID.
    """
    result = await db.execute(
        select(WorkflowSchedule).where(WorkflowSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # TODO: Check permissions (owner or workflow owner)

    return ScheduleResponse.model_validate(schedule)


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    schedule_data: ScheduleCreate,
    # user_id: UUID = Depends(get_current_user_id),  # TODO: Add auth
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new workflow schedule.
    """
    # TODO: Get user_id from auth
    # For now, use a placeholder or first user
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="No user available. Please create a user first.")

    # Verify workflow exists
    workflow_result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == schedule_data.workflow_id)
    )
    workflow = workflow_result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # TODO: Check workflow ownership

    # Calculate next_run_at based on cron expression
    next_run_at = None
    try:
        from croniter import croniter
        from datetime import datetime
        import pytz

        # Get timezone object
        tz = pytz.timezone(schedule_data.timezone.value)
        now = datetime.now(tz)

        # Calculate next run
        cron = croniter(schedule_data.cron_expression, now)
        next_run_at = cron.get_next(datetime)
    except ImportError:
        # croniter not installed, skip calculation
        pass
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cron expression or timezone: {str(e)}"
        )

    # Create schedule
    schedule = WorkflowSchedule(
        workflow_id=schedule_data.workflow_id,
        created_by_user_id=user.id,
        cron_expression=schedule_data.cron_expression,
        timezone=schedule_data.timezone.value,
        enabled=schedule_data.enabled,
        next_run_at=next_run_at,
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return ScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update an existing workflow schedule.
    """
    result = await db.execute(
        select(WorkflowSchedule).where(WorkflowSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # TODO: Check ownership

    update_data = schedule_data.model_dump(exclude_unset=True)

    # If cron_expression or timezone changed, recalculate next_run_at
    if 'cron_expression' in update_data or 'timezone' in update_data:
        try:
            from croniter import croniter
            from datetime import datetime
            import pytz

            # Use updated or existing values
            cron_expr = update_data.get('cron_expression', schedule.cron_expression)
            timezone_str = update_data.get('timezone')
            if timezone_str:
                timezone_str = timezone_str.value  # Extract enum value
            else:
                timezone_str = schedule.timezone

            # Get timezone object
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Calculate next run
            cron = croniter(cron_expr, now)
            next_run_at = cron.get_next(datetime)
            update_data['next_run_at'] = next_run_at

        except ImportError:
            # croniter not installed, skip calculation
            pass
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid cron expression or timezone: {str(e)}"
            )

    # Handle timezone enum conversion
    if 'timezone' in update_data and update_data['timezone']:
        update_data['timezone'] = update_data['timezone'].value

    for field, value in update_data.items():
        setattr(schedule, field, value)

    await db.commit()
    await db.refresh(schedule)

    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a workflow schedule.
    """
    result = await db.execute(
        select(WorkflowSchedule).where(WorkflowSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # TODO: Check ownership

    await db.delete(schedule)
    await db.commit()
