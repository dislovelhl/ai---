"""
Authentication dependencies for agent_service.

Provides JWT-based authentication utilities by wrapping the shared authentication module.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from shared.database import get_async_session
from shared.models import User
from shared.auth import (
    get_current_user as shared_get_current_user,
    get_current_active_user as shared_get_current_active_user,
    get_current_user_id as shared_get_current_user_id,
    get_optional_user_id as shared_get_optional_user_id,
    get_admin_user as shared_get_admin_user
)


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
