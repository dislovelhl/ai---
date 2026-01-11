from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import UserOut, UserUpdate
from ..repository import UserRepository
from ..dependencies import get_db, get_current_active_user
from shared.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    return await repo.update(current_user, user_in)
