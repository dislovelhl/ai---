"""
Pydantic schemas for content service.

This module re-exports all schemas for convenient imports.
"""
from pydantic import BaseModel
from typing import List

# Import comparison schemas from submodule
from .comparison import (
    ComparisonCreate,
    ComparisonResponse,
    ComparisonDetail,
    ComparisonSummary,
    ToolComparisonInfo,
    PaginatedComparisonsResponse,
)

# Import all schemas from the parent schemas.py file using relative path
# These are defined in services/content_service/app/schemas.py
from pydantic import ConfigDict
from pydantic import Field, HttpUrl, UUID4, field_validator
from typing import Optional
from datetime import datetime


# --- Common ---
class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- Scenarios ---
class ScenarioBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    icon: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=255)


class ScenarioRead(ScenarioBase, TimestampSchema):
    id: UUID4


# --- Categories ---
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    order: int = 0

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    order: Optional[int] = None


class CategoryRead(CategoryBase, TimestampSchema):
    id: UUID4
    tool_count: int = 0


# --- Tools ---
class ToolBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_zh: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    url: str = Field(..., max_length=512)
    logo_url: Optional[str] = Field(None, max_length=512)
    pricing_type: Optional[str] = Field(None, max_length=50)
    is_china_accessible: bool = True
    requires_vpn: bool = False
    github_stars: int = 0

    model_config = ConfigDict(from_attributes=True)

    @field_validator('github_stars', mode='before')
    @classmethod
    def coerce_github_stars(cls, v):
        """Coerce None to 0 for github_stars field."""
        return v if v is not None else 0


class ToolCreate(ToolBase):
    category_id: Optional[UUID4] = None
    scenario_ids: List[UUID4] = []


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    pricing_type: Optional[str] = Field(None, max_length=50)
    is_china_accessible: Optional[bool] = None
    requires_vpn: Optional[bool] = None
    category_id: Optional[UUID4] = None
    github_stars: Optional[int] = None
    scenario_ids: Optional[List[UUID4]] = None


class ToolRead(ToolBase, TimestampSchema):
    id: UUID4
    category: Optional[CategoryRead] = None
    scenarios: List[ScenarioRead] = []
    avg_rating: float = 0.0
    review_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ToolAlternativesResponse(BaseModel):
    """Response schema for tool alternatives endpoint."""
    alternatives: List[ToolRead]
    total_count: int
    prioritized_count: int = 0


# --- Learning Path Modules ---
class LearningPathModuleBase(BaseModel):
    order: int = Field(..., ge=0)
    title: str = Field(..., max_length=255)
    title_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    content_type: str = Field(..., max_length=20)
    content_url: Optional[str] = Field(None, max_length=512)
    estimated_minutes: Optional[int] = Field(None, ge=0)
    is_required: bool = True
    quiz_data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class LearningPathModuleCreate(LearningPathModuleBase):
    learning_path_id: UUID4


class LearningPathModuleUpdate(BaseModel):
    order: Optional[int] = Field(None, ge=0)
    title: Optional[str] = Field(None, max_length=255)
    title_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    content_type: Optional[str] = Field(None, max_length=20)
    content_url: Optional[str] = Field(None, max_length=512)
    estimated_minutes: Optional[int] = Field(None, ge=0)
    is_required: Optional[bool] = None
    quiz_data: Optional[dict] = None


class LearningPathModuleRead(LearningPathModuleBase, TimestampSchema):
    id: UUID4
    learning_path_id: UUID4


# --- Learning Paths ---
class LearningPathBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_zh: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    difficulty_level: str = Field(..., max_length=20)
    estimated_hours: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    order: int = 0
    is_published: bool = False
    prerequisites: List[str] = []
    learning_outcomes: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class LearningPathCreate(LearningPathBase):
    tool_ids: List[UUID4] = []


class LearningPathUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    name_zh: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    estimated_hours: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    order: Optional[int] = None
    is_published: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    tool_ids: Optional[List[UUID4]] = None


class LearningPathRead(LearningPathBase, TimestampSchema):
    id: UUID4
    modules: List[LearningPathModuleRead] = []
    recommended_tools: List[ToolRead] = []

    model_config = ConfigDict(from_attributes=True)


# --- Recommendation Schemas ---
class ToolRecommendationRead(BaseModel):
    """Tool recommendation with score."""
    tool: ToolRead
    recommendation_score: float


class ToolCombinationRead(BaseModel):
    """Tool combination with co-occurrence count."""
    tools: List[ToolRead]
    co_occurrence_count: int


class RelatedScenarioRead(BaseModel):
    """Related scenario with similarity score."""
    scenario: ScenarioRead
    similarity_score: float


__all__ = [
    # Comparison schemas
    "ComparisonCreate",
    "ComparisonResponse",
    "ComparisonDetail",
    "ComparisonSummary",
    "ToolComparisonInfo",
    "PaginatedComparisonsResponse",
    # Base schemas
    "TimestampSchema",
    # Scenario schemas
    "ScenarioBase",
    "ScenarioCreate",
    "ScenarioUpdate",
    "ScenarioRead",
    # Category schemas
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryRead",
    # Tool schemas
    "ToolBase",
    "ToolCreate",
    "ToolUpdate",
    "ToolRead",
    "ToolAlternativesResponse",
    # Learning path schemas
    "LearningPathModuleBase",
    "LearningPathModuleCreate",
    "LearningPathModuleUpdate",
    "LearningPathModuleRead",
    "LearningPathBase",
    "LearningPathCreate",
    "LearningPathUpdate",
    "LearningPathRead",
    # Recommendation schemas
    "ToolRecommendationRead",
    "ToolCombinationRead",
    "RelatedScenarioRead",
]

