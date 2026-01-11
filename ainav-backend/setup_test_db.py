"""
Script to create the test database.

This script connects to PostgreSQL and creates the ainav_test_db database
if it doesn't already exist.
"""
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from shared.config import settings


async def create_test_database():
    """Create the test database if it doesn't exist."""
    # Connect to the default 'postgres' database to create our test database
    base_url = settings.DATABASE_URL.rsplit("/", 1)[0]
    postgres_url = f"{base_url}/postgres"

    print(f"Connecting to: {postgres_url}")

    engine = create_async_engine(
        postgres_url,
        isolation_level="AUTOCOMMIT",  # Required to create databases
        echo=True
    )

    try:
        async with engine.connect() as conn:
            # Check if test database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'ainav_test_db'")
            )
            exists = result.scalar() is not None

            if exists:
                print("✓ Test database 'ainav_test_db' already exists")
            else:
                # Create test database
                await conn.execute(text("CREATE DATABASE ainav_test_db"))
                print("✓ Created test database 'ainav_test_db'")

        # Now connect to the test database and create tables
        test_db_url = settings.DATABASE_URL.replace("/ainav_db", "/ainav_test_db")
        test_engine = create_async_engine(test_db_url, echo=True)

        print(f"\nConnecting to test database: {test_db_url}")

        # Import Base to get all models
        from shared.models import Base

        async with test_engine.begin() as conn:
            # Enable pgvector extension first
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✓ Enabled pgvector extension")
            except Exception as ext_error:
                print(f"⚠ Warning: Could not enable pgvector extension: {ext_error}")
                print("  Vector-related features may not work in tests")

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✓ Created all tables in test database")

        await test_engine.dispose()

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return False
    finally:
        await engine.dispose()

    return True


if __name__ == "__main__":
    success = asyncio.run(create_test_database())
    sys.exit(0 if success else 1)
