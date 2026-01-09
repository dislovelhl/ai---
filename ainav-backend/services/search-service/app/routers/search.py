from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from meilisearch import Client
from shared.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
client = Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_KEY)

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
        
        results = index.search(q, search_params)
        return results
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search engine error")
