"""
Comparisons Router - CRUD operations for tool comparisons.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
import secrets

from ..dependencies import get_db
from shared.models import ToolComparison, Tool
from ..schemas import (
    ComparisonCreate,
    ComparisonResponse,
    ComparisonDetail,
    ComparisonSummary,
    PaginatedComparisonsResponse,
    ToolComparisonInfo,
)

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.post("/", response_model=ComparisonResponse)
async def create_comparison(
    comparison_in: ComparisonCreate,
    user_id: UUID,  # TODO: Get from auth dependency (e.g., current_user = Depends(get_current_user))
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new tool comparison.

    Validates that:
    - 2-4 unique tool IDs are provided (handled by schema validation)
    - All tool IDs exist in the database

    Generates a unique share_token for public sharing.
    """
    # Validate that all tool IDs exist
    tools_query = select(Tool.id).where(Tool.id.in_(comparison_in.tool_ids))
    result = await db.execute(tools_query)
    existing_tool_ids = set(result.scalars().all())

    # Check if all provided tool IDs exist
    provided_tool_ids = set(comparison_in.tool_ids)
    missing_tool_ids = provided_tool_ids - existing_tool_ids

    if missing_tool_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Tools not found: {', '.join(str(tid) for tid in missing_tool_ids)}"
        )

    # Generate unique share token
    share_token = secrets.token_urlsafe(16)

    # Ensure share_token is unique (very unlikely to collide, but safety check)
    max_attempts = 5
    for _ in range(max_attempts):
        check_query = select(ToolComparison.id).where(ToolComparison.share_token == share_token)
        existing = await db.execute(check_query)
        if existing.scalar_one_or_none() is None:
            break
        share_token = secrets.token_urlsafe(16)

    # Create the comparison
    comparison = ToolComparison(
        user_id=user_id,
        title=comparison_in.title,
        tool_ids=comparison_in.tool_ids,
        is_public=comparison_in.is_public,
        share_token=share_token,
    )

    db.add(comparison)
    await db.commit()
    await db.refresh(comparison)

    return comparison
