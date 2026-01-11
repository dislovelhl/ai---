from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from shared.config import settings
import logging

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


# =============================================================================
# EXISTING ENDPOINT: Basic Search
# =============================================================================

@router.get("")
async def search_tools(
    q: str = Query("", description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    scenario: Optional[str] = Query(None, description="Filter by scenario slug"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Search AI tools using Meilisearch.
    Supports filtering and pagination.
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
    page_size: int = Query(20, ge=1, le=100, description="Results per page")
):
    """
    Faceted search for AI tools with aggregated filter counts.

    Returns search results along with facet distributions for:
    - pricing_type: Count of tools by pricing model
    - is_china_accessible: Count of tools by China accessibility
    - has_api: Count of tools by API availability
    - category_slug: Count of tools by category

    Use facets to build dynamic filter UIs.
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
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions")
):
    """
    Fast prefix-based autocomplete suggestions.

    Returns lightweight results with only name and slug fields.
    Optimized for real-time typeahead functionality.

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
