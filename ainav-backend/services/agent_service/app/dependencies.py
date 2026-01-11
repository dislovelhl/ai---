"""
Authentication dependencies for agent_service.

Provides JWT-based authentication utilities following the same pattern as user_service.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.database import get_async_session
from shared.config import settings
from shared.models import User
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None


# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Retrieve the current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT token from Authorization header

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Query user by username
    result = await db.execute(
        select(User).where(User.username == token_data.username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that the current user is active.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User: The active user object

    Raises:
        HTTPException: 400 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_id(
    current_user: User = Depends(get_current_user)
) -> UUID:
    """
    Extract the current user's ID from the authenticated user.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        UUID: The authenticated user's ID
    """
    return current_user.id


async def get_optional_current_user_id(
    db: AsyncSession = Depends(get_async_session),
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False))
) -> Optional[UUID]:
    """
    Extract the current user's ID from JWT token if present, otherwise return None.

    This allows endpoints to optionally require authentication - useful for endpoints
    that show different data based on whether the user is authenticated.

    Args:
        db: Database session
        token: Optional JWT token from Authorization header

    Returns:
        Optional[UUID]: The authenticated user's ID if token is valid, None otherwise
    """
    if token is None:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        # Query user by username
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if user is None:
            return None
        return user.id
    except JWTError:
        return None
