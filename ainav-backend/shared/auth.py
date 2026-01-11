"""
Shared authentication module for all microservices.

Provides centralized JWT validation and user authentication utilities
that can be used across content, search, user, and agent services.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import logging

from .config import settings
from .database import SessionLocal

logger = logging.getLogger(__name__)

# OAuth2 scheme for JWT token authentication
# This will extract the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


async def get_db() -> AsyncSession:
    """
    Async database session dependency.

    Yields an async database session that automatically closes after use.
    All services can use this for consistent database access.
    """
    async with SessionLocal() as session:
        yield session


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Dict containing the decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
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


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID as a string (will be converted to UUID by caller)

    Raises:
        HTTPException: If token is invalid or missing user ID
    """
    payload = decode_token(token)
    user_id: Optional[str] = payload.get("sub")

    if user_id is None:
        logger.warning("Token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def validate_token(token: str) -> bool:
    """
    Validate a JWT token without raising exceptions.

    Args:
        token: JWT token string

    Returns:
        True if token is valid, False otherwise
    """
    try:
        decode_token(token)
        return True
    except HTTPException:
        return False


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Dependency to get the current authenticated user.

    Extracts user ID from JWT token, fetches the user from database,
    and returns the full User object. Used for authenticated endpoints
    that need access to user data.

    Args:
        db: Database session dependency
        token: JWT token from Authorization header

    Returns:
        User object from database

    Raises:
        HTTPException: If token is invalid or user not found (401)

    Example:
        @app.get("/me")
        async def get_profile(user: User = Depends(get_current_user)):
            return {"username": user.username, "email": user.email}
    """
    from sqlalchemy import select
    from .models import User
    from uuid import UUID

    # Extract user_id from token
    user_id_str = extract_user_id_from_token(token)

    # Convert to UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError) as e:
        logger.warning(f"Invalid UUID format in token: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error while fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    if user is None:
        logger.warning(f"User not found for id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
