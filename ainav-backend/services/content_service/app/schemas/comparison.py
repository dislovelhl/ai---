"""
Pydantic schemas for tool comparisons.
"""
from pydantic import BaseModel, Field, UUID4, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime


class ComparisonBase(BaseModel):
    """Base schema for tool comparisons."""
    title: Optional[str] = Field(None, max_length=255, description="Optional user-defined title for the comparison")
    tool_ids: List[UUID4] = Field(..., min_length=2, max_length=4, description="Array of 2-4 tool UUIDs to compare")
    is_public: bool = Field(default=False, description="Whether comparison is publicly accessible")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('tool_ids')
    @classmethod
    def validate_tool_ids_count(cls, v):
        """Ensure tool_ids contains 2-4 unique tools."""
        if len(v) < 2:
            raise ValueError("At least 2 tools are required for comparison")
        if len(v) > 4:
            raise ValueError("Maximum 4 tools allowed for comparison")
        if len(v) != len(set(v)):
            raise ValueError("Tool IDs must be unique")
        return v


class ComparisonCreate(ComparisonBase):
    """Schema for creating a new tool comparison."""
    pass


class ComparisonResponse(ComparisonBase):
    """Schema for basic comparison response without full tool details."""
    id: UUID4
    user_id: UUID4
    share_token: str = Field(..., description="Unique token for public sharing")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolComparisonInfo(BaseModel):
    """Lightweight tool information for comparison display."""
    id: UUID4
    name: str
    name_zh: Optional[str] = None
    slug: str
    description: Optional[str] = None
    description_zh: Optional[str] = None
    url: str
    logo_url: Optional[str] = None
    pricing_type: Optional[str] = None
    is_china_accessible: bool = True
    requires_vpn: bool = False
    avg_rating: float = 0.0
    review_count: int = 0
    github_stars: int = 0

    model_config = ConfigDict(from_attributes=True)


class ComparisonDetail(BaseModel):
    """Schema for detailed comparison response with full tool information."""
    id: UUID4
    user_id: UUID4
    title: Optional[str] = None
    tool_ids: List[UUID4]
    share_token: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    tools: List[ToolComparisonInfo] = Field(..., description="Full details of tools being compared, ordered by tool_ids")

    model_config = ConfigDict(from_attributes=True)


class ComparisonSummary(BaseModel):
    """Lightweight comparison for history listings."""
    id: UUID4
    title: Optional[str] = None
    tool_ids: List[UUID4]
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedComparisonsResponse(BaseModel):
    """Paginated response for comparison history."""
    items: List[ComparisonSummary]
    total: int
    page: int
    page_size: int
    pages: int
