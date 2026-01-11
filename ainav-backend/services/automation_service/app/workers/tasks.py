from ..celery_app import celery_app
from ..clients.producthunt import ProductHuntClient
from ..clients.deepseek import DeepSeekClient
from ..clients.github import GitHubClient
from ..clients.github_trending import GitHubTrendingClient
from ..clients.arxiv_miner import ArXivMiner
from ..utils.duplicate_detector import DuplicateDetector
from ..utils.category_mapper import CategoryMapper
from shared.models import Tool, Category, CrawledContent
from shared.config import settings
from shared.embedding import embedding_service
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
    duplicate_detector = DuplicateDetector(fuzzy_threshold=0.85)

    logger.info("Starting daily PH crawl...")
    ph_tools = await ph_client.get_daily_ai_tools()

    if not ph_tools:
        logger.warning("No tools found on Product Hunt today.")
        return {"status": "no_tools_found"}

    new_tools_count = 0
    skipped_duplicates = 0
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

            tool_url = node["website"] or node["url"]
            tool_name = node["name"]

            # Check for duplicates using DuplicateDetector
            duplicates = await duplicate_detector.find_duplicates(
                session=session,
                name=tool_name,
                url=tool_url,
                check_fuzzy=True
            )

            if duplicates:
                logger.info(
                    f"Skipping duplicate from ProductHunt: {tool_name} - "
                    f"Found {len(duplicates)} match(es): "
                    f"{', '.join([f'{d['name']} ({d['match_type']})' for d in duplicates])}"
                )
                skipped_duplicates += 1
                continue

            logger.info(f"Enriching new tool: {node['name']} (Votes: {node['votesCount']})")
            # Enrich with DeepSeek
            enrichment = await ds_client.enrich_tool_info(node["name"], node["tagline"])

            if enrichment:
                slug = node["name"].lower().replace(" ", "-")  # Simple slugify
                new_tool = Tool(
                    name=node["name"],
                    name_zh=enrichment.get("name_zh"),
                    slug=slug,
                    description=node["tagline"],
                    description_zh=enrichment.get("description_zh"),
                    url=tool_url,
                    category_id=category.id,
                    pricing_type=enrichment.get("pricing_type", "free")
                )
                session.add(new_tool)
                new_tools_count += 1

        await session.commit()

    if new_tools_count > 0:
        logger.info(f"Added {new_tools_count} new tools. Triggering Meilisearch sync...")
        sync_to_meilisearch.delay()

    logger.info(f"ProductHunt crawl complete: {new_tools_count} added, {skipped_duplicates} duplicates skipped")
    return {"status": "success", "added": new_tools_count, "skipped_duplicates": skipped_duplicates}

@celery_app.task(name="crawl_github_trending_daily")
def crawl_github_trending_daily():
    """Discover trending AI repos on GitHub."""
    return asyncio.run(_crawl_github_trending_pipeline())

async def _crawl_github_trending_pipeline():
    gt_client = GitHubTrendingClient()
    ds_client = DeepSeekClient()
    duplicate_detector = DuplicateDetector(fuzzy_threshold=0.85)
    category_mapper = CategoryMapper()

    logger.info("Starting GitHub Trending crawl...")
    repos = await gt_client.get_trending_repos()

    new_content_count = 0
    skipped_duplicates = 0
    skipped_low_confidence = 0

    async with AsyncSessionLocal() as session:
        for repo in repos:
            repo_url = repo["url"]
            repo_name = repo["name"]
            repo_full_name = repo["full_name"]

            # Check for duplicates using DuplicateDetector
            duplicates = await duplicate_detector.find_duplicates(
                session=session,
                name=repo_name,
                url=repo_url,
                check_fuzzy=True
            )

            if duplicates:
                logger.info(
                    f"Skipping duplicate from GitHub: {repo_name} - "
                    f"Found {len(duplicates)} match(es): "
                    f"{', '.join([f'{d['name']} ({d['match_type']})' for d in duplicates])}"
                )
                skipped_duplicates += 1
                continue

            logger.info(f"Enriching new GitHub tool: {repo_full_name}")
            enrichment = await ds_client.enrich_tool_info(repo_name, repo["description"])

            if not enrichment:
                logger.warning(f"Failed to enrich {repo_name}, skipping")
                continue

            # Check if it's actually an AI tool based on LLM confidence
            is_ai_tool = enrichment.get("is_ai_tool", True)
            ai_tool_confidence = enrichment.get("ai_tool_confidence", 0.0)

            # Skip if LLM is confident this is NOT an AI tool (confidence > 0.7 that it's not AI)
            if not is_ai_tool and ai_tool_confidence > 0.7:
                logger.info(
                    f"Skipping {repo_name} - LLM determined it's not an AI tool "
                    f"(confidence: {ai_tool_confidence:.2f})"
                )
                skipped_low_confidence += 1
                continue

            # Map suggested category to database category
            suggested_category = enrichment.get("suggested_category", "productivity")
            category_confidence = enrichment.get("category_confidence", 0.0)

            # Calculate overall AI confidence score (combine crawler's AI score with LLM confidence)
            crawler_ai_score = repo.get("ai_score", 0.0)
            overall_confidence = (crawler_ai_score * 0.4 + ai_tool_confidence * 0.6) if is_ai_tool else crawler_ai_score * 0.5

            logger.info(
                f"Creating CrawledContent for {repo_name}: "
                f"category={suggested_category} (confidence: {category_confidence:.2f}), "
                f"AI confidence: {overall_confidence:.2f}"
            )

            # Prepare metadata JSON with all GitHub-specific information
            metadata = {
                "full_name": repo_full_name,
                "stars_today": repo.get("stars_today", 0),
                "topics": repo.get("topics", []),
                "language": repo.get("language", ""),
                "has_readme": repo.get("has_readme", False),
                "ai_score": crawler_ai_score,
                "is_ai_tool": is_ai_tool,
                "ai_tool_confidence": ai_tool_confidence,
                "category_confidence": category_confidence,
                "enrichment": {
                    "name_zh": enrichment.get("name_zh"),
                    "description_zh": enrichment.get("description_zh"),
                    "tags": enrichment.get("tags", []),
                    "summary": enrichment.get("summary")
                }
            }

            # Create CrawledContent entry for admin review
            crawled_content = CrawledContent(
                source="github",
                name=repo_name,
                description=repo["description"] or f"Trending GitHub repository: {repo_full_name}",
                url=repo_url,
                meta_data=metadata,
                suggested_category=suggested_category,
                suggested_pricing="open_source",  # GitHub repos are open source
                ai_confidence_score=overall_confidence,
                status="pending"
            )
            session.add(crawled_content)
            new_content_count += 1

        await session.commit()

    logger.info(
        f"GitHub crawl complete: {new_content_count} added to review queue, "
        f"{skipped_duplicates} duplicates skipped, "
        f"{skipped_low_confidence} non-AI tools filtered"
    )
    return {
        "status": "success",
        "added": new_content_count,
        "skipped_duplicates": skipped_duplicates,
        "skipped_low_confidence": skipped_low_confidence
    }

@celery_app.task(name="mine_arxiv_papers_daily")
def mine_arxiv_papers_daily():
    """Mine latest AI papers from ArXiv."""
    return asyncio.run(_mine_arxiv_papers_pipeline())

async def _mine_arxiv_papers_pipeline():
    arxiv_miner = ArXivMiner()
    ds_client = DeepSeekClient()
    duplicate_detector = DuplicateDetector(fuzzy_threshold=0.85)

    logger.info("Starting ArXiv paper mining...")
    papers = await arxiv_miner.get_latest_papers()

    new_tools_count = 0
    skipped_duplicates = 0
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
            paper_url = paper["url"]
            paper_name = paper["name"]

            # Check for duplicates using DuplicateDetector
            duplicates = await duplicate_detector.find_duplicates(
                session=session,
                name=paper_name,
                url=paper_url,
                check_fuzzy=True
            )

            if duplicates:
                logger.info(
                    f"Skipping duplicate from ArXiv: {paper_name} - "
                    f"Found {len(duplicates)} match(es): "
                    f"{', '.join([f'{d['name']} ({d['match_type']})' for d in duplicates])}"
                )
                skipped_duplicates += 1
                continue

            logger.info(f"Enriching new paper: {paper['name']}")
            enrichment = await ds_client.enrich_tool_info(paper["name"], paper["description"])

            if enrichment:
                slug = f"arxiv-{paper['url'].split('/')[-1].replace('.', '-')}"
                new_tool = Tool(
                    name=paper["name"],
                    name_zh=enrichment.get("name_zh"),
                    slug=slug,
                    description=paper["description"][:500],  # Summary might be long
                    description_zh=enrichment.get("description_zh"),
                    url=paper_url,
                    category_id=category.id,
                    pricing_type="free"
                )
                session.add(new_tool)
                new_tools_count += 1

        await session.commit()

    if new_tools_count > 0:
        sync_to_meilisearch.delay()

    logger.info(f"ArXiv crawl complete: {new_tools_count} added, {skipped_duplicates} duplicates skipped")
    return {"status": "success", "added": new_tools_count, "skipped_duplicates": skipped_duplicates}

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
            # Update settings for searchable attributes and filters
            # Ensure vector search is enabled or configured if needed (usually implicit with _vectors)
            index.update_filterable_attributes(["category_slug", "scenario_slugs", "pricing_type", "github_stars"])
            index.update_searchable_attributes(["name", "name_zh", "description", "category_name", "scenario_names"])
            
            # Configure embedding settings if we wanted Meilisearch to do it, but we are doing it manually.
            # We just need to enable vector search if it is locked behind a flag, but in recent versions it's open.
            
            # Upsert documents
            index.add_documents(documents)
            logger.info(f"Synced {len(documents)} tools to Meilisearch.")
            return {"status": "success", "synced": len(documents)}
        
        return {"status": "no_tools"}
