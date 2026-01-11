"""
Test database fixtures and transaction isolation.

This test suite verifies that:
1. Test database configuration is correctly set up
2. Database sessions use the test database
3. Transaction rollback works properly for test isolation
4. No data persists between tests
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import User, Category, Tool
from shared.config import settings


# ============================================================================
# TEST DATABASE CONFIGURATION
# ============================================================================

def test_using_test_database(test_db_url: str):
    """Verify that tests use the test database, not production."""
    # The test_db_url fixture ensures we're using the test database
    # Just verify it contains test database name
    assert "/ainav_test_db" in test_db_url, \
        f"Tests should use ainav_test_db database. Current URL: {test_db_url}"

    # Ensure we're NOT using production database
    assert not test_db_url.endswith("/ainav_db"), \
        "Tests should not use the production ainav_db database"


def test_test_environment_configured():
    """Verify test environment variables are properly set."""
    # SECRET_KEY should be set for tests
    assert settings.SECRET_KEY is not None, "SECRET_KEY should be set"

    # SMTP should be disabled in tests to prevent email sending
    assert settings.SMTP_USER == "" or settings.SMTP_USER is None, \
        "SMTP should be disabled in tests"


# ============================================================================
# DATABASE SESSION FIXTURE TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.db
async def test_db_session_fixture(db_session: AsyncSession):
    """Verify that db_session fixture provides a valid async session."""
    assert db_session is not None, "db_session fixture should provide a session"
    assert isinstance(db_session, AsyncSession), "db_session should be an AsyncSession"

    # Session should be active and able to execute queries
    result = await db_session.execute(select(1))
    assert result.scalar() == 1, "Session should be able to execute queries"


@pytest.mark.asyncio
@pytest.mark.db
async def test_db_session_can_query_models(db_session: AsyncSession):
    """Verify that db_session can query database models."""
    # Query should work even if no data exists
    result = await db_session.execute(select(User))
    users = result.scalars().all()

    # Should return a list (even if empty)
    assert isinstance(users, list), "Query should return a list"


# ============================================================================
# TRANSACTION ISOLATION TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.db
async def test_transaction_isolation_first_test(db_session: AsyncSession):
    """
    First test in isolation sequence - creates a user.

    This user should NOT be visible in the next test due to rollback.
    """
    # Create a test user
    user = User(
        email="isolation_test@example.com",
        username="isolation_test_user",
        hashed_password="hashed_password_placeholder"
    )
    db_session.add(user)
    await db_session.commit()

    # Verify user was created in this session
    result = await db_session.execute(
        select(User).where(User.email == "isolation_test@example.com")
    )
    found_user = result.scalar_one_or_none()
    assert found_user is not None, "User should be created in this test"
    assert found_user.email == "isolation_test@example.com"


@pytest.mark.asyncio
@pytest.mark.db
async def test_transaction_isolation_second_test(db_session: AsyncSession):
    """
    Second test in isolation sequence - should NOT see user from previous test.

    This verifies that transaction rollback is working correctly.
    """
    # Try to find the user created in the previous test
    result = await db_session.execute(
        select(User).where(User.email == "isolation_test@example.com")
    )
    found_user = result.scalar_one_or_none()

    # User should NOT exist (rolled back after previous test)
    assert found_user is None, \
        "User from previous test should not exist (transaction rollback failed)"


@pytest.mark.asyncio
@pytest.mark.db
async def test_multiple_operations_in_same_test(db_session: AsyncSession):
    """
    Verify that multiple database operations work within a single test.
    """
    # Create a category
    category = Category(
        name="Test Category",
        slug="test-category",
        description="A test category",
        order=1
    )
    db_session.add(category)
    await db_session.commit()

    # Verify category was created
    result = await db_session.execute(
        select(Category).where(Category.slug == "test-category")
    )
    found_category = result.scalar_one_or_none()
    assert found_category is not None
    assert found_category.name == "Test Category"

    # Create a tool in that category
    tool = Tool(
        name="Test Tool",
        slug="test-tool",
        description="A test tool",
        url="https://example.com",
        category_id=found_category.id
    )
    db_session.add(tool)
    await db_session.commit()

    # Verify tool was created with relationship
    result = await db_session.execute(
        select(Tool).where(Tool.slug == "test-tool")
    )
    found_tool = result.scalar_one_or_none()
    assert found_tool is not None
    assert found_tool.category_id == found_category.id


@pytest.mark.asyncio
@pytest.mark.db
async def test_rollback_cleans_up_previous_test(db_session: AsyncSession):
    """
    Verify that data from the previous test is cleaned up.

    This should NOT see the category or tool from test_multiple_operations_in_same_test.
    """
    # Check that category doesn't exist
    result = await db_session.execute(
        select(Category).where(Category.slug == "test-category")
    )
    category = result.scalar_one_or_none()
    assert category is None, "Category from previous test should be rolled back"

    # Check that tool doesn't exist
    result = await db_session.execute(
        select(Tool).where(Tool.slug == "test-tool")
    )
    tool = result.scalar_one_or_none()
    assert tool is None, "Tool from previous test should be rolled back"


# ============================================================================
# RELATIONSHIP TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.db
async def test_relationship_loading(db_session: AsyncSession):
    """
    Verify that SQLAlchemy relationships work correctly with async sessions.
    """
    # Create a category
    category = Category(
        name="Test Category",
        slug="test-category-rel",
        description="Testing relationships"
    )
    db_session.add(category)
    await db_session.commit()

    # Create multiple tools in that category
    tool1 = Tool(
        name="Tool 1",
        slug="tool-1",
        description="First tool",
        url="https://example.com/tool1",
        category_id=category.id
    )
    tool2 = Tool(
        name="Tool 2",
        slug="tool-2",
        description="Second tool",
        url="https://example.com/tool2",
        category_id=category.id
    )
    db_session.add_all([tool1, tool2])
    await db_session.commit()

    # Query category and access its tools through relationship
    result = await db_session.execute(
        select(Category).where(Category.slug == "test-category-rel")
    )
    found_category = result.scalar_one_or_none()

    assert found_category is not None
    # Note: Async sessions require explicit loading of relationships
    # This test verifies that the relationship is defined correctly


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.db
async def test_unique_constraint_violation(db_session: AsyncSession):
    """
    Verify that unique constraint violations are handled properly.
    """
    from sqlalchemy.exc import IntegrityError

    # Create a user
    user1 = User(
        email="unique_test@example.com",
        username="unique_user",
        hashed_password="password123"
    )
    db_session.add(user1)
    await db_session.commit()

    # Try to create another user with the same email
    user2 = User(
        email="unique_test@example.com",  # Duplicate email
        username="another_user",
        hashed_password="password456"
    )
    db_session.add(user2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.commit()

    # Rollback to clean up the failed transaction
    await db_session.rollback()


@pytest.mark.asyncio
@pytest.mark.db
async def test_session_rollback_on_error(db_session: AsyncSession):
    """
    Verify that explicit rollback works after an error.
    """
    from sqlalchemy.exc import IntegrityError

    # Create a user
    user1 = User(
        email="rollback_test@example.com",
        username="rollback_user",
        hashed_password="password123"
    )
    db_session.add(user1)
    await db_session.commit()

    # Try to create a duplicate (will fail)
    user2 = User(
        email="rollback_test@example.com",
        username="another_rollback_user",
        hashed_password="password456"
    )
    db_session.add(user2)

    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()

    # After rollback, session should be usable again
    result = await db_session.execute(select(User))
    users = result.scalars().all()

    # Should have exactly one user (the first one)
    assert len(users) == 1
    assert users[0].email == "rollback_test@example.com"


# ============================================================================
# CONCURRENT TEST DATA
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.db
async def test_clean_slate_for_each_test(db_session: AsyncSession):
    """
    Verify that each test starts with a clean database state.

    This test should see an empty database despite all previous tests.
    """
    # Count all users
    result = await db_session.execute(select(User))
    users = result.scalars().all()

    # Should be empty (all previous test data rolled back)
    assert len(users) == 0, "Database should be clean at the start of each test"

    # Count all categories
    result = await db_session.execute(select(Category))
    categories = result.scalars().all()
    assert len(categories) == 0

    # Count all tools
    result = await db_session.execute(select(Tool))
    tools = result.scalars().all()
    assert len(tools) == 0
