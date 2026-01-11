"""
Authentication utilities for search service.

Provides JWT token validation and optional user authentication for search features.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config import settings
from shared.models import User
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

# OAuth2 scheme for extracting JWT tokens from Authorization header
# auto_error=False makes authentication optional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)


async def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UUID]:
    """
    Extract user_id from JWT token.

    Returns None if no token provided or token is invalid (for optional auth).
    Used for endpoints where authentication is optional but enables extra features.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token missing 'sub' claim")
            return None

        # Extract user_id if present (newer tokens include it)
        user_id_str = payload.get("user_id")
        if user_id_str:
            try:
                return UUID(user_id_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id in token: {user_id_str}")

        # For older tokens without user_id, we'd need to query the database
        # For now, we'll require the user_id in the token payload
        # The user_service should include user_id when creating tokens
        logger.info("Token valid but missing user_id, requires database lookup")
        return None

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def require_authentication(
    token: str = Depends(oauth2_scheme)
) -> UUID:
    """
    Require valid authentication and return user_id.

    Raises 401 Unauthorized if no token or invalid token.
    Used for endpoints that require authentication.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id_str = payload.get("user_id")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = UUID(user_id_str)
            return user_id
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: malformed user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
