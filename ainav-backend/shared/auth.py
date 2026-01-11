"""
Shared Authentication Module

Centralized JWT authentication for all backend services.
Implements specs 001, 002, 004, 005.
"""
from uuid import UUID
from typing import Optional, Dict, Any, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from .config import settings
from .database import SessionLocal
from .models import User

logger = logging.getLogger(__name__)

# OAuth2 scheme - tokenUrl relative to API gateway (or user service)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency.
    """
    async with SessionLocal() as session:
        yield session


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
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
    Extract user ID from JWT token without database lookup.
    """
    payload = decode_token(token)
    user_id_str: str = payload.get("sub") or payload.get("user_id")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )


async def get_optional_user_id(
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[UUID]:
    """
    Optional authentication - returns user_id if token present and valid.
    """
    if not token:
        return None
    
    try:
        return await get_current_user_id(token)
    except HTTPException:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the full User object from JWT token (includes DB lookup).
    """
    user_id = await get_current_user_id(token)
    
    # Look up user in database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are active.
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
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    """
    Optional authentication - returns full User object if token present.
    """
    user_id = await get_optional_user_id(token)
    if not user_id:
        return None
        
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


def require_owner_or_admin(user_id: UUID, resource_owner_id: UUID, user: User) -> None:
    """
    Helper to check if user owns a resource or is admin.
    """
    if user_id != resource_owner_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
