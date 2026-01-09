import asyncio
import sys
import os
from sqlalchemy.future import select

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.database import SessionLocal
from shared.models import Tool, Category

async def insert_test_tool():
    async with SessionLocal() as session:
        # Check if category exists
        res = await session.execute(select(Category).where(Category.slug == "dev-tools"))
        category = res.scalar_one_or_none()
        
        if not category:
            category = Category(name="Dev Tools", slug="dev-tools")
            session.add(category)
            await session.commit()
            await session.refresh(category)
            
        # Check if tool exists
        res = await session.execute(select(Tool).where(Tool.slug == "fastapi"))
        tool = res.scalar_one_or_none()
        
        if not tool:
            tool = Tool(
                name="FastAPI",
                slug="fastapi",
                url="https://github.com/fastapi/fastapi",
                description="FastAPI framework, high performance, easy to learn, fast to code, ready for production",
                category_id=category.id,
                pricing_type="open_source"
            )
            session.add(tool)
            await session.commit()
            print("Test tool inserted.")
        else:
            print("Test tool already exists.")

if __name__ == "__main__":
    asyncio.run(insert_test_tool())
