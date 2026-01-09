"""
Celery Task Template
Usage: /gen worker <task_name>
"""

from celery import shared_task, Task
from celery.utils.log import get_task_logger
from typing import Optional, Any
import asyncio

from app.core.database import SessionLocal
from app.services.__SERVICE___service import __SERVICE_PASCAL__Service

logger = get_task_logger(__name__)


# =============================================================================
# Task Configuration
# =============================================================================

class BaseTask(Task):
    """
    基础任务类 - 提供通用功能
    """
    abstract = True
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        logger.error(
            f"Task {self.name}[{task_id}] failed: {exc}",
            extra={"args": args, "kwargs": kwargs},
        )

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功回调"""
        logger.info(f"Task {self.name}[{task_id}] completed successfully")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """任务重试回调"""
        logger.warning(
            f"Task {self.name}[{task_id}] retrying due to: {exc}",
            extra={"args": args, "kwargs": kwargs},
        )


# =============================================================================
# Sync Task
# =============================================================================

@shared_task(
    bind=True,
    base=BaseTask,
    name="app.workers.tasks.__TASK_NAME__",
    queue="default",
    rate_limit="100/m",  # 每分钟最多100次
    time_limit=300,  # 5分钟超时
    soft_time_limit=240,  # 4分钟软超时
)
def __TASK_NAME__(
    self,
    resource_id: str,
    options: Optional[dict] = None,
) -> dict:
    """
    __TASK_DESCRIPTION__

    Args:
        resource_id: 资源ID
        options: 可选配置

    Returns:
        处理结果
    """
    logger.info(f"Processing {resource_id} with options {options}")

    try:
        with SessionLocal() as db:
            service = __SERVICE_PASCAL__Service(db)
            result = service.process(resource_id, options or {})

            return {
                "status": "success",
                "resource_id": resource_id,
                "result": result,
            }

    except Exception as e:
        logger.error(f"Failed to process {resource_id}: {e}")
        # 让BaseTask处理重试逻辑
        raise


# =============================================================================
# Async Task
# =============================================================================

@shared_task(
    bind=True,
    base=BaseTask,
    name="app.workers.tasks.__TASK_NAME___async",
    queue="async",
)
def __TASK_NAME___async(self, resource_id: str) -> dict:
    """
    异步任务 - 包装async函数
    """
    return asyncio.get_event_loop().run_until_complete(
        _process_async(resource_id)
    )


async def _process_async(resource_id: str) -> dict:
    """
    实际的异步处理逻辑
    """
    # async implementation
    await asyncio.sleep(0)  # placeholder
    return {"status": "success", "resource_id": resource_id}


# =============================================================================
# Batch Task
# =============================================================================

@shared_task(
    bind=True,
    base=BaseTask,
    name="app.workers.tasks.__TASK_NAME___batch",
    queue="batch",
    rate_limit="10/m",
)
def __TASK_NAME___batch(
    self,
    resource_ids: list[str],
    batch_size: int = 50,
) -> dict:
    """
    批量处理任务

    Args:
        resource_ids: 资源ID列表
        batch_size: 每批处理数量
    """
    logger.info(f"Processing batch of {len(resource_ids)} items")

    results = {"success": 0, "failed": 0, "errors": []}

    with SessionLocal() as db:
        service = __SERVICE_PASCAL__Service(db)

        for i in range(0, len(resource_ids), batch_size):
            batch = resource_ids[i : i + batch_size]

            for resource_id in batch:
                try:
                    service.process(resource_id)
                    results["success"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "resource_id": resource_id,
                        "error": str(e),
                    })

            # 进度更新
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": min(i + batch_size, len(resource_ids)),
                    "total": len(resource_ids),
                },
            )

    return results


# =============================================================================
# Scheduled Task
# =============================================================================

@shared_task(
    name="app.workers.tasks.__TASK_NAME___scheduled",
    queue="scheduled",
)
def __TASK_NAME___scheduled() -> dict:
    """
    定时任务 - 由Celery Beat调度

    配置示例 (celeryconfig.py):
        beat_schedule = {
            '__TASK_NAME__-hourly': {
                'task': 'app.workers.tasks.__TASK_NAME___scheduled',
                'schedule': crontab(minute=0),  # 每小时
            },
        }
    """
    logger.info("Running scheduled task")

    with SessionLocal() as db:
        service = __SERVICE_PASCAL__Service(db)
        count = service.process_pending()

    return {
        "status": "success",
        "processed_count": count,
    }


# =============================================================================
# Chain/Group Tasks
# =============================================================================

def create_processing_chain(resource_id: str):
    """
    创建任务链

    Usage:
        chain = create_processing_chain("resource-id")
        chain.delay()
    """
    from celery import chain, group

    return chain(
        __TASK_NAME__.s(resource_id),
        enrich_resource.s(),
        notify_completion.s(),
    )


def create_processing_group(resource_ids: list[str]):
    """
    创建并行任务组

    Usage:
        group = create_processing_group(["id1", "id2", "id3"])
        group.delay()
    """
    from celery import group

    return group(__TASK_NAME__.s(rid) for rid in resource_ids)


# =============================================================================
# Helper Tasks
# =============================================================================

@shared_task(name="app.workers.tasks.enrich_resource")
def enrich_resource(previous_result: dict) -> dict:
    """链式任务 - 丰富资源数据"""
    resource_id = previous_result.get("resource_id")
    # Process enrichment
    return {**previous_result, "enriched": True}


@shared_task(name="app.workers.tasks.notify_completion")
def notify_completion(previous_result: dict) -> dict:
    """链式任务 - 完成通知"""
    resource_id = previous_result.get("resource_id")
    # Send notification
    logger.info(f"Processing complete for {resource_id}")
    return {**previous_result, "notified": True}
