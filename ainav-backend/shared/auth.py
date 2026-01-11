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
