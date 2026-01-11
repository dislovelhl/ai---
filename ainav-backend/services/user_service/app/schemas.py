from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from shared.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminUserCreate(UserBase):
    """Schema for creating admin/moderator accounts (admin-only)"""
    password: str
    role: UserRole = Field(default=UserRole.USER, description="User role (admin, moderator, user)")
    permissions: Optional[List[str]] = Field(default=None, description="Optional permissions array")
    is_active: bool = Field(default=True, description="Account active status")

class AdminUserOut(UserBase):
    """Admin view of user with role and permissions"""
    id: UUID
    is_active: bool
    is_superuser: bool
    is_admin: bool
    role: UserRole
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

class MessageResponse(BaseModel):
    message: str
