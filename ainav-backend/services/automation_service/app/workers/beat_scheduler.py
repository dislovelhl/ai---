"""
Database-backed Celery Beat Scheduler.

This module provides a custom Celery Beat scheduler that:
1. Loads workflow schedules dynamically from PostgreSQL
2. Creates individual beat entries for each enabled schedule
3. Syncs with database changes without requiring restart
4. Provides more efficient scheduling than polling every minute
"""
import logging
from datetime import datetime, timezone
from typing import Dict
import asyncio

from celery import schedules
from celery.beat import Scheduler, ScheduleEntry
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from shared.models import WorkflowSchedule
from shared.config import settings

logger = logging.getLogger(__name__)


class WorkflowScheduleEntry(ScheduleEntry):
    """
    Custom ScheduleEntry for workflow schedules.
    Wraps a WorkflowSchedule database record as a Celery Beat schedule entry.
    """

    def __init__(self, schedule_record: WorkflowSchedule, app=None):
        """
        Initialize from a WorkflowSchedule database record.

        Args:
            schedule_record: WorkflowSchedule instance from database
            app: Celery app instance
        """
        self.schedule_record = schedule_record

        # Create a cron schedule from the cron expression
        # Parse cron expression: "minute hour day month day_of_week"
        parts = schedule_record.cron_expression.split()
        if len(parts) != 5:
            logger.error(f"Invalid cron expression: {schedule_record.cron_expression}")
            # Default to every hour as fallback
            cron_schedule = schedules.crontab(minute=0)
        else:
            minute, hour, day_of_month, month_of_year, day_of_week = parts
            cron_schedule = schedules.crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week
            )

        # Initialize parent ScheduleEntry
        super().__init__(
            name=f"workflow_schedule_{schedule_record.id}",
            task="execute_single_scheduled_workflow",
            schedule=cron_schedule,
            args=(str(schedule_record.id),),  # Pass schedule ID as argument
            kwargs={},
            options={
                'expires': 3600,  # Task expires after 1 hour if not executed
            },
            app=app
        )

    def is_due(self):
        """
        Check if this schedule is due to run.
        Only returns true if the schedule is enabled.
        """
        if not self.schedule_record.enabled:
            # Return not due if disabled
            return False, 3600  # Check again in 1 hour

        return super().is_due()


class DatabaseScheduler(Scheduler):
    """
    Custom Celery Beat scheduler that loads schedules from PostgreSQL.

    This scheduler:
    - Loads WorkflowSchedule records on startup
    - Polls database every 5 minutes for changes
    - Creates ScheduleEntry objects for each enabled schedule
    - Allows adding/modifying schedules without restarting beat
    """

    # How often to sync with database (in seconds)
    SYNC_INTERVAL = 300  # 5 minutes

    def __init__(self, *args, **kwargs):
        """Initialize the database scheduler."""
        self._schedule = {}
        self._last_sync = None

        # Setup async database connection
        self.engine = create_async_engine(settings.DATABASE_URL)
        self.AsyncSessionLocal = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        super().__init__(*args, **kwargs)

        # Load schedules from database on initialization
        logger.info("DatabaseScheduler initializing...")
        self._sync_schedules()

    def setup_schedule(self):
        """
        Setup the schedule by loading from database.
        This is called during scheduler initialization.
        """
        # Sync with database
        self._sync_schedules()

        # Also include static schedules from celery_app.py
        # (for other periodic tasks like crawlers)
        static_schedule = self.app.conf.beat_schedule or {}

        # Merge static schedules with dynamic workflow schedules
        # Static schedules take precedence to avoid conflicts
        for name, entry_dict in static_schedule.items():
            if name not in self._schedule:
                # Convert dict to ScheduleEntry
                entry = self.Entry(
                    name=name,
                    app=self.app,
                    **entry_dict
                )
                self._schedule[name] = entry

        return self._schedule

    @property
    def schedule(self):
        """
        Get the current schedule.
        Syncs with database if enough time has passed.
        """
        now = datetime.now(timezone.utc)

        # Check if it's time to sync
        if (self._last_sync is None or
            (now - self._last_sync).total_seconds() > self.SYNC_INTERVAL):
            logger.info("Syncing schedules from database...")
            self._sync_schedules()

        return self._schedule

    def _sync_schedules(self):
        """
        Sync workflow schedules from database.
        This runs in a synchronous context, so we use asyncio.run().
        """
        try:
            # Run async database query in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                schedules = loop.run_until_complete(self._load_schedules_from_db())
            finally:
                loop.close()

            # Remove old workflow schedule entries
            # (keep static schedules from celery_app.py)
            old_keys = [
                key for key in self._schedule.keys()
                if key.startswith('workflow_schedule_')
            ]
            for key in old_keys:
                del self._schedule[key]

            # Add new workflow schedule entries
            for schedule_record in schedules:
                entry = WorkflowScheduleEntry(schedule_record, app=self.app)
                self._schedule[entry.name] = entry
                logger.debug(
                    f"Loaded schedule: {entry.name} "
                    f"(cron: {schedule_record.cron_expression}, "
                    f"enabled: {schedule_record.enabled})"
                )

            self._last_sync = datetime.now(timezone.utc)
            logger.info(f"Synced {len(schedules)} workflow schedules from database")

        except Exception as e:
            logger.error(f"Error syncing schedules from database: {str(e)}", exc_info=True)

    async def _load_schedules_from_db(self):
        """
        Load all workflow schedules from database.

        Returns:
            List of WorkflowSchedule records
        """
        async with self.AsyncSessionLocal() as session:
            # Load all schedules (both enabled and disabled)
            # We load all so we can properly clean up disabled ones
            query = select(WorkflowSchedule)
            result = await session.execute(query)
            schedules = result.scalars().all()

            # Return a copy of the data to avoid detached instance issues
            # Create simple objects with the data we need
            schedule_data = []
            for s in schedules:
                schedule_data.append(WorkflowSchedule(
                    id=s.id,
                    workflow_id=s.workflow_id,
                    created_by_user_id=s.created_by_user_id,
                    cron_expression=s.cron_expression,
                    timezone=s.timezone,
                    enabled=s.enabled,
                    next_run_at=s.next_run_at,
                    last_run_at=s.last_run_at
                ))

            return schedule_data
