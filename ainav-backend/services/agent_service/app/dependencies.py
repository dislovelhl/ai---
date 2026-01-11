"""
FastAPI Dependencies for Agent Service

Provides reusable dependency injection functions for:
- Database sessions
- User authentication
- Rate limiting
"""
from typing import AsyncGenerator
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import SessionLocal
from shared.config import settings
from shared.models import User
from shared.rate_limit import check_rate_limit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide database session.

    Yields an async SQLAlchemy session that automatically commits
    or rolls back transactions.
    """
    async with SessionLocal() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to extract and validate current user from JWT token.

    Args:
        db: Database session
        token: JWT access token from Authorization header

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
    except JWTError:
        raise credentials_exception

    # Query user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is active.

    Args:
        current_user: The authenticated user

    Returns:
        User: The active user object

    Raises:
        HTTPException: 400 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def check_execution_rate_limit(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to check rate limits for agent workflow executions.

    Enforces per-user, per-tier rate limits to prevent abuse and control
    LLM API costs. Uses Redis-based sliding window algorithm for accurate
    distributed rate limiting.

    Rate limits by tier:
    - free: 50 executions per 24 hours
    - pro: 500 executions per 24 hours
    - enterprise: unlimited (9,999,999 per 24 hours)

    Args:
        current_user: The authenticated active user

    Returns:
        User: The user object if rate limit check passes

    Raises:
        HTTPException: 429 Too Many Requests if user has exceeded their limit.
        Response includes:
        - detail: Error message with limit information
        - headers: Retry-After header with seconds until reset

    Example:
        @router.post("/execute")
        async def execute_workflow(
            user: User = Depends(check_execution_rate_limit)
        ):
            # Execution logic here
            pass
    """
    user_id = str(current_user.id)
    user_tier = current_user.user_tier.value  # Convert enum to string

    # Check rate limit
    is_allowed, stats = await check_rate_limit(user_id, user_tier)

    if not is_allowed:
        # Calculate retry_after in seconds
        retry_after = stats.get("reset_at_timestamp", 0) - int(datetime.now(timezone.utc).timestamp())
        retry_after = max(1, retry_after)  # Ensure at least 1 second

        # Build detailed error message
        error_detail = (
            f"Rate limit exceeded. You have reached your daily execution limit "
            f"of {stats['limit']} executions. Please upgrade your plan or try again later. "
            f"Limit resets at {stats['reset_at']}."
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": error_detail,
                "limit": stats["limit"],
                "used": stats["used"],
                "remaining": stats["remaining"],
                "reset_at": stats["reset_at"],
                "reset_at_timestamp": stats["reset_at_timestamp"],
                "tier": user_tier,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(stats["limit"]),
                "X-RateLimit-Remaining": str(stats["remaining"]),
                "X-RateLimit-Reset": str(stats["reset_at_timestamp"]),
            }
        )

    # Rate limit check passed, return user for downstream use
    return current_user
