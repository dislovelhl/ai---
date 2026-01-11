from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from shared.database import SessionLocal
from shared.config import settings
from shared.models import User
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

# Token schema for JWT validation
class TokenData(BaseModel):
    username: Optional[str] = None

# OAuth2 scheme pointing to user_service login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8003/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate JWT token and return the current user.

    Args:
        db: Database session
        token: JWT token from Authorization header

    Returns:
        User object if token is valid

    Raises:
        HTTPException: If token is invalid or user not found
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

    # Query user from database
    query = select(User).where(User.username == token_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if the current user is active.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User object if user is active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
