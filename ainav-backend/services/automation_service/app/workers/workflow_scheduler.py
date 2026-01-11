"""
Workflow Scheduler - Celery task for executing scheduled workflows.

This module provides the scheduled workflow execution task that:
1. Finds workflows scheduled to run (based on next_run_at)
2. Creates execution records for each scheduled workflow
3. Updates next_run_at using timezone-aware cron parsing
4. Handles failures and prepares for email notifications
"""
from datetime import datetime, timezone
import logging
import asyncio

from croniter import croniter
import pytz

from ..celery_app import celery_app
from shared.models import WorkflowSchedule, AgentWorkflow, AgentExecution, User
from shared.config import settings
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

logger = logging.getLogger(__name__)

# SQLAlchemy async setup for this task
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="execute_scheduled_workflows")
def execute_scheduled_workflows():
    """
    Main task to find and execute scheduled workflows.
    This task runs periodically (every minute via Celery Beat).
    """
    return asyncio.run(_execute_scheduled_workflows_pipeline())


async def _execute_scheduled_workflows_pipeline():
    """
    Find all enabled schedules that are due and execute them.
    """
    now_utc = datetime.now(timezone.utc)
    executed_count = 0
    failed_count = 0

    logger.info(f"Checking for scheduled workflows at {now_utc}")

    async with AsyncSessionLocal() as session:
        # Find all enabled schedules where next_run_at <= now
        query = select(WorkflowSchedule).where(
            WorkflowSchedule.enabled == True,
            WorkflowSchedule.next_run_at <= now_utc
        )

        result = await session.execute(query)
        due_schedules = result.scalars().all()

        if not due_schedules:
            logger.info("No scheduled workflows due at this time")
            return {
                "status": "success",
                "executed": 0,
                "failed": 0,
                "timestamp": now_utc.isoformat()
            }

        logger.info(f"Found {len(due_schedules)} scheduled workflow(s) to execute")

        for schedule in due_schedules:
            try:
                # Get the workflow
                workflow_result = await session.execute(
                    select(AgentWorkflow).where(AgentWorkflow.id == schedule.workflow_id)
                )
                workflow = workflow_result.scalar_one_or_none()

                if not workflow:
                    logger.error(f"Workflow {schedule.workflow_id} not found for schedule {schedule.id}")
                    failed_count += 1
                    continue

                # Get the user who created the schedule
                user_result = await session.execute(
                    select(User).where(User.id == schedule.created_by_user_id)
                )
                user = user_result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {schedule.created_by_user_id} not found for schedule {schedule.id}")
                    failed_count += 1
                    continue

                # Create execution record
                execution = AgentExecution(
                    workflow_id=workflow.id,
                    user_id=user.id,
                    status="pending",
                    input_data={},  # Scheduled workflows run without explicit input
                    trigger_type="scheduled",
                    trigger_metadata={
                        "schedule_id": str(schedule.id),
                        "cron_expression": schedule.cron_expression,
                        "timezone": schedule.timezone,
                        "scheduled_time": now_utc.isoformat()
                    },
                    execution_log=[],
                )

                session.add(execution)
                await session.flush()  # Get execution ID without committing

                logger.info(
                    f"Created execution {execution.id} for workflow '{workflow.name}' "
                    f"(schedule: {schedule.cron_expression}, timezone: {schedule.timezone})"
                )

                # Calculate next run time using croniter with timezone awareness
                next_run_at = _calculate_next_run(
                    schedule.cron_expression,
                    schedule.timezone
                )

                # Update schedule with new next_run_at and last_run_at
                schedule.last_run_at = now_utc
                schedule.next_run_at = next_run_at

                await session.commit()

                # Execute workflow in background (asynchronously within this task)
                # We don't wait for completion - it runs independently
                asyncio.create_task(
                    _execute_workflow_async(
                        execution_id=execution.id,
                        workflow=workflow
                    )
                )

                executed_count += 1
                logger.info(
                    f"Scheduled workflow '{workflow.name}' for execution. "
                    f"Next run: {next_run_at.isoformat()}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to process schedule {schedule.id}: {str(e)}",
                    exc_info=True
                )
                failed_count += 1
                # Continue processing other schedules even if one fails
                continue

    logger.info(
        f"Scheduled workflow execution complete: "
        f"{executed_count} executed, {failed_count} failed"
    )

    return {
        "status": "success",
        "executed": executed_count,
        "failed": failed_count,
        "timestamp": now_utc.isoformat()
    }


def _calculate_next_run(cron_expression: str, timezone_str: str) -> datetime:
    """
    Calculate the next run time for a cron expression in a specific timezone.

    Args:
        cron_expression: Cron expression (e.g., "0 9 * * *")
        timezone_str: Timezone name (e.g., "Asia/Shanghai", "America/New_York")

    Returns:
        Next run time as timezone-aware datetime in UTC
    """
    try:
        # Get timezone object
        tz = pytz.timezone(timezone_str)

        # Get current time in the schedule's timezone
        now_tz = datetime.now(tz)

        # Create croniter instance and get next occurrence
        cron = croniter(cron_expression, now_tz)
        next_run_tz = cron.get_next(datetime)

        # Convert to UTC for storage
        next_run_utc = next_run_tz.astimezone(pytz.UTC)

        return next_run_utc

    except Exception as e:
        logger.error(
            f"Error calculating next run time for cron '{cron_expression}' "
            f"in timezone '{timezone_str}': {str(e)}"
        )
        # Fallback: schedule 1 hour from now
        from datetime import timedelta
        return datetime.now(timezone.utc) + timedelta(hours=1)


async def _execute_workflow_async(execution_id, workflow: AgentWorkflow):
    """
    Execute a workflow asynchronously.

    This function is similar to execute_workflow_background in executions.py
    but adapted for scheduled execution.

    Args:
        execution_id: UUID of the execution record
        workflow: AgentWorkflow instance
    """
    # Import WorkflowExecutor from agent_service
    # Note: This assumes agent_service is in the Python path
    try:
        from services.agent_service.app.core.executor import WorkflowExecutor
    except ImportError:
        # Fallback for different import paths
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        from services.agent_service.app.core.executor import WorkflowExecutor

    start_time = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        # Update status to running
        await session.execute(
            update(AgentExecution)
            .where(AgentExecution.id == execution_id)
            .values(status="running")
        )
        await session.commit()

        try:
            # Create executor and run
            executor = WorkflowExecutor(
                graph_json=workflow.graph_json,
                llm_config={
                    "model": workflow.llm_model,
                    "system_prompt": workflow.system_prompt,
                    "temperature": workflow.temperature,
                }
            )

            result = await executor.execute({})  # Empty input for scheduled runs

            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Update with success
            await session.execute(
                update(AgentExecution)
                .where(AgentExecution.id == execution_id)
                .values(
                    status="completed",
                    output_data=result.output,
                    execution_log=result.logs,
                    token_usage=result.token_usage,
                    total_api_calls=result.api_calls,
                    duration_ms=duration_ms,
                )
            )

            # Increment workflow run count
            await session.execute(
                update(AgentWorkflow)
                .where(AgentWorkflow.id == workflow.id)
                .values(run_count=AgentWorkflow.run_count + 1)
            )

            await session.commit()

            logger.info(
                f"Scheduled execution {execution_id} completed successfully "
                f"in {duration_ms}ms"
            )

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            error_msg = str(e)
            logger.error(
                f"Scheduled execution {execution_id} failed: {error_msg}",
                exc_info=True
            )

            # Update with failure
            await session.execute(
                update(AgentExecution)
                .where(AgentExecution.id == execution_id)
                .values(
                    status="failed",
                    error_message=error_msg,
                    duration_ms=duration_ms,
                )
            )
            await session.commit()

            # TODO: Send email notification on failure (will be implemented in subtask 4.6)
            # For now, just log the failure
            logger.warning(
                f"Email notification for failed execution {execution_id} "
                f"will be sent once email service is integrated"
            )


@celery_app.task(name="execute_single_scheduled_workflow")
def execute_single_scheduled_workflow(schedule_id: str):
    """
    Execute a single scheduled workflow by schedule ID.

    This task is called by the DatabaseScheduler for individual workflow schedules.
    Each workflow schedule gets its own Celery Beat entry with its specific cron timing.

    Args:
        schedule_id: UUID string of the WorkflowSchedule record

    Returns:
        Dict with execution status and details
    """
    return asyncio.run(_execute_single_schedule(schedule_id))


async def _execute_single_schedule(schedule_id: str):
    """
    Execute a workflow for a specific schedule.

    Args:
        schedule_id: UUID string of the WorkflowSchedule record

    Returns:
        Dict with execution details
    """
    from uuid import UUID

    now_utc = datetime.now(timezone.utc)

    logger.info(f"Executing scheduled workflow for schedule {schedule_id}")

    async with AsyncSessionLocal() as session:
        # Get the schedule
        schedule_result = await session.execute(
            select(WorkflowSchedule).where(WorkflowSchedule.id == UUID(schedule_id))
        )
        schedule = schedule_result.scalar_one_or_none()

        if not schedule:
            logger.error(f"Schedule {schedule_id} not found")
            return {
                "status": "error",
                "message": f"Schedule {schedule_id} not found",
                "timestamp": now_utc.isoformat()
            }

        if not schedule.enabled:
            logger.info(f"Schedule {schedule_id} is disabled, skipping execution")
            return {
                "status": "skipped",
                "message": "Schedule is disabled",
                "timestamp": now_utc.isoformat()
            }

        # Get the workflow
        workflow_result = await session.execute(
            select(AgentWorkflow).where(AgentWorkflow.id == schedule.workflow_id)
        )
        workflow = workflow_result.scalar_one_or_none()

        if not workflow:
            logger.error(f"Workflow {schedule.workflow_id} not found for schedule {schedule_id}")
            return {
                "status": "error",
                "message": f"Workflow {schedule.workflow_id} not found",
                "timestamp": now_utc.isoformat()
            }

        # Get the user who created the schedule
        user_result = await session.execute(
            select(User).where(User.id == schedule.created_by_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"User {schedule.created_by_user_id} not found for schedule {schedule_id}")
            return {
                "status": "error",
                "message": f"User {schedule.created_by_user_id} not found",
                "timestamp": now_utc.isoformat()
            }

        # Create execution record
        execution = AgentExecution(
            workflow_id=workflow.id,
            user_id=user.id,
            status="pending",
            input_data={},  # Scheduled workflows run without explicit input
            trigger_type="scheduled",
            trigger_metadata={
                "schedule_id": str(schedule.id),
                "cron_expression": schedule.cron_expression,
                "timezone": schedule.timezone,
                "scheduled_time": now_utc.isoformat()
            },
            execution_log=[],
        )

        session.add(execution)
        await session.flush()  # Get execution ID without committing

        logger.info(
            f"Created execution {execution.id} for workflow '{workflow.name}' "
            f"(schedule: {schedule.cron_expression}, timezone: {schedule.timezone})"
        )

        # Calculate next run time using croniter with timezone awareness
        next_run_at = _calculate_next_run(
            schedule.cron_expression,
            schedule.timezone
        )

        # Update schedule with new next_run_at and last_run_at
        schedule.last_run_at = now_utc
        schedule.next_run_at = next_run_at

        await session.commit()

        # Execute workflow in background
        asyncio.create_task(
            _execute_workflow_async(
                execution_id=execution.id,
                workflow=workflow
            )
        )

        logger.info(
            f"Scheduled workflow '{workflow.name}' for execution. "
            f"Next run: {next_run_at.isoformat()}"
        )

        return {
            "status": "success",
            "execution_id": str(execution.id),
            "workflow_name": workflow.name,
            "next_run_at": next_run_at.isoformat(),
            "timestamp": now_utc.isoformat()
        }
