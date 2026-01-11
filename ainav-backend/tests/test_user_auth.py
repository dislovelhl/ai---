"""
Test suite for user authentication endpoints.

This module tests:
- User registration with validation and rate limiting
- Login with JWT token generation
- Password reset flow (forgot password, reset password)
- Password change for authenticated users
- Rate limiting across all auth endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.models import User
from services.user_service.app.main import app
from services.user_service.app.dependencies import get_db
from services.user_service.app.routers.auth import (
    create_access_token,
    create_reset_token,
    verify_reset_token,
    invalidate_reset_token,
    RESET_TOKEN_PREFIX,
    RESET_TOKEN_EXPIRY
)
from datetime import timedelta
from jose import jwt
from shared.config import settings


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for rate limiting and token storage."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_email_service():
    """Mock email service to prevent actual email sending."""
    with patch('services.user_service.app.routers.auth.email_service') as mock:
        mock.send_welcome_email = MagicMock(return_value=True)
        mock.send_password_reset_email = MagicMock(return_value=True)
        yield mock


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession, override_get_db) -> AsyncClient:
    """Create test client with database dependency override."""
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for registration tests."""
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }


@pytest_asyncio.fixture
async def registered_user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create and return a registered user in the database."""
    from services.user_service.app.repository import UserRepository, pwd_context

    repo = UserRepository(db_session)
    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=pwd_context.hash(sample_user_data["password"]),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# TOKEN GENERATION TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestTokenGeneration:
    """Test JWT token creation and validation."""

    async def test_create_access_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Verify token can be decoded
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded

    async def test_create_access_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "testuser"

        # Expiration should be set
        assert "exp" in decoded

    async def test_token_contains_correct_algorithm(self):
        """Test token uses the correct signing algorithm."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Decode with algorithm verification
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert decoded["sub"] == "testuser"


# ============================================================================
# USER REGISTRATION TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoint."""

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_register_new_user_success(
        self,
        mock_redis,
        test_client: AsyncClient,
        db_session: AsyncSession,
        mock_email_service
    ):
        """Test successful user registration."""
        # Setup mock Redis for rate limiting
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }

        response = await test_client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
        assert data["is_active"] is True

        # Verify user was created in database
        result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == user_data["email"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_register_duplicate_email(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test registration with already registered email."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        user_data = {
            "email": registered_user.email,
            "username": "differentusername",
            "password": "SecurePass123!"
        }

        response = await test_client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_register_duplicate_username(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test registration with already taken username."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        user_data = {
            "email": "different@example.com",
            "username": registered_user.username,
            "password": "SecurePass123!"
        }

        response = await test_client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_register_rate_limit(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test rate limiting on registration endpoint."""
        # Simulate rate limit exceeded
        mock_redis.get = AsyncMock(return_value="5")  # Already at limit

        user_data = {
            "email": "ratelimit@example.com",
            "username": "ratelimituser",
            "password": "SecurePass123!"
        }

        response = await test_client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_register_invalid_email(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test registration with invalid email format."""
        mock_redis.get = AsyncMock(return_value=None)

        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "SecurePass123!"
        }

        response = await test_client.post("/v1/auth/register", json=user_data)

        # Should fail validation
        assert response.status_code == 422


# ============================================================================
# LOGIN TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestLogin:
    """Test login endpoint and token generation."""

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_login_success(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User,
        sample_user_data: dict
    ):
        """Test successful login with correct credentials."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }

        response = await test_client.post(
            "/v1/auth/login",
            data=login_data  # OAuth2 uses form data
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid
        token = data["access_token"]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == sample_user_data["username"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_login_invalid_username(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test login with non-existent username."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        login_data = {
            "username": "nonexistent",
            "password": "AnyPassword123!"
        }

        response = await test_client.post("/v1/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_login_invalid_password(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test login with incorrect password."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        login_data = {
            "username": registered_user.username,
            "password": "WrongPassword123!"
        }

        response = await test_client.post("/v1/auth/login", data=login_data)

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_login_rate_limit_per_username(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test rate limiting per username on login."""
        mock_redis.get = AsyncMock(return_value="5")  # At limit

        login_data = {
            "username": registered_user.username,
            "password": "AnyPassword"
        }

        response = await test_client.post("/v1/auth/login", data=login_data)

        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_login_increments_rate_limit_on_failure(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test that failed login increments rate limit counter."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        login_data = {
            "username": registered_user.username,
            "password": "WrongPassword"
        }

        await test_client.post("/v1/auth/login", data=login_data)

        # Verify rate limit was incremented
        assert mock_redis.incr.called


# ============================================================================
# PASSWORD RESET FLOW TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestPasswordResetFlow:
    """Test password reset (forgot password and reset password)."""

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_forgot_password_success(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User,
        mock_email_service
    ):
        """Test forgot password request for existing user."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)
        mock_redis.setex = AsyncMock(return_value=True)

        request_data = {
            "email": registered_user.email
        }

        # Mock development mode to get token in response
        with patch('services.user_service.app.routers.auth.settings') as mock_settings:
            mock_settings.DEBUG = True
            mock_settings.ENVIRONMENT = "development"
            mock_settings.SECRET_KEY = settings.SECRET_KEY
            mock_settings.ALGORITHM = settings.ALGORITHM
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            mock_settings.get_utc_now = settings.get_utc_now

            response = await test_client.post(
                "/v1/auth/forgot-password",
                json=request_data
            )

        assert response.status_code == 200
        data = response.json()
        assert "reset link has been sent" in data["message"] or "Dev token:" in data["message"]

        # Verify token was stored in Redis
        assert mock_redis.setex.called

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_forgot_password_nonexistent_email(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test forgot password with non-existent email (should not reveal)."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock(return_value=True)

        request_data = {
            "email": "nonexistent@example.com"
        }

        response = await test_client.post(
            "/v1/auth/forgot-password",
            json=request_data
        )

        # Should return same message to prevent email enumeration
        assert response.status_code == 200
        assert "reset link has been sent" in response.json()["message"].lower()

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_forgot_password_rate_limit(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test rate limiting on forgot password endpoint."""
        mock_redis.get = AsyncMock(return_value="3")  # At limit

        request_data = {
            "email": "test@example.com"
        }

        response = await test_client.post(
            "/v1/auth/forgot-password",
            json=request_data
        )

        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_reset_password_success(
        self,
        mock_redis,
        test_client: AsyncClient,
        db_session: AsyncSession,
        registered_user: User
    ):
        """Test successful password reset with valid token."""
        test_token = "valid-reset-token-12345"

        # Mock Redis to return the user's email for this token
        mock_redis.get = AsyncMock(return_value=registered_user.email)
        mock_redis.delete = AsyncMock(return_value=True)

        reset_data = {
            "token": test_token,
            "new_password": "NewSecurePass456!"
        }

        response = await test_client.post(
            "/v1/auth/reset-password",
            json=reset_data
        )

        assert response.status_code == 200
        assert "reset successfully" in response.json()["message"].lower()

        # Verify token was deleted from Redis (one-time use)
        assert mock_redis.delete.called

        # Verify password was actually changed in database
        await db_session.refresh(registered_user)
        from services.user_service.app.repository import pwd_context
        assert pwd_context.verify("NewSecurePass456!", registered_user.hashed_password)

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_reset_password_invalid_token(
        self,
        mock_redis,
        test_client: AsyncClient
    ):
        """Test password reset with invalid or expired token."""
        mock_redis.get = AsyncMock(return_value=None)  # Token not found

        reset_data = {
            "token": "invalid-token",
            "new_password": "NewPassword123!"
        }

        response = await test_client.post(
            "/v1/auth/reset-password",
            json=reset_data
        )

        assert response.status_code == 400
        assert "Invalid or expired token" in response.json()["detail"]

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_reset_password_token_one_time_use(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User
    ):
        """Test that reset token can only be used once."""
        test_token = "one-time-token-12345"

        # First use - token exists
        mock_redis.get = AsyncMock(return_value=registered_user.email)
        mock_redis.delete = AsyncMock(return_value=True)

        reset_data = {
            "token": test_token,
            "new_password": "FirstPassword123!"
        }

        response = await test_client.post(
            "/v1/auth/reset-password",
            json=reset_data
        )
        assert response.status_code == 200

        # Verify delete was called (invalidating token)
        assert mock_redis.delete.called

        # Second use - token no longer exists
        mock_redis.get = AsyncMock(return_value=None)

        response = await test_client.post(
            "/v1/auth/reset-password",
            json=reset_data
        )
        assert response.status_code == 400
        assert "Invalid or expired token" in response.json()["detail"]


# ============================================================================
# CHANGE PASSWORD TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestChangePassword:
    """Test authenticated password change."""

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_change_password_success(
        self,
        mock_redis,
        test_client: AsyncClient,
        db_session: AsyncSession,
        registered_user: User,
        sample_user_data: dict
    ):
        """Test successful password change for authenticated user."""
        mock_redis.get = AsyncMock(return_value=None)

        # Login to get token
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        login_response = await test_client.post("/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Change password
        change_data = {
            "current_password": sample_user_data["password"],
            "new_password": "NewSecurePassword123!"
        }

        response = await test_client.post(
            "/v1/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "changed successfully" in response.json()["message"].lower()

        # Verify new password works
        await db_session.refresh(registered_user)
        from services.user_service.app.repository import pwd_context
        assert pwd_context.verify("NewSecurePassword123!", registered_user.hashed_password)

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_change_password_wrong_current_password(
        self,
        mock_redis,
        test_client: AsyncClient,
        registered_user: User,
        sample_user_data: dict
    ):
        """Test password change with incorrect current password."""
        mock_redis.get = AsyncMock(return_value=None)

        # Login to get token
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        login_response = await test_client.post("/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Try to change with wrong current password
        change_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        }

        response = await test_client.post(
            "/v1/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]

    async def test_change_password_unauthenticated(
        self,
        test_client: AsyncClient
    ):
        """Test that password change requires authentication."""
        change_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!"
        }

        response = await test_client.post(
            "/v1/auth/change-password",
            json=change_data
        )

        # Should require authentication
        assert response.status_code == 401

    async def test_change_password_invalid_token(
        self,
        test_client: AsyncClient
    ):
        """Test password change with invalid JWT token."""
        change_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!"
        }

        response = await test_client.post(
            "/v1/auth/change-password",
            json=change_data,
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401


# ============================================================================
# RESET TOKEN UTILITY TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.auth
class TestResetTokenUtilities:
    """Test password reset token utility functions."""

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_create_reset_token(self, mock_redis):
        """Test creating a password reset token."""
        mock_redis.setex = AsyncMock(return_value=True)

        email = "test@example.com"
        token = await create_reset_token(email)

        assert token is not None
        assert len(token) > 20  # Should be a long random string

        # Verify token was stored in Redis
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"{RESET_TOKEN_PREFIX}{token}"
        assert call_args[0][1] == RESET_TOKEN_EXPIRY
        assert call_args[0][2] == email

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_verify_reset_token_valid(self, mock_redis):
        """Test verifying a valid reset token."""
        test_email = "test@example.com"
        test_token = "valid-token-12345"

        mock_redis.get = AsyncMock(return_value=test_email)

        email = await verify_reset_token(test_token)

        assert email == test_email
        mock_redis.get.assert_called_once_with(f"{RESET_TOKEN_PREFIX}{test_token}")

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_verify_reset_token_invalid(self, mock_redis):
        """Test verifying an invalid/expired reset token."""
        mock_redis.get = AsyncMock(return_value=None)

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await verify_reset_token("invalid-token")

        assert exc_info.value.status_code == 400
        assert "Invalid or expired token" in exc_info.value.detail

    @patch('services.user_service.app.routers.auth.redis_client')
    async def test_invalidate_reset_token(self, mock_redis):
        """Test invalidating a reset token."""
        mock_redis.delete = AsyncMock(return_value=True)

        test_token = "token-to-invalidate"
        await invalidate_reset_token(test_token)

        mock_redis.delete.assert_called_once_with(f"{RESET_TOKEN_PREFIX}{test_token}")
