from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import UserOut, UserUpdate, UsageStatsOut
from ..repository import UserRepository
from ..dependencies import get_db, get_current_active_user
from shared.models import User
from shared.rate_limit import get_usage_stats

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

@router.get("/me/usage", response_model=UsageStatsOut)
async def get_user_usage(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's execution usage statistics.

    Returns the user's current execution count, remaining quota, rate limit,
    and when the limit resets. This helps users understand their API usage
    and plan accordingly.
    """
    # Get user tier as string (handle enum conversion)
    user_tier = current_user.user_tier.value if hasattr(current_user.user_tier, 'value') else str(current_user.user_tier)

    # Fetch usage statistics from Redis rate limiting service
    stats = await get_usage_stats(str(current_user.id), user_tier)

    return UsageStatsOut(**stats)
