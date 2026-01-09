import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from shared.config import settings

async def test_connection():
    # Use the asyncpg URL
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"Failed to connect: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
