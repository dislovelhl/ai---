from typing import Generator
from shared.database import SessionLocal

async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session
