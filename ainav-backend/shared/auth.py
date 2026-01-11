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

# Optional OAuth2 scheme that doesn't raise errors when token is missing
# Used for public endpoints that want to provide personalized content when user is authenticated
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)


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


async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
):
    """
    Dependency to get the current authenticated user's ID.

    Lightweight alternative to get_current_user that only extracts and validates
    the UUID from the JWT token without querying the database. Use this when you
    only need the user ID and don't need the full User object.

    Args:
        token: JWT token from Authorization header

    Returns:
        UUID: User ID extracted from token

    Raises:
        HTTPException: If token is invalid or contains invalid UUID (401)

    Example:
        @app.post("/workflows")
        async def create_workflow(
            workflow: WorkflowCreate,
            user_id: UUID = Depends(get_current_user_id)
        ):
            # user_id is already a UUID, no DB query needed
            return await create_workflow_for_user(workflow, user_id)
    """
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

    return user_id


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


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency to get the current authenticated and active user.

    Wraps get_current_user and adds an additional check to ensure the user
    account is active (is_active=True). Use this for endpoints that should
    only be accessible to active users.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User object from database (guaranteed to be active)

    Raises:
        HTTPException: If user account is inactive (403 Forbidden)

    Example:
        @app.post("/workflows")
        async def create_workflow(
            workflow: WorkflowCreate,
            user: User = Depends(get_current_active_user)
        ):
            # user is guaranteed to be authenticated AND active
            return await create_workflow_for_user(workflow, user)
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user attempted access: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
):
    """
    Dependency to optionally get the current authenticated user.

    This is used for public endpoints that want to provide personalized
    content when a user is authenticated, but still work for anonymous users.
    Unlike get_current_user, this does NOT raise exceptions for missing
    or invalid tokens.

    Args:
        db: Database session dependency
        token: Optional JWT token from Authorization header

    Returns:
        User object if token is valid and user exists, None otherwise

    Example:
        @app.get("/tools")
        async def list_tools(
            user: Optional[User] = Depends(get_optional_user)
        ):
            # Show personalized content if user is authenticated
            if user:
                return await get_tools_with_favorites(user.id)
            # Show public content for anonymous users
            return await get_public_tools()
    """
    from sqlalchemy import select
    from .models import User
    from uuid import UUID

    # If no token provided, return None (anonymous user)
    if token is None:
        return None

    # Try to extract and validate user_id from token
    try:
        user_id_str = extract_user_id_from_token(token)
    except HTTPException:
        # Token is invalid or malformed, treat as anonymous
        logger.debug("Invalid token in optional auth, treating as anonymous")
        return None

    # Try to convert to UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        logger.debug(f"Invalid UUID format in optional auth: {user_id_str}")
        return None

    # Try to fetch user from database
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.warning(f"Database error in optional auth: {e}")
        return None

    # Return user if found, None if not found
    if user is None:
        logger.debug(f"User not found in optional auth for id: {user_id}")
        return None

    return user
