"""
OAuth2 Social Login Routes

Supports:
- GitHub OAuth2 login
- WeChat OAuth2 login (for Chinese users)

Security Features:
- CSRF protection via Redis-stored state tokens
- State tokens expire after 10 minutes
- One-time use state validation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config import settings
from shared.models import User
from ..repository import UserRepository, pwd_context
from ..dependencies import get_db
from .auth import create_access_token
from datetime import timedelta
import httpx
import secrets
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Redis client for OAuth state storage (CSRF protection)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# OAuth state prefix and expiry
OAUTH_STATE_PREFIX = "oauth_state:"
OAUTH_STATE_EXPIRY = 600  # 10 minutes


async def store_oauth_state(state: str, provider: str) -> None:
    """Store OAuth state in Redis for CSRF validation."""
    redis_key = f"{OAUTH_STATE_PREFIX}{state}"
    await redis_client.setex(redis_key, OAUTH_STATE_EXPIRY, provider)


async def validate_oauth_state(state: str, expected_provider: str) -> bool:
    """
    Validate OAuth state from Redis.

    Returns True if valid, raises HTTPException otherwise.
    State is deleted after validation (one-time use).
    """
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter - possible CSRF attack"
        )

    redis_key = f"{OAUTH_STATE_PREFIX}{state}"
    stored_provider = await redis_client.get(redis_key)

    if not stored_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state - please try logging in again"
        )

    if stored_provider != expected_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State provider mismatch - possible CSRF attack"
        )

    # Delete state after validation (one-time use)
    await redis_client.delete(redis_key)
    return True

router = APIRouter(prefix="/oauth", tags=["oauth"])


# =============================================================================
# GitHub OAuth2
# =============================================================================

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


@router.get("/github/authorize")
async def github_authorize():
    """
    Redirect user to GitHub for OAuth2 authorization.

    Returns a redirect to GitHub's authorization page.
    State is stored in Redis for CSRF validation during callback.
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured"
        )

    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in Redis for validation during callback
    await store_oauth_state(state, "github")

    # Build authorization URL
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email",
        "state": state,
    }

    query = "&".join(f"{k}={v}" for k, v in params.items())
    authorize_url = f"{GITHUB_AUTHORIZE_URL}?{query}"

    return {
        "authorize_url": authorize_url,
        "state": state,
    }


@router.get("/github/callback")
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State for CSRF verification"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle GitHub OAuth2 callback.

    Exchanges the authorization code for an access token,
    fetches user info, and creates/updates the user in our database.

    CSRF Protection: State is validated against Redis-stored value.
    Returns a redirect to the frontend with the JWT token.
    """
    # Validate CSRF state first (before any other processing)
    await validate_oauth_state(state, "github")

    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured"
        )

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )

        if token_response.status_code != 200:
            logger.error(f"GitHub token exchange failed: {token_response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            logger.error(f"No access token in response: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )

        # Fetch user info from GitHub
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        user_response = await client.get(GITHUB_USER_URL, headers=headers)
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from GitHub"
            )

        github_user = user_response.json()

        # Get user's primary email if not public
        email = github_user.get("email")
        if not email:
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Find primary email
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        email = e.get("email")
                        break

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not get email from GitHub account"
            )

    # Find or create user
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    github_id = str(github_user.get("id"))
    github_username = github_user.get("login")

    if not user:
        # Create new user
        # Generate a unique username if the GitHub username is taken
        username = github_username
        existing_user = await repo.get_by_username(username)
        if existing_user:
            username = f"{github_username}_{github_id[:8]}"

        # Create user with a random password (they'll use OAuth to login)
        random_password = secrets.token_urlsafe(32)
        user = User(
            email=email,
            username=username,
            hashed_password=pwd_context.hash(random_password),
            github_id=github_id,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Created new user from GitHub: {email}")
    else:
        # Update existing user's GitHub ID if not set
        if not user.github_id:
            user.github_id = github_id
            db.add(user)
            await db.commit()

        logger.info(f"Existing user logged in via GitHub: {email}")

    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}&provider=github"
    return RedirectResponse(url=redirect_url)


# =============================================================================
# WeChat OAuth2 (Placeholder - requires WeChat Open Platform registration)
# =============================================================================

WECHAT_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect"
WECHAT_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WECHAT_USER_URL = "https://api.weixin.qq.com/sns/userinfo"


@router.get("/wechat/authorize")
async def wechat_authorize():
    """
    Redirect user to WeChat for OAuth2 authorization.

    Note: WeChat OAuth requires registration on WeChat Open Platform
    and approval for website login capability.
    State is stored in Redis for CSRF validation during callback.
    """
    if not settings.WECHAT_APP_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="WeChat OAuth is not configured"
        )

    state = secrets.token_urlsafe(32)

    # Store state in Redis for validation during callback
    await store_oauth_state(state, "wechat")

    params = {
        "appid": settings.WECHAT_APP_ID,
        "redirect_uri": settings.WECHAT_REDIRECT_URI,
        "response_type": "code",
        "scope": "snsapi_login",
        "state": state,
    }

    query = "&".join(f"{k}={v}" for k, v in params.items())
    authorize_url = f"{WECHAT_AUTHORIZE_URL}?{query}#wechat_redirect"

    return {
        "authorize_url": authorize_url,
        "state": state,
    }


@router.get("/wechat/callback")
async def wechat_callback(
    code: str = Query(..., description="Authorization code from WeChat"),
    state: str = Query(..., description="State for CSRF verification"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle WeChat OAuth2 callback.

    CSRF Protection: State is validated against Redis-stored value.
    Note: Implementation pending WeChat Open Platform registration.
    """
    # Validate CSRF state first (before any other processing)
    await validate_oauth_state(state, "wechat")

    if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="WeChat OAuth is not configured"
        )

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.get(
            WECHAT_TOKEN_URL,
            params={
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )

        token_data = token_response.json()

        if "errcode" in token_data:
            logger.error(f"WeChat token error: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"WeChat error: {token_data.get('errmsg')}"
            )

        access_token = token_data.get("access_token")
        openid = token_data.get("openid")

        # Fetch user info
        user_response = await client.get(
            WECHAT_USER_URL,
            params={
                "access_token": access_token,
                "openid": openid,
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from WeChat"
            )

        wechat_user = user_response.json()

        if "errcode" in wechat_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"WeChat error: {wechat_user.get('errmsg')}"
            )

    # Find or create user
    repo = UserRepository(db)

    # WeChat uses unionid for cross-platform user identification
    unionid = wechat_user.get("unionid") or openid
    nickname = wechat_user.get("nickname", f"wx_{unionid[:8]}")

    # Try to find existing user by WeChat ID
    # Note: This requires adding wechat_id field to User model
    # For now, we'll use a placeholder email
    placeholder_email = f"wechat_{unionid}@placeholder.local"
    user = await repo.get_by_email(placeholder_email)

    if not user:
        # Create new user
        random_password = secrets.token_urlsafe(32)
        user = User(
            email=placeholder_email,
            username=nickname,
            hashed_password=pwd_context.hash(random_password),
            wechat_id=unionid,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"Created new user from WeChat: {nickname}")
    else:
        logger.info(f"Existing user logged in via WeChat: {nickname}")

    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}&provider=wechat"
    return RedirectResponse(url=redirect_url)
