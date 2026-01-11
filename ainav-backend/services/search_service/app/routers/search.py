from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from shared.config import settings
from shared.models import SearchHistory
from shared.pinyin_utils import to_pinyin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime
import logging

# Import local dependencies
from ..auth import require_authentication, get_current_user_id
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
client = Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class FacetCounts(BaseModel):
    """Aggregated counts for faceted search results."""
    pricing_type: dict[str, int] = {}
    is_china_accessible: dict[str, int] = {}
    has_api: dict[str, int] = {}
    category_slug: dict[str, int] = {}


class FacetedSearchResponse(BaseModel):
    """Response model for faceted search endpoint."""
    hits: List[dict]
    query: str
    processing_time_ms: int
    estimated_total_hits: int
    facets: FacetCounts
    page: int
    page_size: int


class AutocompleteItem(BaseModel):
    """Single autocomplete suggestion item."""
    name: str
    slug: str


class AutocompleteResponse(BaseModel):
    """Response model for autocomplete endpoint."""
    suggestions: List[AutocompleteItem]
    query: str
    processing_time_ms: int


class WorkflowSearchResponse(BaseModel):
    """Response model for workflow search endpoint."""
    hits: List[dict]
    query: str
    processing_time_ms: int
    estimated_total_hits: int
    page: int
    page_size: int


class RecentSearchItem(BaseModel):
    """Single recent search item."""
    query: str = Field(..., description="The search query text")
    query_pinyin: Optional[str] = Field(None, description="Pinyin representation of Chinese query")
    result_count: int = Field(..., description="Number of results returned for this search")
    searched_at: datetime = Field(..., description="When the search was performed")

    class Config:
        from_attributes = True


class RecentSearchesResponse(BaseModel):
    """Response model for recent searches endpoint."""
    searches: List[RecentSearchItem] = Field(..., description="List of recent unique searches")
    total: int = Field(..., description="Total number of recent searches returned")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_index_exists(index_name: str) -> bool:
    """Check if a Meilisearch index exists, log warning if not."""
    try:
        client.get_index(index_name)
        return True
    except MeilisearchApiError as e:
        if "index_not_found" in str(e).lower():
            logger.warning(f"Index '{index_name}' does not exist in Meilisearch")
            return False
        raise


def build_filter_string(filters: List[str]) -> Optional[str]:
    """Build a Meilisearch filter string from a list of filter conditions."""
    if not filters:
        return None
    return " AND ".join(filters)


async def record_search_history(
    db: AsyncSession,
    user_id: Optional[UUID],
    query: str,
    result_count: int
) -> None:
    """
    Record a search query to the SearchHistory table for authenticated users.

    Args:
        db: Database session
        user_id: User ID (None for anonymous users)
        query: The search query text
        result_count: Number of results returned

    Note:
        Only records history for authenticated users (user_id is not None).
        Generates pinyin for Chinese queries to improve searchability.
    """
    # Only record for authenticated users
    if user_id is None:
        return

    # Skip empty queries
    if not query or not query.strip():
        return

    try:
        # Generate pinyin for Chinese queries
        query_pinyin = None
        try:
            pinyin_result = to_pinyin(query.strip())
            # Only store if different from original (i.e., contained Chinese)
            if pinyin_result and pinyin_result != query.strip():
                query_pinyin = pinyin_result
        except Exception as e:
            logger.warning(f"Failed to generate pinyin for query '{query}': {e}")

        # Create search history record
        search_record = SearchHistory(
            user_id=user_id,
            query=query.strip(),
            query_pinyin=query_pinyin,
            result_count=result_count
        )

        db.add(search_record)
        await db.commit()

        logger.debug(f"Recorded search history for user {user_id}: query='{query}', results={result_count}")

    except Exception as e:
        logger.error(f"Failed to record search history: {e}", exc_info=True)
        # Don't fail the request if history recording fails
        await db.rollback()


# =============================================================================
# EXISTING ENDPOINT: Basic Search
# =============================================================================

@router.get("")
async def search_tools(
    q: str = Query("", description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    scenario: Optional[str] = Query(None, description="Filter by scenario slug"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_current_user_id)
):
    """
    Search AI tools using Meilisearch.
    Supports filtering and pagination.

    Authentication is optional. If authenticated, search queries will be recorded
    to search history for personalization and analytics.
    """
    index = client.index("tools")

    # Build filters
    filter_list = []
    if category:
        filter_list.append(f"category_slug = {category}")
    if scenario:
        # Note: scenario is an array in Meilisearch
        filter_list.append(f"scenario_slugs = {scenario}")

    filter_str = " AND ".join(filter_list) if filter_list else None

    try:
        search_params = {
            "filter": filter_str,
            "offset": (page - 1) * page_size,
            "limit": page_size,
            "attributesToHighlight": ["*"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
        }

        # Hybrid Search Implementation
        # Only meaningful if query is not empty
        if q and q.strip():
            try:
                # Generate embedding for the query
                from shared.embedding import embedding_service
                vector = embedding_service.generate_embedding(q)

                # Add vector to search params
                # Semantic ratio 0.5 means balanced between keyword (exact match) and vector (semantic)
                search_params["vector"] = vector
                search_params["hybrid"] = {"semanticRatio": 0.5, "embedder": "default"}
                # Note: 'embedder' param is for Meilisearch-managed embeddings.
                # Since we provide 'vector' manually, we might not need 'embedder', or stick to 'userProvided' if updated.
                # In standard raw usage, passing 'vector' is enough for recent versions.
                # Let's just pass 'vector' and 'hybrid' config.
                del search_params["hybrid"]["embedder"]

                logger.info(f"Performing hybrid search for query: {q}")
            except Exception as e:
                logger.error(f"Failed to generate vector for query '{q}': {e}")
                # Fallback to keyword search if embedding fails

        results = index.search(q, search_params)

        # Record search history for authenticated users
        result_count = results.get("estimatedTotalHits", 0)
        await record_search_history(db, user_id, q, result_count)

        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search engine error")


# =============================================================================
# NEW ENDPOINT 1: Faceted Search
# =============================================================================

@router.get("/faceted", response_model=FacetedSearchResponse)
async def faceted_search(
    q: str = Query("", description="Search query"),
    pricing_type: Optional[str] = Query(
        None,
        description="Filter by pricing type (free, freemium, paid)"
    ),
    is_china_accessible: Optional[bool] = Query(
        None,
        description="Filter by China accessibility"
    ),
    has_api: Optional[bool] = Query(
        None,
        description="Filter by API availability"
    ),
    category: Optional[str] = Query(
        None,
        description="Filter by category slug"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_current_user_id)
):
    """
    Faceted search for AI tools with aggregated filter counts.

    Returns search results along with facet distributions for:
    - pricing_type: Count of tools by pricing model
    - is_china_accessible: Count of tools by China accessibility
    - has_api: Count of tools by API availability
    - category_slug: Count of tools by category

    Use facets to build dynamic filter UIs.

    Authentication is optional. If authenticated, search queries will be recorded
    to search history for personalization and analytics.
    """
    if not ensure_index_exists("tools"):
        raise HTTPException(
            status_code=503,
            detail="Search index not available. Please try again later."
        )

    index = client.index("tools")

    # Build filter conditions
    filter_conditions = []

    if pricing_type:
        filter_conditions.append(f'pricing_type = "{pricing_type}"')

    if is_china_accessible is not None:
        filter_conditions.append(f"is_china_accessible = {str(is_china_accessible).lower()}")

    if has_api is not None:
        filter_conditions.append(f"has_api = {str(has_api).lower()}")

    if category:
        filter_conditions.append(f'category_slug = "{category}"')

    filter_str = build_filter_string(filter_conditions)

    try:
        search_params = {
            "filter": filter_str,
            "offset": (page - 1) * page_size,
            "limit": page_size,
            "facets": ["pricing_type", "is_china_accessible", "has_api", "category_slug"],
            "attributesToHighlight": ["name", "name_zh", "description", "description_zh"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
        }

        # Add hybrid search if query provided
        if q and q.strip():
            try:
                from shared.embedding import embedding_service
                vector = embedding_service.generate_embedding(q)
                search_params["vector"] = vector
                search_params["hybrid"] = {"semanticRatio": 0.5}
                logger.info(f"Faceted search with hybrid for query: {q}")
            except Exception as e:
                logger.warning(f"Embedding generation failed, falling back to keyword search: {e}")

        results = index.search(q, search_params)

        # Parse facet distribution from results
        facet_distribution = results.get("facetDistribution", {})

        # Convert boolean facets from string keys to readable format
        china_accessible_raw = facet_distribution.get("is_china_accessible", {})
        has_api_raw = facet_distribution.get("has_api", {})

        facets = FacetCounts(
            pricing_type=facet_distribution.get("pricing_type", {}),
            is_china_accessible={
                "accessible": china_accessible_raw.get("true", 0),
                "not_accessible": china_accessible_raw.get("false", 0)
            },
            has_api={
                "with_api": has_api_raw.get("true", 0),
                "without_api": has_api_raw.get("false", 0)
            },
            category_slug=facet_distribution.get("category_slug", {})
        )

        # Record search history for authenticated users
        result_count = results.get("estimatedTotalHits", 0)
        await record_search_history(db, user_id, q, result_count)

        return FacetedSearchResponse(
            hits=results.get("hits", []),
            query=q,
            processing_time_ms=results.get("processingTimeMs", 0),
            estimated_total_hits=results.get("estimatedTotalHits", 0),
            facets=facets,
            page=page,
            page_size=page_size
        )

    except MeilisearchApiError as e:
        logger.error(f"Meilisearch API error in faceted search: {e}")
        raise HTTPException(status_code=502, detail="Search engine error")
    except Exception as e:
        logger.error(f"Unexpected error in faceted search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# NEW ENDPOINT 2: Autocomplete
# =============================================================================

@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=1, description="Search prefix (at least 1 character)"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_current_user_id)
):
    """
    Fast prefix-based autocomplete suggestions.

    Returns lightweight results with only name and slug fields.
    Optimized for real-time typeahead functionality.

    Authentication is optional. If authenticated, search queries will be recorded
    to search history for personalization and analytics.

    Example usage:
    - User types "chat" -> returns ["ChatGPT", "ChatSonic", "Character.AI", ...]
    """
    if not ensure_index_exists("tools"):
        raise HTTPException(
            status_code=503,
            detail="Search index not available. Please try again later."
        )

    index = client.index("tools")

    try:
        # Optimized search params for autocomplete
        # - Only retrieve necessary fields for performance
        # - No highlighting needed for autocomplete
        # - Small limit for fast response
        search_params = {
            "limit": limit,
            "attributesToRetrieve": ["name", "name_zh", "slug"],
            "attributesToSearchOn": ["name", "name_zh"],  # Focus search on name fields
        }

        results = index.search(q, search_params)

        # Build suggestions list with bilingual support
        suggestions = []
        for hit in results.get("hits", []):
            # Prefer Chinese name if available, fallback to English
            name = hit.get("name_zh") or hit.get("name", "")
            slug = hit.get("slug", "")

            if name and slug:
                suggestions.append(AutocompleteItem(name=name, slug=slug))

        logger.debug(f"Autocomplete for '{q}': {len(suggestions)} suggestions")

        # Record search history for authenticated users
        result_count = len(suggestions)
        await record_search_history(db, user_id, q, result_count)

        return AutocompleteResponse(
            suggestions=suggestions,
            query=q,
            processing_time_ms=results.get("processingTimeMs", 0)
        )

    except MeilisearchApiError as e:
        logger.error(f"Meilisearch API error in autocomplete: {e}")
        raise HTTPException(status_code=502, detail="Search engine error")
    except Exception as e:
        logger.error(f"Unexpected error in autocomplete: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# NEW ENDPOINT 3: Search Workflows
# =============================================================================

@router.get("/workflows", response_model=WorkflowSearchResponse)
async def search_workflows(
    q: str = Query("", description="Search query for workflow name/description"),
    public_only: bool = Query(
        True,
        description="Only return public workflows (default: True)"
    ),
    is_template: Optional[bool] = Query(
        None,
        description="Filter by template status"
    ),
    trigger_type: Optional[str] = Query(
        None,
        description="Filter by trigger type (manual, schedule, webhook)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page")
):
    """
    Search agent workflows by name and description.

    Supports filtering by:
    - public_only: Only show publicly shared workflows
    - is_template: Filter by template status
    - trigger_type: Filter by how the workflow is triggered

    Returns workflow metadata suitable for browse/discovery UI.
    """
    # Check if workflows index exists
    if not ensure_index_exists("workflows"):
        # Return empty results if index doesn't exist yet
        # This is graceful degradation for new deployments
        logger.warning("Workflows index not found, returning empty results")
        return WorkflowSearchResponse(
            hits=[],
            query=q,
            processing_time_ms=0,
            estimated_total_hits=0,
            page=page,
            page_size=page_size
        )

    index = client.index("workflows")

    # Build filter conditions
    filter_conditions = []

    if public_only:
        filter_conditions.append("is_public = true")

    if is_template is not None:
        filter_conditions.append(f"is_template = {str(is_template).lower()}")

    if trigger_type:
        filter_conditions.append(f'trigger_type = "{trigger_type}"')

    filter_str = build_filter_string(filter_conditions)

    try:
        search_params = {
            "filter": filter_str,
            "offset": (page - 1) * page_size,
            "limit": page_size,
            "attributesToRetrieve": [
                "id", "name", "name_zh", "slug", "description", "description_zh",
                "icon", "trigger_type", "is_public", "is_template",
                "fork_count", "run_count", "star_count", "user_id",
                "created_at", "updated_at"
            ],
            "attributesToHighlight": ["name", "name_zh", "description", "description_zh"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
            "sort": ["star_count:desc", "run_count:desc"],  # Popular first
        }

        # Add hybrid search if query provided
        if q and q.strip():
            try:
                from shared.embedding import embedding_service
                vector = embedding_service.generate_embedding(q)
                search_params["vector"] = vector
                search_params["hybrid"] = {"semanticRatio": 0.5}
                logger.info(f"Workflow search with hybrid for query: {q}")
            except Exception as e:
                logger.warning(f"Embedding generation failed for workflow search: {e}")

        results = index.search(q, search_params)

        return WorkflowSearchResponse(
            hits=results.get("hits", []),
            query=q,
            processing_time_ms=results.get("processingTimeMs", 0),
            estimated_total_hits=results.get("estimatedTotalHits", 0),
            page=page,
            page_size=page_size
        )

    except MeilisearchApiError as e:
        logger.error(f"Meilisearch API error in workflow search: {e}")
        raise HTTPException(status_code=502, detail="Search engine error")
    except Exception as e:
        logger.error(f"Unexpected error in workflow search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# =============================================================================
# NEW ENDPOINT: Recent Searches
# =============================================================================

@router.get("/recent", response_model=RecentSearchesResponse)
async def get_recent_searches(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(require_authentication)
):
    """
    Retrieve user's recent search queries.

    Returns the last 10 unique search queries for the authenticated user,
    ordered by recency. Duplicate queries are deduplicated, showing only
    the most recent occurrence of each unique query.

    **Authentication Required:** This endpoint requires a valid JWT token.

    **Returns:**
    - List of recent searches with query text, result count, and timestamp
    - Searches are deduplicated by query text (case-sensitive)
    - Ordered by most recent first

    **Example Response:**
    ```json
    {
      "searches": [
        {
          "query": "对话AI",
          "query_pinyin": "dui hua AI",
          "result_count": 15,
          "searched_at": "2026-01-11T12:30:00Z"
        }
      ],
      "total": 10
    }
    ```
    """
    try:
        # Query to get recent searches with deduplication
        # We use DISTINCT ON to get only the most recent search for each unique query
        # PostgreSQL DISTINCT ON requires the columns to be in ORDER BY
        subquery = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(
                SearchHistory.query,
                SearchHistory.created_at.desc()
            )
            .distinct(SearchHistory.query)
            .limit(10)
        )

        # Execute the query
        result = await db.execute(subquery)
        search_records = result.scalars().all()

        # Convert to response models
        searches = [
            RecentSearchItem(
                query=record.query,
                query_pinyin=record.query_pinyin,
                result_count=record.result_count,
                searched_at=record.created_at
            )
            for record in search_records
        ]

        # Re-sort by searched_at descending (since DISTINCT ON sorted by query first)
        searches.sort(key=lambda x: x.searched_at, reverse=True)

        logger.info(f"Retrieved {len(searches)} recent searches for user {user_id}")

        return RecentSearchesResponse(
            searches=searches,
            total=len(searches)
        )

    except Exception as e:
        logger.error(f"Error retrieving recent searches for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recent searches"
        )
