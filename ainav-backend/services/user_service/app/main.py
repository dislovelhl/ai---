from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import settings
from .routers import auth, users, personalization, oauth, admin
import logging

logger = logging.getLogger(__name__)

# Validate security settings at startup
settings.validate_security_settings()
if settings.ENVIRONMENT != "production":
    logger.warning(
        "Running in %s mode - ensure SECRET_KEY is properly set in production",
        settings.ENVIRONMENT
    )

app = FastAPI(title="AI Navigator - User Service")

# CORS middleware for OAuth redirects and frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(personalization.router, prefix="/v1/personalization")
app.include_router(oauth.router, prefix="/v1")
app.include_router(admin.router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
