from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from jose import jwt, JWTError
from shared.config import settings
from shared.models import User
from shared.email import email_service
from ..schemas import (
    Token, UserCreate, UserOut,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, MessageResponse
)
from ..repository import UserRepository, pwd_context
from ..dependencies import get_db, get_current_active_user
import logging
import secrets
import redis.asyncio as redis
from typing import Optional

logger = logging.getLogger(__name__)

# Redis client for token storage and rate limiting
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Redis key prefix for password reset tokens
RESET_TOKEN_PREFIX = "password_reset:"
RESET_TOKEN_EXPIRY = 3600  # 1 hour in seconds

# Rate limiting configuration
RATE_LIMIT_PREFIX = "rate_limit:"
RATE_LIMITS = {
    "login": {"requests": 5, "window": 60},           # 5 attempts per minute
    "login_ip": {"requests": 20, "window": 60},       # 20 attempts per minute per IP
    "forgot_password": {"requests": 3, "window": 300}, # 3 requests per 5 minutes
    "register": {"requests": 5, "window": 3600},       # 5 registrations per hour per IP
}


async def check_rate_limit(
    key: str,
    limit_type: str,
    identifier: str
) -> None:
    """
    Check rate limit using sliding window counter in Redis.

    Raises HTTPException if rate limit exceeded.
    """
    limits = RATE_LIMITS.get(limit_type)
    if not limits:
        return

    redis_key = f"{RATE_LIMIT_PREFIX}{limit_type}:{identifier}"
    current_count = await redis_client.get(redis_key)

    if current_count and int(current_count) >= limits["requests"]:
        logger.warning(f"Rate limit exceeded for {limit_type}: {identifier}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please try again in {limits['window']} seconds.",
            headers={"Retry-After": str(limits["window"])}
        )


async def increment_rate_limit(limit_type: str, identifier: str) -> None:
    """Increment rate limit counter for an identifier."""
    limits = RATE_LIMITS.get(limit_type)
    if not limits:
        return

    redis_key = f"{RATE_LIMIT_PREFIX}{limit_type}:{identifier}"

    # Increment counter
    current = await redis_client.incr(redis_key)

    # Set expiry on first increment
    if current == 1:
        await redis_client.expire(redis_key, limits["window"])


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

router = APIRouter(prefix="/auth", tags=["auth"])


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token for authentication."""
    to_encode = data.copy()
    if expires_delta:
        expire = settings.get_utc_now() + expires_delta
    else:
        expire = settings.get_utc_now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserOut)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Rate limited to prevent spam registrations.

    - **email**: Valid email address (must be unique)
    - **username**: Unique username
    - **password**: User password
    """
    client_ip = get_client_ip(request)

    # Check rate limit by IP
    await check_rate_limit("register", "register", client_ip)

    repo = UserRepository(db)
    user = await repo.get_by_email(user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await repo.get_by_username(user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = await repo.create(user_in)

    # Increment rate limit counter
    await increment_rate_limit("register", client_ip)

    # Send welcome email (non-blocking)
    try:
        email_service.send_welcome_email(new_user.email, new_user.username)
    except Exception as e:
        logger.warning(f"Failed to send welcome email: {e}")

    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user and return JWT access token.

    Rate limited to prevent brute force attacks:
    - 5 attempts per minute per username
    - 20 attempts per minute per IP

    Uses OAuth2 password flow with username and password.
    """
    client_ip = get_client_ip(request)

    # Check rate limits (both per-username and per-IP)
    await check_rate_limit("login", "login", form_data.username)
    await check_rate_limit("login_ip", "login_ip", client_ip)

    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        # Increment rate limit on failed attempt
        await increment_rate_limit("login", form_data.username)
        await increment_rate_limit("login_ip", client_ip)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login - no rate limit increment
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def create_reset_token(email: str) -> str:
    """
    Create a password reset token and store it in Redis.

    Token is stored with 1-hour expiry and maps to the user's email.
    """
    token = secrets.token_urlsafe(32)
    redis_key = f"{RESET_TOKEN_PREFIX}{token}"

    # Store token in Redis with email as value and 1-hour expiry
    await redis_client.setex(redis_key, RESET_TOKEN_EXPIRY, email)

    return token


async def verify_reset_token(token: str) -> str:
    """
    Verify a password reset token from Redis.

    Returns the associated email if valid, raises HTTPException otherwise.
    """
    redis_key = f"{RESET_TOKEN_PREFIX}{token}"

    # Get email from Redis
    email = await redis_client.get(redis_key)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    return email


async def invalidate_reset_token(token: str) -> None:
    """
    Invalidate (delete) a password reset token from Redis.

    Called after successful password reset to prevent token reuse.
    """
    redis_key = f"{RESET_TOKEN_PREFIX}{token}"
    await redis_client.delete(redis_key)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_request: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset token.

    Rate limited to 3 requests per 5 minutes to prevent abuse.
    Generates a secure token stored in Redis with 1-hour expiry.

    - In development mode: Returns the token in the response for testing
    - In production mode: Would send an email with the reset link (logged for now)

    Always returns the same message to prevent email enumeration attacks.
    """
    client_ip = get_client_ip(request)

    # Check rate limit by IP and email
    await check_rate_limit("forgot_password", "forgot_password", client_ip)
    await check_rate_limit("forgot_password", "forgot_password", forgot_request.email)

    # Increment rate limit counters
    await increment_rate_limit("forgot_password", client_ip)
    await increment_rate_limit("forgot_password", forgot_request.email)

    repo = UserRepository(db)
    user = await repo.get_by_email(forgot_request.email)

    # Always return the same message to prevent email enumeration
    response_message = "If the email exists, a reset link has been sent"

    if user:
        reset_token = await create_reset_token(user.email)

        # Try to send email if configured
        email_sent = email_service.send_password_reset_email(user.email, reset_token)

        if not email_sent:
            logger.warning(f"Email service not configured. Token for {user.email}: {reset_token}")

        if settings.DEBUG or settings.ENVIRONMENT == "development":
            # In development, also include the token for easy testing
            logger.info(f"Password reset token for {user.email}: {reset_token}")
            return MessageResponse(
                message=f"{response_message}. Dev token: {reset_token}"
            )
        else:
            logger.info(f"Password reset requested for {user.email}")

    return MessageResponse(message=response_message)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using a valid reset token.

    - Validates the token from Redis
    - Updates the user's password
    - Invalidates the token (one-time use)

    Token expires after 1 hour if not used.
    """
    # Verify the token and get associated email
    email = await verify_reset_token(request.token)

    # Find the user
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if not user:
        # This shouldn't happen if token was valid, but handle edge case
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update the password
    user.hashed_password = pwd_context.hash(request.new_password)
    db.add(user)
    await db.commit()

    # Invalidate token (one-time use)
    await invalidate_reset_token(request.token)

    logger.info(f"Password reset completed for {email}")

    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for the authenticated user.

    Requires valid JWT token and current password for verification.

    - **current_password**: The user's current password
    - **new_password**: The new password (min 8 characters)
    """
    # Verify current password
    if not pwd_context.verify(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Update to new password
    current_user.hashed_password = pwd_context.hash(request.new_password)
    db.add(current_user)
    await db.commit()

    logger.info(f"Password changed for user {current_user.username}")

    return MessageResponse(message="Password changed successfully")
