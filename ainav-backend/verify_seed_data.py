import asyncio
import sys
import os

# Add /app to sys.path
sys.path.append("/app")

from shared.models import Tool, Category
from shared.config import settings
from shared.embedding import embedding_service
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from meilisearch import Client as MeiliClient

async def seed_and_sync():
    print("Connecting to DB...")
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 1. Seed Data
    async with AsyncSessionLocal() as session:
        # Create Category
        print("Checking Category...")
        cat_query = select(Category).where(Category.slug == "test-category")
        result = await session.execute(cat_query)
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(name="Test Category", slug="test-category", description="For verification")
            session.add(category)
            await session.commit()
            await session.refresh(category)
            print(f"Created category: {category.id}")
            
        # Create Tool
        print("Checking Tool...")
        tool_query = select(Tool).where(Tool.slug == "deepseek-r1-test")
        result = await session.execute(tool_query)
        tool = result.scalar_one_or_none()
        
        if not tool:
            tool = Tool(
                name="DeepSeek R1 Test",
                name_zh="深度求索 R1 测试版",
                slug="deepseek-r1-test",
                description="An advanced reasoning model excellent at math and logic.",
                description_zh="擅长数学和逻辑的高级推理模型。",
                url="https://deepseek.com",
                category_id=category.id,
                pricing_type="free",
                scenarios=[]
            )
            session.add(tool)
            await session.commit()
            print("Created tool: DeepSeek R1 Test")
        else:
            print("Tool already exists.")
            
    # 2. Sync Logic (Replicating logic from tasks.py to avoid import issues)
    print("Starting Sync Logic...")
    meili_client = MeiliClient(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)
    
    async with AsyncSessionLocal() as session:
        # Fetch all tools
        query = select(Tool).options(
            selectinload(Tool.category),
            selectinload(Tool.scenarios)
        )
        result = await session.execute(query)
        tools = result.scalars().all()
        
        documents = []
        for tool in tools:
            # Generate embedding
            text_to_embed = f"{tool.name} {tool.name_zh or ''} {tool.description} {tool.description_zh or ''}"
            print(f"Generating embedding for: {tool.name}")
            vector = embedding_service.generate_embedding(text_to_embed)

            documents.append({
                "id": str(tool.id),
                "name": tool.name,
                "name_zh": tool.name_zh or tool.name,
                "slug": tool.slug,
                "description": tool.description,
                "description_zh": tool.description_zh or tool.description,
                "url": tool.url,
                "category_name": tool.category.name if tool.category else None,
                "category_slug": tool.category.slug if tool.category else None,
                "scenario_slugs": [s.slug for s in tool.scenarios],
                "scenario_names": [s.name for s in tool.scenarios],
                "avg_rating": tool.avg_rating,
                "pricing_type": tool.pricing_type,
                "github_stars": tool.github_stars,
                "_vectors": {"default": vector},
            })
        
        if documents:
            index = meili_client.index("tools")
            index.update_filterable_attributes(["category_slug", "scenario_slugs", "pricing_type", "github_stars"])
            index.update_searchable_attributes(["name", "name_zh", "description", "category_name", "scenario_names"])
            
            # Remove existing documents to ensure clean state? No, upsert is fine.
            task = index.add_documents(documents)
            print(f"Synced {len(documents)} document(s). Task UID: {task.task_uid}")
            # Wait for task to complete?
            # index.wait_for_task(task.task_uid)
        else:
            print("No documents to sync.")

if __name__ == "__main__":
    asyncio.run(seed_and_sync())
