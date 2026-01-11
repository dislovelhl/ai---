from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import User, UserRole
from .schemas import UserCreate, UserUpdate, AdminUserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: any) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate) -> User:
        hashed_password = pwd_context.hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            phone=user_in.phone,
            hashed_password=hashed_password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def create_admin_user(self, user_in: AdminUserCreate) -> User:
        """Create admin/moderator account with specified role and permissions"""
        hashed_password = pwd_context.hash(user_in.password)

        # Set is_admin flag based on role
        is_admin = user_in.role in [UserRole.ADMIN, UserRole.MODERATOR]

        db_user = User(
            email=user_in.email,
            username=user_in.username,
            phone=user_in.phone,
            hashed_password=hashed_password,
            role=user_in.role,
            is_admin=is_admin,
            permissions=user_in.permissions or [],
            is_active=user_in.is_active
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def update(self, db_user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
