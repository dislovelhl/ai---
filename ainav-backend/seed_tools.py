#!/usr/bin/env python3
"""
Seed script for AI tools database.

Run with: python seed_tools.py

This script populates the database with real AI tools for the AI Navigation platform.
"""

import asyncio
import sys
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from shared.config import settings
from shared.models import Base, Tool, Category, Scenario, tool_scenarios

# =============================================================================
# SEED DATA
# =============================================================================

CATEGORIES = [
    {
        "name": "AI Chatbots",
        "slug": "ai-chatbots",
        "name_zh": "AI 聊天机器人",
        "description": "Conversational AI assistants and chatbots",
        "icon": "MessageSquare",
        "order": 1,
    },
    {
        "name": "Image Generation",
        "slug": "image-generation",
        "name_zh": "AI 图像生成",
        "description": "AI-powered image creation and editing tools",
        "icon": "Image",
        "order": 2,
    },
    {
        "name": "Code Assistants",
        "slug": "code-assistants",
        "name_zh": "AI 编程助手",
        "description": "AI tools for code completion, review, and generation",
        "icon": "Code",
        "order": 3,
    },
    {
        "name": "Writing & Content",
        "slug": "writing-content",
        "name_zh": "AI 写作",
        "description": "AI writing assistants and content generators",
        "icon": "FileText",
        "order": 4,
    },
    {
        "name": "Video Generation",
        "slug": "video-generation",
        "name_zh": "AI 视频生成",
        "description": "AI-powered video creation and editing",
        "icon": "Video",
        "order": 5,
    },
    {
        "name": "Audio & Music",
        "slug": "audio-music",
        "name_zh": "AI 音频与音乐",
        "description": "AI tools for audio, music, and voice",
        "icon": "Music",
        "order": 6,
    },
    {
        "name": "Productivity",
        "slug": "productivity",
        "name_zh": "AI 效率工具",
        "description": "AI-powered productivity and workflow tools",
        "icon": "Zap",
        "order": 7,
    },
    {
        "name": "Research & Analysis",
        "slug": "research-analysis",
        "name_zh": "AI 研究与分析",
        "description": "AI tools for research, data analysis, and insights",
        "icon": "Search",
        "order": 8,
    },
]

SCENARIOS = [
    {"name": "Content Creation", "slug": "content-creation", "icon": "Pencil"},
    {"name": "Marketing", "slug": "marketing", "icon": "Megaphone"},
    {"name": "Development", "slug": "development", "icon": "Code"},
    {"name": "Education", "slug": "education", "icon": "GraduationCap"},
    {"name": "Business", "slug": "business", "icon": "Briefcase"},
    {"name": "Personal Use", "slug": "personal-use", "icon": "User"},
    {"name": "Design", "slug": "design", "icon": "Palette"},
    {"name": "Research", "slug": "research", "icon": "BookOpen"},
]

# Tools organized by category slug
TOOLS_BY_CATEGORY = {
    "ai-chatbots": [
        {
            "name": "ChatGPT",
            "name_zh": "ChatGPT",
            "slug": "chatgpt",
            "description": "OpenAI's powerful conversational AI assistant. Capable of answering questions, writing content, coding, and much more.",
            "description_zh": "OpenAI 出品的强大对话式 AI 助手。能够回答问题、写作、编程等多种任务。",
            "url": "https://chat.openai.com",
            "logo_url": "https://chat.openai.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["content-creation", "development", "education", "business"],
        },
        {
            "name": "Claude",
            "name_zh": "Claude",
            "slug": "claude",
            "description": "Anthropic's AI assistant focused on being helpful, harmless, and honest. Excellent for analysis, writing, and coding.",
            "description_zh": "Anthropic 出品的 AI 助手，专注于有用、无害和诚实。擅长分析、写作和编程。",
            "url": "https://claude.ai",
            "logo_url": "https://claude.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["content-creation", "development", "research", "business"],
        },
        {
            "name": "Kimi",
            "name_zh": "Kimi",
            "slug": "kimi",
            "description": "Moonshot AI's intelligent assistant with strong Chinese language support and long context window.",
            "description_zh": "月之暗面推出的智能助手，支持超长文本处理，中文能力强大。",
            "url": "https://kimi.moonshot.cn",
            "logo_url": "https://kimi.moonshot.cn/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "research", "education", "business"],
        },
        {
            "name": "DeepSeek",
            "name_zh": "DeepSeek",
            "slug": "deepseek",
            "description": "DeepSeek's AI chat assistant with strong reasoning and coding capabilities.",
            "description_zh": "深度求索推出的 AI 对话助手，推理和编程能力强大。",
            "url": "https://chat.deepseek.com",
            "logo_url": "https://chat.deepseek.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["development", "research", "education"],
        },
        {
            "name": "Doubao",
            "name_zh": "豆包",
            "slug": "doubao",
            "description": "ByteDance's AI assistant with rich multimedia capabilities.",
            "description_zh": "字节跳动推出的 AI 对话助手，支持多媒体交互。",
            "url": "https://www.doubao.com",
            "logo_url": "https://www.doubao.com/favicon.ico",
            "pricing_type": "free",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "personal-use", "education"],
        },
    ],
    "image-generation": [
        {
            "name": "Midjourney",
            "name_zh": "Midjourney",
            "slug": "midjourney",
            "description": "AI art generator that creates stunning images from text descriptions via Discord.",
            "description_zh": "通过 Discord 使用的 AI 艺术生成器，可从文字描述创建精美图像。",
            "url": "https://midjourney.com",
            "logo_url": "https://midjourney.com/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["design", "content-creation", "marketing"],
        },
        {
            "name": "DALL-E 3",
            "name_zh": "DALL-E 3",
            "slug": "dall-e-3",
            "description": "OpenAI's latest image generation model integrated into ChatGPT.",
            "description_zh": "OpenAI 最新的图像生成模型，已集成到 ChatGPT 中。",
            "url": "https://openai.com/dall-e-3",
            "logo_url": "https://openai.com/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["design", "content-creation", "marketing"],
        },
        {
            "name": "Stable Diffusion",
            "name_zh": "Stable Diffusion",
            "slug": "stable-diffusion",
            "description": "Open-source image generation model that can run locally or via API.",
            "description_zh": "开源图像生成模型，可本地运行或通过 API 使用。",
            "url": "https://stability.ai",
            "logo_url": "https://stability.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 120000,
            "scenarios": ["design", "content-creation", "development"],
        },
        {
            "name": "Jimeng",
            "name_zh": "即梦",
            "slug": "jimeng",
            "description": "ByteDance's AI image and video generation platform.",
            "description_zh": "字节跳动推出的 AI 图像和视频生成平台。",
            "url": "https://jimeng.jianying.com",
            "logo_url": "https://jimeng.jianying.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["design", "content-creation", "marketing"],
        },
    ],
    "code-assistants": [
        {
            "name": "GitHub Copilot",
            "name_zh": "GitHub Copilot",
            "slug": "github-copilot",
            "description": "AI pair programmer that suggests code and entire functions in real-time.",
            "description_zh": "AI 编程搭档，实时建议代码和完整函数。",
            "url": "https://github.com/features/copilot",
            "logo_url": "https://github.com/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["development"],
        },
        {
            "name": "Cursor",
            "name_zh": "Cursor",
            "slug": "cursor",
            "description": "AI-powered code editor built for pair programming with AI.",
            "description_zh": "专为 AI 协作编程打造的代码编辑器。",
            "url": "https://cursor.sh",
            "logo_url": "https://cursor.sh/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["development"],
        },
        {
            "name": "Claude Code",
            "name_zh": "Claude Code",
            "slug": "claude-code",
            "description": "Anthropic's agentic coding assistant that runs in your terminal.",
            "description_zh": "Anthropic 推出的终端 AI 编程助手，支持自主完成复杂任务。",
            "url": "https://www.anthropic.com/claude-code",
            "logo_url": "https://claude.ai/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 30000,
            "scenarios": ["development"],
        },
        {
            "name": "Codeium",
            "name_zh": "Codeium",
            "slug": "codeium",
            "description": "Free AI code completion and assistance for 70+ languages.",
            "description_zh": "免费的 AI 代码补全工具，支持 70+ 编程语言。",
            "url": "https://codeium.com",
            "logo_url": "https://codeium.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["development"],
        },
    ],
    "writing-content": [
        {
            "name": "Jasper",
            "name_zh": "Jasper",
            "slug": "jasper",
            "description": "AI content platform for marketing teams to create on-brand content.",
            "description_zh": "为营销团队打造的 AI 内容平台，创建品牌一致的内容。",
            "url": "https://jasper.ai",
            "logo_url": "https://jasper.ai/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["marketing", "content-creation", "business"],
        },
        {
            "name": "Copy.ai",
            "name_zh": "Copy.ai",
            "slug": "copy-ai",
            "description": "AI copywriting assistant for marketing content, emails, and social media.",
            "description_zh": "AI 文案助手，用于营销内容、邮件和社交媒体。",
            "url": "https://copy.ai",
            "logo_url": "https://copy.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["marketing", "content-creation"],
        },
        {
            "name": "Notion AI",
            "name_zh": "Notion AI",
            "slug": "notion-ai",
            "description": "AI writing assistant built into Notion workspace.",
            "description_zh": "内置于 Notion 工作空间的 AI 写作助手。",
            "url": "https://notion.so/product/ai",
            "logo_url": "https://notion.so/favicon.ico",
            "pricing_type": "paid",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "business", "productivity"],
        },
    ],
    "video-generation": [
        {
            "name": "Runway",
            "name_zh": "Runway",
            "slug": "runway",
            "description": "AI video generation and editing platform with Gen-3 Alpha.",
            "description_zh": "AI 视频生成和编辑平台，支持 Gen-3 Alpha 模型。",
            "url": "https://runwayml.com",
            "logo_url": "https://runwayml.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["content-creation", "marketing", "design"],
        },
        {
            "name": "Pika",
            "name_zh": "Pika",
            "slug": "pika",
            "description": "AI video generation tool that creates and edits videos from text.",
            "description_zh": "AI 视频生成工具，可从文字创建和编辑视频。",
            "url": "https://pika.art",
            "logo_url": "https://pika.art/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["content-creation", "marketing"],
        },
        {
            "name": "Kling",
            "name_zh": "可灵",
            "slug": "kling",
            "description": "Kuaishou's AI video generation platform.",
            "description_zh": "快手推出的 AI 视频生成平台。",
            "url": "https://klingai.com",
            "logo_url": "https://klingai.com/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "marketing"],
        },
    ],
    "audio-music": [
        {
            "name": "Suno",
            "name_zh": "Suno",
            "slug": "suno",
            "description": "AI music generation platform that creates songs from text prompts.",
            "description_zh": "AI 音乐生成平台，可从文字提示创作歌曲。",
            "url": "https://suno.ai",
            "logo_url": "https://suno.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "personal-use"],
        },
        {
            "name": "ElevenLabs",
            "name_zh": "ElevenLabs",
            "slug": "elevenlabs",
            "description": "AI voice synthesis and cloning platform with lifelike voices.",
            "description_zh": "AI 语音合成和克隆平台，生成逼真的语音。",
            "url": "https://elevenlabs.io",
            "logo_url": "https://elevenlabs.io/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["content-creation", "development", "marketing"],
        },
    ],
    "productivity": [
        {
            "name": "Perplexity",
            "name_zh": "Perplexity",
            "slug": "perplexity",
            "description": "AI-powered search engine that answers questions with sources.",
            "description_zh": "AI 驱动的搜索引擎，提供带来源的答案。",
            "url": "https://perplexity.ai",
            "logo_url": "https://perplexity.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["research", "education", "business"],
        },
        {
            "name": "Otter.ai",
            "name_zh": "Otter.ai",
            "slug": "otter-ai",
            "description": "AI meeting assistant for transcription and notes.",
            "description_zh": "AI 会议助手，用于转录和笔记。",
            "url": "https://otter.ai",
            "logo_url": "https://otter.ai/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": False,
            "requires_vpn": True,
            "github_stars": 0,
            "scenarios": ["business", "education"],
        },
        {
            "name": "Gamma",
            "name_zh": "Gamma",
            "slug": "gamma",
            "description": "AI presentation and document creation tool.",
            "description_zh": "AI 演示文稿和文档创建工具。",
            "url": "https://gamma.app",
            "logo_url": "https://gamma.app/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["business", "education", "marketing"],
        },
    ],
    "research-analysis": [
        {
            "name": "Consensus",
            "name_zh": "Consensus",
            "slug": "consensus",
            "description": "AI-powered academic search engine for research papers.",
            "description_zh": "AI 驱动的学术搜索引擎，用于研究论文。",
            "url": "https://consensus.app",
            "logo_url": "https://consensus.app/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["research", "education"],
        },
        {
            "name": "Elicit",
            "name_zh": "Elicit",
            "slug": "elicit",
            "description": "AI research assistant that helps analyze papers and find evidence.",
            "description_zh": "AI 研究助手，帮助分析论文和寻找证据。",
            "url": "https://elicit.org",
            "logo_url": "https://elicit.org/favicon.ico",
            "pricing_type": "freemium",
            "is_china_accessible": True,
            "requires_vpn": False,
            "github_stars": 0,
            "scenarios": ["research", "education"],
        },
    ],
}


# =============================================================================
# SEEDING FUNCTIONS
# =============================================================================

async def seed_categories(session: AsyncSession) -> dict:
    """Seed categories and return mapping of slug -> id."""
    print("Seeding categories...")
    category_map = {}

    for cat_data in CATEGORIES:
        # Check if exists
        result = await session.execute(
            select(Category).where(Category.slug == cat_data["slug"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            category_map[cat_data["slug"]] = existing.id
            print(f"  Category '{cat_data['name']}' already exists")
        else:
            cat = Category(
                id=uuid4(),
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                order=cat_data["order"],
            )
            session.add(cat)
            category_map[cat_data["slug"]] = cat.id
            print(f"  Created category: {cat_data['name']}")

    await session.commit()
    return category_map


async def seed_scenarios(session: AsyncSession) -> dict:
    """Seed scenarios and return mapping of slug -> id."""
    print("Seeding scenarios...")
    scenario_map = {}

    for scen_data in SCENARIOS:
        result = await session.execute(
            select(Scenario).where(Scenario.slug == scen_data["slug"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            scenario_map[scen_data["slug"]] = existing.id
            print(f"  Scenario '{scen_data['name']}' already exists")
        else:
            scen = Scenario(
                id=uuid4(),
                name=scen_data["name"],
                slug=scen_data["slug"],
                icon=scen_data["icon"],
            )
            session.add(scen)
            scenario_map[scen_data["slug"]] = scen.id
            print(f"  Created scenario: {scen_data['name']}")

    await session.commit()
    return scenario_map


async def seed_tools(
    session: AsyncSession,
    category_map: dict,
    scenario_map: dict
) -> None:
    """Seed tools with category and scenario relationships."""
    print("Seeding tools...")

    for category_slug, tools in TOOLS_BY_CATEGORY.items():
        category_id = category_map.get(category_slug)
        if not category_id:
            print(f"  Warning: Category '{category_slug}' not found, skipping tools")
            continue

        for tool_data in tools:
            # Check if exists
            result = await session.execute(
                select(Tool).where(Tool.slug == tool_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Tool '{tool_data['name']}' already exists")
                continue

            # Create tool
            tool = Tool(
                id=uuid4(),
                name=tool_data["name"],
                name_zh=tool_data.get("name_zh"),
                slug=tool_data["slug"],
                description=tool_data["description"],
                description_zh=tool_data.get("description_zh"),
                url=tool_data["url"],
                logo_url=tool_data.get("logo_url"),
                pricing_type=tool_data["pricing_type"],
                is_china_accessible=tool_data.get("is_china_accessible", True),
                requires_vpn=tool_data.get("requires_vpn", False),
                github_stars=tool_data.get("github_stars", 0),
                category_id=category_id,
            )
            session.add(tool)
            await session.flush()  # Get the tool ID

            # Add scenario relationships
            scenario_slugs = tool_data.get("scenarios", [])
            for scen_slug in scenario_slugs:
                scen_id = scenario_map.get(scen_slug)
                if scen_id:
                    await session.execute(
                        tool_scenarios.insert().values(
                            tool_id=tool.id,
                            scenario_id=scen_id
                        )
                    )

            print(f"  Created tool: {tool_data['name']}")

    await session.commit()


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("AI Tools Database Seeder")
    print("=" * 60)

    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Test connection
            await session.execute(text("SELECT 1"))
            print("Database connection successful!")
            print()

            # Seed data
            category_map = await seed_categories(session)
            scenario_map = await seed_scenarios(session)
            await seed_tools(session, category_map, scenario_map)

            print()
            print("=" * 60)
            print("Seeding complete!")

            # Print summary
            result = await session.execute(select(Category))
            categories = result.scalars().all()

            result = await session.execute(select(Tool))
            tools = result.scalars().all()

            result = await session.execute(select(Scenario))
            scenarios = result.scalars().all()

            print(f"  Categories: {len(categories)}")
            print(f"  Scenarios: {len(scenarios)}")
            print(f"  Tools: {len(tools)}")
            print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
