"""
Analytics Router - Usage statistics and performance monitoring for agent workflows.

Includes:
- Workflow usage analytics
- Performance metrics dashboard
- Cache statistics
- System health monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Optional

from shared.database import get_async_session
from shared.models import AgentWorkflow, AgentExecution
from ..core.memory_service import memory_service
from ..core.cache_service import skill_cache, llm_cache, skill_selector
from ..engine.langgraph_engine import WorkflowGraphCache

router = APIRouter()


@router.get("/workflow/{workflow_id}")
async def get_workflow_analytics(
    workflow_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get usage analytics for a specific workflow.
    """
    # Get workflow
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get execution stats
    exec_query = select(
        func.count(AgentExecution.id).label("total_runs"),
        func.sum(AgentExecution.token_usage).label("total_tokens"),
        func.avg(AgentExecution.duration_ms).label("avg_duration_ms"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "completed"
        ).label("successful_runs"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "failed"
        ).label("failed_runs"),
    ).where(
        AgentExecution.workflow_id == workflow_id,
        AgentExecution.created_at >= start_date
    )
    
    exec_result = await db.execute(exec_query)
    stats = exec_result.one()
    
    total_runs = stats.total_runs or 0
    successful_runs = stats.successful_runs or 0
    
    return {
        "workflow_id": str(workflow_id),
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "stats": {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": stats.failed_runs or 0,
            "success_rate": round(successful_runs / total_runs * 100, 2) if total_runs > 0 else 0,
            "total_tokens": stats.total_tokens or 0,
            "avg_duration_ms": round(stats.avg_duration_ms or 0, 2),
        },
        "counts": {
            "stars": workflow.star_count,
            "forks": workflow.fork_count,
            "version": workflow.version or 1,
        }
    }


@router.get("/workflow/{workflow_id}/runs")
async def get_workflow_run_history(
    workflow_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get daily run counts for a workflow over time.
    """
    # Verify workflow exists
    result = await db.execute(
        select(AgentWorkflow).where(AgentWorkflow.id == workflow_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Get daily counts
    daily_query = select(
        func.date(AgentExecution.created_at).label("date"),
        func.count(AgentExecution.id).label("runs"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "completed"
        ).label("successful"),
    ).where(
        AgentExecution.workflow_id == workflow_id,
        AgentExecution.created_at >= start_date
    ).group_by(
        func.date(AgentExecution.created_at)
    ).order_by(
        func.date(AgentExecution.created_at)
    )
    
    daily_result = await db.execute(daily_query)
    daily_data = daily_result.all()
    
    return {
        "workflow_id": str(workflow_id),
        "period_days": days,
        "data": [
            {
                "date": str(row.date),
                "runs": row.runs,
                "successful": row.successful
            }
            for row in daily_data
        ]
    }


@router.get("/top")
async def get_top_workflows(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get top workflows by popularity score.
    """
    query = select(AgentWorkflow).where(
        AgentWorkflow.is_public == True
    ).order_by(
        (AgentWorkflow.run_count + AgentWorkflow.star_count * 2).desc()
    ).limit(limit)

    result = await db.execute(query)
    workflows = result.scalars().all()

    return {
        "workflows": [
            {
                "id": str(w.id),
                "name": w.name,
                "name_zh": w.name_zh,
                "description": w.description,
                "icon": w.icon,
                "run_count": w.run_count,
                "star_count": w.star_count,
                "fork_count": w.fork_count,
                "score": w.run_count + w.star_count * 2
            }
            for w in workflows
        ]
    }


@router.get("/performance/dashboard")
async def get_performance_dashboard(
    db: AsyncSession = Depends(get_async_session),
):
    """
    Comprehensive performance monitoring dashboard.

    Returns metrics for:
    - Cache hit rates (embedding, LLM, skill)
    - Workflow graph cache status
    - Memory service statistics
    - Skill selector status
    - System execution summary
    """
    # Get cache statistics
    embedding_stats = memory_service.get_cache_stats()
    llm_stats = llm_cache.get_stats()
    skill_stats = skill_cache.get_stats()

    # Get workflow graph cache stats
    graph_cache_stats = {
        "cached_workflows": len(WorkflowGraphCache._cache),
        "max_size": WorkflowGraphCache._max_size,
        "utilization_percent": round(
            len(WorkflowGraphCache._cache) / WorkflowGraphCache._max_size * 100, 2
        )
    }

    # Get skill selector status
    skill_selector_stats = {
        "initialized": len(skill_selector.skill_embeddings) > 0,
        "indexed_skills": len(skill_selector.skill_embeddings),
        "skills": list(skill_selector.skill_embeddings.keys())[:10]  # First 10
    }

    # Get recent execution statistics (last 24 hours)
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    exec_query = select(
        func.count(AgentExecution.id).label("total"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "completed"
        ).label("completed"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "failed"
        ).label("failed"),
        func.avg(AgentExecution.duration_ms).label("avg_duration"),
        func.sum(AgentExecution.token_usage).label("total_tokens"),
    ).where(
        AgentExecution.created_at >= day_ago
    )

    exec_result = await db.execute(exec_query)
    exec_stats = exec_result.one()

    total_executions = exec_stats.total or 0
    completed = exec_stats.completed or 0

    return {
        "timestamp": now.isoformat(),
        "caches": {
            "embedding": embedding_stats,
            "llm": llm_stats,
            "skill": skill_stats,
            "workflow_graph": graph_cache_stats,
        },
        "skill_selector": skill_selector_stats,
        "executions_24h": {
            "total": total_executions,
            "completed": completed,
            "failed": exec_stats.failed or 0,
            "success_rate": round(completed / total_executions * 100, 2) if total_executions > 0 else 0,
            "avg_duration_ms": round(exec_stats.avg_duration or 0, 2),
            "total_tokens": exec_stats.total_tokens or 0,
        },
        "optimization_status": {
            "async_embeddings": True,
            "redis_connection_pooling": True,
            "multi_tier_caching": True,
            "semantic_skill_selection": len(skill_selector.skill_embeddings) > 0,
            "parallel_node_execution": True,
            "graph_caching": len(WorkflowGraphCache._cache) > 0,
        }
    }


@router.get("/performance/caches")
async def get_cache_details():
    """
    Detailed cache statistics for all caching layers.
    """
    return {
        "embedding_cache": {
            **memory_service.get_cache_stats(),
            "description": "Local LRU + Redis distributed cache for text embeddings"
        },
        "llm_response_cache": {
            **llm_cache.get_stats(),
            "similarity_threshold": llm_cache.SIMILARITY_THRESHOLD,
            "description": "Semantic caching for LLM responses (95% similarity match)"
        },
        "skill_result_cache": {
            **skill_cache.get_stats(),
            "ttl_config": skill_cache.SKILL_TTL_MAP,
            "description": "TTL-based caching for skill execution results"
        },
        "workflow_graph_cache": {
            "size": len(WorkflowGraphCache._cache),
            "max_size": WorkflowGraphCache._max_size,
            "cached_workflow_ids": list(WorkflowGraphCache._cache.keys())[:20],
            "description": "Compiled LangGraph StateGraph cache"
        }
    }


@router.get("/performance/bottlenecks")
async def get_performance_bottlenecks(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Identify performance bottlenecks across workflows.

    Analyzes:
    - Slowest workflows by average duration
    - Highest token consuming workflows
    - Highest failure rate workflows
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Slowest workflows
    slow_query = select(
        AgentExecution.workflow_id,
        func.avg(AgentExecution.duration_ms).label("avg_duration"),
        func.count(AgentExecution.id).label("run_count"),
    ).where(
        AgentExecution.created_at >= start_date,
        AgentExecution.status == "completed"
    ).group_by(
        AgentExecution.workflow_id
    ).having(
        func.count(AgentExecution.id) >= 5  # At least 5 runs
    ).order_by(
        func.avg(AgentExecution.duration_ms).desc()
    ).limit(10)

    slow_result = await db.execute(slow_query)
    slow_workflows = slow_result.all()

    # Highest token consuming
    token_query = select(
        AgentExecution.workflow_id,
        func.sum(AgentExecution.token_usage).label("total_tokens"),
        func.avg(AgentExecution.token_usage).label("avg_tokens"),
        func.count(AgentExecution.id).label("run_count"),
    ).where(
        AgentExecution.created_at >= start_date
    ).group_by(
        AgentExecution.workflow_id
    ).having(
        func.count(AgentExecution.id) >= 5
    ).order_by(
        func.sum(AgentExecution.token_usage).desc()
    ).limit(10)

    token_result = await db.execute(token_query)
    token_workflows = token_result.all()

    # Highest failure rate
    failure_query = select(
        AgentExecution.workflow_id,
        func.count(AgentExecution.id).label("total"),
        func.count(AgentExecution.id).filter(
            AgentExecution.status == "failed"
        ).label("failed"),
    ).where(
        AgentExecution.created_at >= start_date
    ).group_by(
        AgentExecution.workflow_id
    ).having(
        func.count(AgentExecution.id) >= 5
    ).order_by(
        (func.count(AgentExecution.id).filter(AgentExecution.status == "failed") * 100.0 /
         func.count(AgentExecution.id)).desc()
    ).limit(10)

    failure_result = await db.execute(failure_query)
    failure_workflows = failure_result.all()

    return {
        "period_days": days,
        "slowest_workflows": [
            {
                "workflow_id": str(w.workflow_id),
                "avg_duration_ms": round(w.avg_duration, 2),
                "run_count": w.run_count
            }
            for w in slow_workflows
        ],
        "highest_token_usage": [
            {
                "workflow_id": str(w.workflow_id),
                "total_tokens": w.total_tokens,
                "avg_tokens": round(w.avg_tokens, 2) if w.avg_tokens else 0,
                "run_count": w.run_count
            }
            for w in token_workflows
        ],
        "highest_failure_rate": [
            {
                "workflow_id": str(w.workflow_id),
                "total_runs": w.total,
                "failed_runs": w.failed,
                "failure_rate": round(w.failed / w.total * 100, 2) if w.total > 0 else 0
            }
            for w in failure_workflows
        ],
        "recommendations": _generate_optimization_recommendations(
            slow_workflows, token_workflows, failure_workflows
        )
    }


def _generate_optimization_recommendations(slow, tokens, failures) -> list:
    """Generate optimization recommendations based on bottleneck analysis."""
    recommendations = []

    if slow and slow[0].avg_duration > 5000:  # > 5 seconds
        recommendations.append({
            "type": "performance",
            "priority": "high",
            "message": "Consider enabling parallel node execution for slow workflows",
            "affected_workflows": [str(w.workflow_id) for w in slow[:3]]
        })

    if tokens and tokens[0].avg_tokens and tokens[0].avg_tokens > 10000:
        recommendations.append({
            "type": "cost",
            "priority": "medium",
            "message": "High token usage detected. Consider implementing response caching",
            "affected_workflows": [str(w.workflow_id) for w in tokens[:3]]
        })

    if failures:
        high_failure = [f for f in failures if f.total > 0 and f.failed / f.total > 0.2]
        if high_failure:
            recommendations.append({
                "type": "reliability",
                "priority": "high",
                "message": "High failure rates detected. Review error logs and add retry logic",
                "affected_workflows": [str(w.workflow_id) for w in high_failure[:3]]
            })

    if not recommendations:
        recommendations.append({
            "type": "status",
            "priority": "info",
            "message": "All systems operating within normal parameters"
        })

    return recommendations


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_async_session),
):
    """
    System health check with component status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {}
    }

    # Check database
    try:
        await db.execute(select(func.count(AgentWorkflow.id)))
        health_status["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check Redis (via memory service)
    try:
        redis = memory_service.get_redis()
        await redis.ping()
        health_status["components"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check embedding service
    try:
        embedder = memory_service.get_embedder()
        health_status["components"]["embeddings"] = {
            "status": "healthy",
            "model": "all-MiniLM-L6-v2"
        }
    except Exception as e:
        health_status["components"]["embeddings"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check skill selector
    health_status["components"]["skill_selector"] = {
        "status": "healthy" if len(skill_selector.skill_embeddings) > 0 else "not_initialized",
        "indexed_skills": len(skill_selector.skill_embeddings)
    }

    # Check caches
    health_status["components"]["caches"] = {
        "embedding_cache": "active",
        "llm_cache": "active",
        "skill_cache": "active",
        "graph_cache": f"{len(WorkflowGraphCache._cache)} cached"
    }

    return health_status
