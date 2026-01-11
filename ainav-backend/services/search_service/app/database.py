"""
Database session management for search service.

Provides async database session dependency for accessing PostgreSQL.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import SessionLocal
from typing import AsyncGenerator


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.

    Usage:
        @router.get("/endpoint")
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass

    The session is automatically closed after the request completes.
    """
    async with SessionLocal() as session:
        yield session
