from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import AdminUserCreate, AdminUserOut
from ..repository import UserRepository
from ..dependencies import get_db, require_admin
from shared.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    user_in: AdminUserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new admin or moderator account (admin-only).

    This endpoint is restricted to admin users only.

    - **email**: Valid email address (must be unique)
    - **username**: Unique username
    - **password**: User password
    - **role**: User role (admin, moderator, or user)
    - **permissions**: Optional array of permission strings
    - **is_active**: Account active status (default: true)
    """
    repo = UserRepository(db)

    # Check if email already exists
    existing_user = await repo.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_user = await repo.get_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create the admin/moderator user
    new_user = await repo.create_admin_user(user_in)

    logger.info(
        f"Admin user created: {new_user.username} (role: {new_user.role}) by {current_user.username}"
    )

    return new_user
