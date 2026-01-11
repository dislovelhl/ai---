"""
Authentication and Rate Limiting dependencies for agent_service.

Provides JWT-based authentication and rate limiting utilities by wrapping 
the shared authentication and rate limit modules.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from shared.database import get_async_session
from shared.models import User
from shared.auth import (
    get_current_user as shared_get_current_user,
    get_current_active_user as shared_get_current_active_user,
    get_current_user_id as shared_get_current_user_id,
    get_optional_user_id as shared_get_optional_user_id,
    get_admin_user as shared_get_admin_user,
    get_db
)
from shared.rate_limit import check_rate_limit


async def get_current_user(
    user: User = Depends(shared_get_current_user)
) -> User:
    """Dependency to get the current authenticated user."""
    return user


async def get_current_active_user(
    user: User = Depends(shared_get_current_active_user)
) -> User:
    """Dependency to get the current authenticated and active user."""
    return user


async def get_current_user_id(
    user_id: UUID = Depends(shared_get_current_user_id)
) -> UUID:
    """Dependency to get the current authenticated user's ID (lightweight)."""
    return user_id


async def get_optional_current_user_id(
    user_id: Optional[UUID] = Depends(shared_get_optional_user_id)
) -> Optional[UUID]:
    """Dependency to optionally get the user ID."""
    return user_id


async def get_admin_user(
    user: User = Depends(shared_get_admin_user)
) -> User:
    """Dependency to get the current active admin user."""
    return user


async def check_execution_rate_limit(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to check rate limits for agent workflow executions.
    """
    user_id = str(current_user.id)
    user_tier = current_user.user_tier.value

    # Check rate limit
    is_allowed, stats = await check_rate_limit(user_id, user_tier)

    if not is_allowed:
        # Calculate retry_after in seconds
        retry_after = stats.get("reset_at_timestamp", 0) - int(datetime.now(timezone.utc).timestamp())
        retry_after = max(1, retry_after)

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"Rate limit exceeded. Limit resets at {stats['reset_at']}.",
                "limit": stats["limit"],
                "used": stats["used"],
                "remaining": stats["remaining"],
                "reset_at": stats["reset_at"],
                "tier": user_tier,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(stats["limit"]),
                "X-RateLimit-Remaining": str(stats["remaining"]),
                "X-RateLimit-Reset": str(stats["reset_at_timestamp"]),
            }
        )

    return current_user

# Re-export key deps
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_user_id",
    "get_optional_current_user_id",
    "get_admin_user",
    "check_execution_rate_limit"
]
