"""
Authentication dependencies for user_service.

Wraps shared authentication module for consistent JWT handling across services.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.auth import (
    get_current_user as shared_get_current_user,
    get_current_active_user as shared_get_current_active_user,
    get_admin_user as shared_get_admin_user,
    get_db,
)
from shared.models import User, UserRole


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


async def require_admin(
    user: User = Depends(shared_get_admin_user)
) -> User:
    """
    Dependency that requires the current user to have admin role.

    Raises HTTPException with 403 status if user is not an admin.
    """
    return user


async def require_moderator(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires the current user to have moderator or admin role.

    Raises HTTPException with 403 status if user is not a moderator or admin.
    """
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator privileges required"
        )
    return current_user


# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_moderator",
]
