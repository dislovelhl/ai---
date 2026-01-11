from ..celery_app import celery_app
from ..clients.producthunt import ProductHuntClient
from ..clients.deepseek import DeepSeekClient
from ..clients.github import GitHubClient
from ..clients.github_trending import GitHubTrendingClient
from ..clients.arxiv_miner import ArXivMiner
from shared.models import Tool, Category
from shared.config import settings
from shared.embedding import embedding_service
from shared.chinese_synonyms import get_synonym_pairs
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
import logging

logger = logging.getLogger(__name__)

# Standard SQLAlchemy setup for the task
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
@celery_app.task(name="crawl_and_enrich_daily")
def crawl_and_enrich_daily():
    """Main pipeline: Fetch from PH -> Enrich with DeepSeek -> Save to DB -> Sync to Meili."""
    return asyncio.run(_crawl_and_enrich_pipeline())

async def _crawl_and_enrich_pipeline():
    ph_client = ProductHuntClient()
    ds_client = DeepSeekClient()
    
    logger.info("Starting daily PH crawl...")
    ph_tools = await ph_client.get_daily_ai_tools()
    
    if not ph_tools:
        logger.warning("No tools found on Product Hunt today.")
        return {"status": "no_tools_found"}

    new_tools_count = 0
    async with AsyncSessionLocal() as session:
        # Get a default category or create it
        cat_query = select(Category).where(Category.slug == "ai-tools")
        result = await session.execute(cat_query)
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(name="AI Tools", slug="ai-tools", description="Automatically discovered AI tools")
            session.add(category)
            await session.commit()
            await session.refresh(category)

        for edge in ph_tools:
            node = edge["node"]
            
            # 2026 Strategy: Filter for high quality (votes > 100)
            if node.get("votesCount", 0) < 100:
                logger.info(f"Skipping {node['name']} (Votes: {node['votesCount']})")
                continue
                
            slug = node["name"].lower().replace(" ", "-") # Simple slugify
            
            # Check if exists
            tool_query = select(Tool).where(Tool.slug == slug)
            tool_result = await session.execute(tool_query)
            if tool_result.scalar_one_or_none():
                continue
            
            logger.info(f"Enriching new tool: {node['name']} (Votes: {node['votesCount']})")
            # Enrich with DeepSeek
            enrichment = await ds_client.enrich_tool_info(node["name"], node["tagline"])
            
            if enrichment:
                new_tool = Tool(
                    name=node["name"],
                    name_zh=enrichment.get("name_zh"),
                    slug=slug,
                    description=node["tagline"],
                    description_zh=enrichment.get("description_zh"),
                    url=node["website"] or node["url"],
                    category_id=category.id,
                    pricing_type=enrichment.get("pricing_type", "free")
                )
                session.add(new_tool)
                new_tools_count += 1
        
        await session.commit()
    
    if new_tools_count > 0:
        logger.info(f"Added {new_tools_count} new tools. Triggering Meilisearch sync...")
        sync_to_meilisearch.delay()
    
    return {"status": "success", "added": new_tools_count}

@celery_app.task(name="crawl_github_trending_daily")
def crawl_github_trending_daily():
    """Discover trending AI repos on GitHub."""
    return asyncio.run(_crawl_github_trending_pipeline())

async def _crawl_github_trending_pipeline():
    gt_client = GitHubTrendingClient()
    ds_client = DeepSeekClient()
    
    logger.info("Starting GitHub Trending crawl...")
    repos = await gt_client.get_trending_repos()
    
    new_tools_count = 0
    async with AsyncSessionLocal() as session:
        cat_query = select(Category).where(Category.slug == "open-source")
        result = await session.execute(cat_query)
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(name="Open Source", slug="open-source", description="Open Source AI projects")
            session.add(category)
            await session.commit()
            await session.refresh(category)

        for repo in repos:
            slug = repo["name"].lower().replace(" ", "-")
            tool_query = select(Tool).where(Tool.slug == slug)
            tool_result = await session.execute(tool_query)
            if tool_result.scalar_one_or_none():
                continue

            logger.info(f"Enriching new GitHub tool: {repo['full_name']}")
            enrichment = await ds_client.enrich_tool_info(repo["name"], repo["description"])
            
            if enrichment:
                new_tool = Tool(
                    name=repo["name"],
                    name_zh=enrichment.get("name_zh"),
                    slug=slug,
                    description=repo["description"],
                    description_zh=enrichment.get("description_zh"),
                    url=repo["url"],
                    category_id=category.id,
                    pricing_type="open_source",
                    github_stars=repo.get("stars_today", 0)
                )
                session.add(new_tool)
                new_tools_count += 1
        
        await session.commit()
    
    if new_tools_count > 0:
        sync_to_meilisearch.delay()
    
    return {"status": "success", "added": new_tools_count}

@celery_app.task(name="mine_arxiv_papers_daily")
def mine_arxiv_papers_daily():
    """Mine latest AI papers from ArXiv."""
    return asyncio.run(_mine_arxiv_papers_pipeline())

async def _mine_arxiv_papers_pipeline():
    arxiv_miner = ArXivMiner()
    ds_client = DeepSeekClient()
    
    logger.info("Starting ArXiv paper mining...")
    papers = await arxiv_miner.get_latest_papers()
    
    new_tools_count = 0
    async with AsyncSessionLocal() as session:
        cat_query = select(Category).where(Category.slug == "research")
        result = await session.execute(cat_query)
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(name="Research", slug="research", description="AI Research Papers & Models")
            session.add(category)
            await session.commit()
            await session.refresh(category)

        for paper in papers:
            slug = f"arxiv-{paper['url'].split('/')[-1].replace('.', '-')}"
            tool_query = select(Tool).where(Tool.slug == slug)
            tool_result = await session.execute(tool_query)
            if tool_result.scalar_one_or_none():
                continue

            logger.info(f"Enriching new paper: {paper['name']}")
            enrichment = await ds_client.enrich_tool_info(paper["name"], paper["description"])
            
            if enrichment:
                new_tool = Tool(
                    name=paper["name"],
                    name_zh=enrichment.get("name_zh"),
                    slug=slug,
                    description=paper["description"][:500], # Summary might be long
                    description_zh=enrichment.get("description_zh"),
                    url=paper["url"],
                    category_id=category.id,
                    pricing_type="free"
                )
                session.add(new_tool)
                new_tools_count += 1
        
        await session.commit()
    
    if new_tools_count > 0:
        sync_to_meilisearch.delay()
    
    return {"status": "success", "added": new_tools_count}

@celery_app.task(name="sync_github_stats")
def sync_github_stats():
    """Fetch GitHub stats for tools with repo URLs."""
    return asyncio.run(_sync_github_stats_pipeline())

async def _sync_github_stats_pipeline():
    github_client = GitHubClient()
    
    async with AsyncSessionLocal() as session:
        # Fetch tools that have a github.com link in their URL
        query = select(Tool).where(Tool.url.like("%github.com%"))
        result = await session.execute(query)
        tools = result.scalars().all()
        
        logger.info(f"Found {len(tools)} tools with GitHub URLs. Starting sync...")
        synced_count = 0
        
        for tool in tools:
            stats = await github_client.get_repo_stats(tool.url)
            if stats:
                tool.github_stars = stats.get("stars", 0)
                # We could also update pricing_type to 'open_source' if it's GitHub
                if not tool.pricing_type:
                    tool.pricing_type = "open_source"
                synced_count += 1
        
        await session.commit()
        
    if synced_count > 0:
        logger.info(f"Synced {synced_count} tools. Triggering Meilisearch sync...")
        sync_to_meilisearch.delay()
        
    return {"status": "success", "synced": synced_count}
    
@celery_app.task(name="enrich_single_tool")
def enrich_single_tool(tool_id: str):
    """Enrich a single tool with DeepSeek."""
    return asyncio.run(_enrich_single_tool_pipeline(tool_id))

async def _enrich_single_tool_pipeline(tool_id: str):
    ds_client = DeepSeekClient()
    
    async with AsyncSessionLocal() as session:
        query = select(Tool).where(Tool.id == tool_id)
        result = await session.execute(query)
        tool = result.scalar_one_or_none()
        
        if not tool:
            logger.error(f"Tool with id {tool_id} not found.")
            return {"status": "not_found"}
            
        logger.info(f"Manually enriching tool: {tool.name}")
        enrichment = await ds_client.enrich_tool_info(tool.name, tool.description)
        
        if enrichment:
            tool.name_zh = enrichment.get("name_zh")
            tool.description_zh = enrichment.get("description_zh")
            tool.pricing_type = enrichment.get("pricing_type", tool.pricing_type)
            # Check for GitHub stars if it's a GitHub URL
            if "github.com" in tool.url:
                github_client = GitHubClient()
                stats = await github_client.get_repo_stats(tool.url)
                if stats:
                    tool.github_stars = stats.get("stars", tool.github_stars)
            
            await session.commit()
            sync_to_meilisearch.delay()
            return {"status": "success", "tool": tool.name}
            
        return {"status": "enrichment_failed"}

from meilisearch import Client as MeiliClient

# Meilisearch setup
meili_client = MeiliClient(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)

@celery_app.task(name="sync_to_meilisearch")
def sync_to_meilisearch():
    """Sync all tools from Postgres to Meilisearch."""
    return asyncio.run(_sync_to_meilisearch_pipeline())

async def _sync_to_meilisearch_pipeline():
    from sqlalchemy.orm import selectinload
    
    async with AsyncSessionLocal() as session:
        # Fetch all tools with categories and scenarios
        query = select(Tool).options(
            selectinload(Tool.category),
            selectinload(Tool.scenarios)
        )
        result = await session.execute(query)
        tools = result.scalars().all()
        
        # Initialize embedding service once batch starts (if not executing in worker process that already has it)
        # However, for Celery, it might be better to initialize at module level or inside task?
        # Let's rely on the service lazy loading.
        
        documents = []
        for tool in tools:
            # Generate embedding for vector search
            # Combine important fields for semantic representation
            text_to_embed = f"{tool.name} {tool.name_zh or ''} {tool.description} {tool.description_zh or ''}"
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
                "_vectors": {"default": vector},  # Meilisearch vector field
            })
        
        if documents:
            index = meili_client.index("tools")

            # === Chinese-Optimized Search Configuration ===
            logger.info("Configuring Meilisearch index with Chinese-specific settings...")

            # 1. Set Chinese locale for better tokenization
            index.update_localized_attributes([
                {"locales": ["cmn"], "attributePatterns": ["name_zh", "description_zh"]}
            ])

            # 2. Configure typo tolerance - disable for Chinese characters
            # Chinese characters don't have typos in the same way as alphabetic languages
            # Set minWordSizeForTypos very high to effectively disable for short Chinese queries
            index.update_typo_tolerance({
                "enabled": True,
                "minWordSizeForTypos": {
                    "oneTypo": 255,  # Effectively disable for Chinese
                    "twoTypos": 255  # Effectively disable for Chinese
                },
                "disableOnWords": [],
                "disableOnAttributes": ["name_zh", "description_zh"]
            })

            # 3. Upload Chinese AI terminology synonyms
            synonym_pairs = get_synonym_pairs()
            index.update_synonyms(synonym_pairs)
            logger.info(f"Uploaded {len(synonym_pairs)} synonym groups for bilingual search")

            # 4. Configure searchable attributes with Chinese prioritization
            # Order matters: earlier fields get higher ranking weight
            index.update_searchable_attributes([
                "name_zh",           # Prioritize Chinese name (most important for Chinese users)
                "name",              # English name
                "description_zh",    # Chinese description
                "description",       # English description
                "category_name",     # Category names
                "scenario_names"     # Scenario names
            ])

            # 5. Add Chinese punctuation to separator tokens
            # This helps with proper tokenization of Chinese text
            index.update_separator_tokens([
                "、",  # Chinese enumeration comma
                "。",  # Chinese period
                "，",  # Chinese comma
                "：",  # Chinese colon
                "；",  # Chinese semicolon
                "！",  # Chinese exclamation
                "？",  # Chinese question mark
                "（",  # Chinese left parenthesis
                "）",  # Chinese right parenthesis
                "【",  # Chinese left bracket
                "】",  # Chinese right bracket
            ])

            # 6. Configure filterable attributes
            index.update_filterable_attributes([
                "category_slug",
                "scenario_slugs",
                "pricing_type",
                "github_stars"
            ])

            # 7. Configure ranking rules (default + custom)
            # Prioritize exact matches and semantic relevance
            index.update_ranking_rules([
                "words",        # Number of matched query terms
                "typo",         # Fewer typos = higher rank
                "proximity",    # Proximity of matched terms
                "attribute",    # Position in searchable attributes list
                "sort",         # Custom sort (stars, ratings)
                "exactness"     # Exact matches ranked higher
            ])

            logger.info("Chinese-optimized index configuration completed")

            # Upsert documents
            index.add_documents(documents)
            logger.info(f"Synced {len(documents)} tools to Meilisearch with Chinese optimization.")
            return {"status": "success", "synced": len(documents)}
        
        return {"status": "no_tools"}
