"""
AI Navigator - Agent Service

Provides APIs for managing Skills, Agent Workflows, and Executions.
This is the core of the Agentic Creation Platform.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import JWTError, jwt
import logging

from shared.config import settings
from shared.rate_limit import get_usage_stats

from .routers import skills, workflows, executions, chat, analytics, collaboration

logger = logging.getLogger(__name__)


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to execution endpoint responses.

    Adds the following headers to all execution-related endpoints:
    - X-RateLimit-Limit: Maximum requests allowed in window
    - X-RateLimit-Remaining: Requests remaining in current window
    - X-RateLimit-Reset: Unix timestamp when window resets
    """

    async def dispatch(self, request: Request, call_next):
        # Process the request and get the response
        response = await call_next(request)

        # Only add headers for execution endpoints
        if not request.url.path.startswith("/v1/executions/"):
            return response

        # Try to extract user from JWT token
        try:
            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return response

            # Extract token
            token = auth_header.split(" ")[1]

            # Decode JWT to get user info
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                username = payload.get("sub")

                if not username:
                    return response

                # Get user from database to fetch user_id and tier
                from sqlalchemy import select
                from shared.database import async_session_factory
                from shared.models import User

                async with async_session_factory() as db:
                    result = await db.execute(select(User).where(User.username == username))
                    user = result.scalar_one_or_none()

                    if not user:
                        return response

                    # Get rate limit stats
                    user_id = str(user.id)
                    user_tier = user.user_tier.value
                    stats = await get_usage_stats(user_id, user_tier)

                    # Add rate limit headers to response
                    response.headers["X-RateLimit-Limit"] = str(stats["limit"])
                    response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
                    response.headers["X-RateLimit-Reset"] = str(stats["reset_at_timestamp"])

            except JWTError:
                # Invalid token, skip adding headers
                pass

        except Exception as e:
            # Log error but don't fail the request
            logger.warning(f"Failed to add rate limit headers: {e}")

        return response


app = FastAPI(
    title="AI Navigator - Agent Service",
    description="Agent workflow builder and execution service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limit headers middleware (add before CORS)
app.add_middleware(RateLimitHeadersMiddleware)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router, prefix="/v1/skills", tags=["Skills"])
app.include_router(workflows.router, prefix="/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/v1/executions", tags=["Executions"])
app.include_router(chat.router, prefix="/v1/agents", tags=["Agent Chat"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
app.include_router(collaboration.router, prefix="/v1/collaboration", tags=["Collaboration"])



@app.get("/")
async def root():
    return {
        "service": "agent-service",
        "version": "1.0.0",
        "description": "Agent workflow builder and execution service",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-service"}
