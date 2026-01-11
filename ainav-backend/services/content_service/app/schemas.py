from pydantic import BaseModel, Field, HttpUrl, UUID4, ConfigDict, field_validator
from typing import List, Optional
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
    alternatives: List[ToolRead] = Field(
        default_factory=list,
        description="List of alternative tools with similar functionality"
    )
    total_count: int = Field(
        0,
        description="Total number of alternatives found"
    )
    prioritized_count: int = Field(
        0,
        description="Number of China-accessible alternatives (when original requires VPN)"
    )

    model_config = ConfigDict(from_attributes=True)
