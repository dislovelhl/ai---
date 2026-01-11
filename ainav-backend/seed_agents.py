import asyncio
import uuid
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os

# Adjust sys.path to import shared and app modules
import sys
sys.path.append(os.getcwd())

from shared.config import settings
from shared.database import SessionLocal, engine
from shared.models import AgentWorkflow, User, Skill, Tool

async def seed():
    async with SessionLocal() as db:
        # 1. Get a user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("No user found. Create a user first.")
            return

        # 2. Define some example skills if they don't exist
        # (Assuming some tools already exist)
        tools_result = await db.execute(select(Tool).limit(5))
        tools = tools_result.scalars().all()
        
        # 3. Create Example Workflows (Agents)
        agents_data = [
            {
                "name": "Market Researcher",
                "name_zh": "全能市场调研员",
                "slug": "market-researcher",
                "description": "自动抓取行业新闻，分析竞品动向并生成专业报告。",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个专业的市场调研专家。你会利用搜索工具获取最新信息，并写出深刻的分析报告。",
                "is_public": True,
                "is_template": True,
                "star_count": 128,
                "fork_count": 45,
                "run_count": 1200
            },
            {
                "name": "Social Media Manager",
                "name_zh": "社交媒体推手",
                "slug": "social-media-manager",
                "description": "帮你在微博、小红书上生成爆款文案，并寻找配图建议。",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个精通流量密码的社交媒体运营。你擅长写吸引人的标题和内容。",
                "is_public": True,
                "is_template": True,
                "star_count": 256,
                "fork_count": 89,
                "run_count": 3500
            },
            {
                "name": "Code Assistant Pro",
                "name_zh": "编程助手专家版",
                "slug": "code-assistant-pro",
                "description": "深入理解你的代码库，提供重构建议和单元测试生成。",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个资深软件架构师。你的建议总是遵循最佳实践。",
                "is_public": True,
                "is_template": False,
                "star_count": 512,
                "fork_count": 210,
                "run_count": 8900
            },
            {
                "name": "Personal Health Coach",
                "name_zh": "私人健康教练",
                "slug": "health-coach",
                "description": "根据你的身体数据，定制每日饮食和运动计划。",
                "llm_model": "deepseek-chat",
                "system_prompt": "你是一个细心且专业的健康教练。你总是提供科学的建议。",
                "is_public": True,
                "is_template": True,
                "star_count": 85,
                "fork_count": 12,
                "run_count": 600
            }
        ]

        for data in agents_data:
            # Check if slug exists
            existing = await db.execute(select(AgentWorkflow).where(AgentWorkflow.slug == data["slug"]))
            if existing.scalar_one_or_none():
                continue
                
            agent = AgentWorkflow(
                id=uuid.uuid4(),
                user_id=user.id,
                graph_json={"nodes": [], "edges": []}, # Mock graph
                **data
            )
            db.add(agent)
            print(f"Added agent: {data['name']}")
            
        await db.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
