"""
Shared Authentication Module

Centralized JWT authentication for all backend services.
Implements specs 001, 002, 004: Auth Middleware, Agent Service Auth, Consistent User ID Handling.
"""
from uuid import UUID
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from .config import settings
from .database import get_async_session
from .models import User

logger = logging.getLogger(__name__)

# OAuth2 scheme - tokenUrl relative to API gateway
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)


async def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Returns the payload if valid, raises HTTPException otherwise.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception


async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> UUID:
    """
    Extract user ID from JWT token.
    
    This is the primary dependency for routes requiring authentication.
    Returns user_id as UUID for consistent handling across services.
    """
    payload = await decode_token(token)
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    
    if username is None and user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If user_id is directly in token, use it
    if user_id:
        try:
            return UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
            )
    
    # Otherwise, we need to look up user by username
    # This is a fallback for tokens that don't include user_id
    return None  # Will be resolved by get_current_user


async def get_optional_user_id(
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[UUID]:
    """
    Optional authentication - returns user_id if token present and valid, None otherwise.
    
    Use for routes that work with or without authentication.
    """
    if not token:
        return None
    
    try:
        return await get_current_user_id(token)
    except HTTPException:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Get the full User object from JWT token.
    
    Use when you need more than just the user_id (e.g., checking is_superuser).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = await decode_token(token)
    username: str = payload.get("sub")
    
    if username is None:
        raise credentials_exception
    
    # Look up user in database
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are active.
    
    Use for routes requiring an active (non-disabled) user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current user and verify they have admin privileges.
    
    Use for admin-only routes.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_owner_or_admin(user_id: UUID, resource_owner_id: UUID, user: User) -> None:
    """
    Helper to check if user owns a resource or is admin.
    
    Raises HTTPException if neither condition is met.
    """
    if user.id != resource_owner_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
