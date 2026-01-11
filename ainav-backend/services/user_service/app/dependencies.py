from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import SessionLocal
from shared.config import settings
from shared.models import User, UserRole
from .repository import UserRepository
from .schemas import TokenData
from typing import AsyncGenerator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
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

    repo = UserRepository(db)
    user = await repo.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires the current user to have admin role.

    Raises HTTPException with 403 status if user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def require_moderator(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires the current user to have moderator or admin role.

    Raises HTTPException with 403 status if user is not a moderator or admin.
    """
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator privileges required"
        )
    return current_user
