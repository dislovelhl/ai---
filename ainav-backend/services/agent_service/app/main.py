"""
AI Navigator - Agent Service

Provides APIs for managing Skills, Agent Workflows, and Executions.
This is the core of the Agentic Creation Platform.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from uuid import UUID

from shared.config import settings
from shared.rate_limit import get_usage_stats
from shared.auth import decode_token
from .routers import skills, workflows, executions, chat, analytics, collaboration

logger = logging.getLogger(__name__)


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to execution endpoint responses.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only add headers for execution endpoints
        if not request.url.path.startswith("/v1/executions/"):
            return response

        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return response

            token = auth_header.split(" ")[1]

            # Use centralized decode_token
            try:
                payload = decode_token(token)
                user_id_str = payload.get("sub") or payload.get("user_id")

                if not user_id_str:
                    return response

                # Get user from database for tier info
                from sqlalchemy import select
                from shared.database import SessionLocal
                from shared.models import User

                async with SessionLocal() as db:
                    result = await db.execute(select(User).where(User.id == UUID(user_id_str)))
                    user = result.scalar_one_or_none()

                    if not user:
                        return response

                    stats = await get_usage_stats(str(user.id), user.user_tier.value)

                    response.headers["X-RateLimit-Limit"] = str(stats["limit"])
                    response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
                    response.headers["X-RateLimit-Reset"] = str(stats["reset_at_timestamp"])

            except Exception:
                # Invalid token or DB error, skip adding headers
                pass

        except Exception as e:
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
    allow_origins=settings.CORS_ORIGINS,
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
