from fastapi import FastAPI
from .routers import search
from shared.database import engine
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Navigator - Search Service")

app.include_router(search.router, prefix="/v1/search", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    try:
        # Test database connectivity
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # Don't fail startup - search features work without DB, just no history


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown."""
    await engine.dispose()
    logger.info("Database connections closed")


@app.get("/")
async def root():
    return {"message": "Welcome to AI Navigator Search Service"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
