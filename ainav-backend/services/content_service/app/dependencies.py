"""
Authentication dependencies for content_service.

Wraps shared authentication module for consistent JWT handling across services.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.auth import (
    get_current_user as shared_get_current_user,
    get_current_active_user as shared_get_current_active_user,
    get_admin_user as shared_get_admin_user,
    get_current_user_id as shared_get_current_user_id,
    get_optional_user_id as shared_get_optional_user_id,
    get_optional_user as shared_get_optional_user,
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


async def get_current_user_id(
    user_id: UUID = Depends(shared_get_current_user_id)
) -> UUID:
    """Dependency to get the current user's ID (lightweight, no DB lookup)."""
    return user_id


async def get_optional_user_id(
    user_id: Optional[UUID] = Depends(shared_get_optional_user_id)
) -> Optional[UUID]:
    """Dependency to optionally get the user ID."""
    return user_id


async def get_optional_user(
    user: Optional[User] = Depends(shared_get_optional_user)
) -> Optional[User]:
    """Dependency to optionally get the current user."""
    return user


async def get_admin_user(
    user: User = Depends(shared_get_admin_user)
) -> User:
    """Dependency that requires admin role (superuser)."""
    return user


# Alias for backward compatibility
async def get_current_admin_user(
    user: User = Depends(shared_get_admin_user)
) -> User:
    """Alias for get_admin_user - requires admin role."""
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


# Re-export all dependencies
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_user_id",
    "get_optional_user_id",
    "get_optional_user",
    "get_admin_user",
    "get_current_admin_user",
    "require_admin",
    "require_moderator",
]
