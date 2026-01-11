from celery import Celery
from celery.signals import worker_process_init
from shared.config import settings

celery_app = Celery(
    "automation_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "services.automation_service.app.workers.tasks",
        "services.automation_service.app.workers.workflow_scheduler"
    ]
)

@worker_process_init.connect
def init_worker(**kwargs):
    """Ensure that each worker process has its own SQLAlchemy engine and connection pool."""
    from shared.database import engine
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # For AsyncEngine, we dispose the underlying sync engine's pool
    engine.sync_engine.dispose()

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Standard Celery performance tweaks
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "crawl-ph-daily": {
        "task": "crawl_and_enrich_daily",
        "schedule": crontab(hour=0, minute=0),
    },
    "crawl-github-daily": {
        "task": "crawl_github_trending_daily",
        "schedule": crontab(hour=1, minute=0),
    },
    "mine-arxiv-daily": {
        "task": "mine_arxiv_papers_daily",
        "schedule": crontab(hour=2, minute=0),
    },
    "execute-scheduled-workflows": {
        "task": "execute_scheduled_workflows",
        "schedule": crontab(minute="*"),  # Run every minute
    },
}
