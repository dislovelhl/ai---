"""
Pytest configuration and shared fixtures for AI Navigation Platform.

This module provides fixtures for:
- Async event loop management
- Database sessions with transaction rollback
- HTTP clients for API testing
- Mock external services
- Test data factories
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool, StaticPool

# Handle SQLAlchemy 2.0 imports with fallback
try:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import Session, sessionmaker
except ImportError as e:
    raise ImportError(
        "SQLAlchemy 2.0+ is required for async testing. "
        "Please install the project dependencies: pip install -r requirements.txt\n"
        f"Original error: {e}"
    )

from shared.config import settings
from shared.database import SessionLocal, engine, get_async_session
from shared.models import Base


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables and configuration."""
    # Use test database if not already set
    if "test" not in os.getenv("DATABASE_URL", ""):
        os.environ["DATABASE_URL"] = settings.DATABASE_URL.replace(
            "/ainav_db", "/ainav_test_db"
        )

    # Disable email sending in tests
    os.environ["SMTP_USER"] = ""
    os.environ["SMTP_PASSWORD"] = ""

    # Use test-specific secret key
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production-use"

    yield

    # Cleanup after all tests
    pass


# ============================================================================
# ASYNC EVENT LOOP
# ============================================================================
# Note: We don't override event_loop anymore as pytest-asyncio handles it
# Tests use the default function-scoped event loop from pytest-asyncio


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Get test database URL."""
    db_url = settings.DATABASE_URL
    # Replace main database with test database
    if "/ainav_db" in db_url:
        db_url = db_url.replace("/ainav_db", "/ainav_test_db")
    return db_url


@pytest.fixture(scope="session")
def test_engine_sync(test_db_url: str):
    """
    Create async engine for test database (session-scoped).

    This creates the engine once for all tests. Individual tests use
    function-scoped sessions with transaction rollback.
    """
    import asyncio

    engine = create_async_engine(
        test_db_url,
        echo=False,  # Set to True for SQL debugging
        poolclass=NullPool,  # Don't pool connections in tests
    )

    # Create all tables at test session start
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())

    yield engine

    # Drop all tables at test session end
    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(drop_tables())


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_engine_sync):
    """
    Provide the async engine to function-scoped tests.

    This bridges the session-scoped sync fixture to async tests.
    """
    return test_engine_sync


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session with automatic rollback.

    Each test gets a fresh database state through transaction rollback.
    This ensures test isolation without recreating the entire database.

    Usage:
        async def test_create_user(db_session: AsyncSession):
            user = User(username="test")
            db_session.add(user)
            await db_session.commit()
            # Transaction automatically rolled back after test
    """
    # Create a connection that we'll use for the test
    connection = await test_engine.connect()

    # Begin a transaction
    transaction = await connection.begin()

    # Create session bound to the transaction
    async_session_maker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )

    session = async_session_maker()

    try:
        yield session
    finally:
        # Close the session
        await session.close()
        # Rollback the transaction
        await transaction.rollback()
        # Close the connection
        await connection.close()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """
    Override the get_async_session dependency for FastAPI.

    Usage in tests:
        app.dependency_overrides[get_async_session] = override_get_db
    """
    async def _get_db_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    return _get_db_override


# ============================================================================
# HTTP CLIENT FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for API testing.

    Usage:
        async def test_api(async_client: AsyncClient):
            response = await async_client.get("/v1/health")
            assert response.status_code == 200
    """
    async with AsyncClient(
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
        timeout=10.0,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient, auth_token: str) -> AsyncClient:
    """
    Provide an authenticated async HTTP client with JWT token.

    Usage:
        async def test_protected_endpoint(authenticated_client: AsyncClient):
            response = await authenticated_client.get("/v1/users/me")
            assert response.status_code == 200
    """
    async_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return async_client


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def auth_token() -> str:
    """
    Generate a test JWT token.

    Note: This is a placeholder. Will be implemented in subtask 2.1
    when JWT utilities are tested.
    """
    # TODO: Import and use actual JWT creation logic
    return "test-jwt-token-placeholder"


@pytest.fixture
def test_user_data() -> dict:
    """Provide test user data for registration/login tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
    }


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.exists = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_meilisearch():
    """Mock Meilisearch client for testing."""
    mock = MagicMock()
    mock.index = MagicMock()
    mock.index.return_value.search = AsyncMock(return_value={"hits": [], "estimatedTotalHits": 0})
    mock.index.return_value.add_documents = AsyncMock(return_value={"uid": 0})
    mock.index.return_value.update_documents = AsyncMock(return_value={"uid": 0})
    mock.index.return_value.delete_document = AsyncMock(return_value={"uid": 0})
    return mock


@pytest.fixture
def mock_celery():
    """Mock Celery task for testing."""
    mock = MagicMock()
    mock.delay = MagicMock(return_value=MagicMock(id="test-task-id"))
    mock.apply_async = MagicMock(return_value=MagicMock(id="test-task-id"))
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI/DeepSeek client for LLM testing."""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="This is a test LLM response",
                        role="assistant"
                    )
                )
            ]
        )
    )
    return mock


@pytest.fixture
def mock_embedding_model():
    """Mock sentence transformer for embedding tests."""
    import numpy as np

    mock = MagicMock()
    # Return a 384-dimension vector (matching pgvector config)
    mock.encode = MagicMock(return_value=np.random.rand(384).astype('float32'))
    return mock


# ============================================================================
# DATA FACTORY FIXTURES
# ============================================================================

@pytest.fixture
def category_factory():
    """Factory for creating test category data."""
    def _create_category(**kwargs):
        defaults = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "A test category description",
            "icon": "test-icon",
            "order": 1,
        }
        defaults.update(kwargs)
        return defaults

    return _create_category


@pytest.fixture
def tool_factory():
    """Factory for creating test tool data."""
    def _create_tool(**kwargs):
        defaults = {
            "name": "Test Tool",
            "slug": "test-tool",
            "description": "A test tool description",
            "url": "https://example.com",
            "logo_url": "https://example.com/logo.png",
            "is_free": True,
            "is_china_accessible": True,
        }
        defaults.update(kwargs)
        return defaults

    return _create_tool


@pytest.fixture
def workflow_factory():
    """Factory for creating test workflow data."""
    def _create_workflow(**kwargs):
        defaults = {
            "name": "Test Workflow",
            "description": "A test workflow description",
            "graph_json": {
                "nodes": [
                    {"id": "1", "type": "start", "data": {"label": "Start"}},
                    {"id": "2", "type": "end", "data": {"label": "End"}},
                ],
                "edges": [
                    {"id": "e1", "source": "1", "target": "2"},
                ],
            },
            "is_public": False,
        }
        defaults.update(kwargs)
        return defaults

    return _create_workflow


@pytest.fixture
def skill_factory():
    """Factory for creating test skill data."""
    def _create_skill(**kwargs):
        defaults = {
            "name": "Test Skill",
            "description": "A test skill description",
            "openapi_schema": {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {},
            },
        }
        defaults.update(kwargs)
        return defaults

    return _create_skill


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def anyio_backend():
    """Specify the async backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
def caplog_debug(caplog):
    """Set logging to DEBUG level for tests."""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup resources after each test."""
    yield
    # Add any cleanup logic here (e.g., clear caches, close connections)
    pass
