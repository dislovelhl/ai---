"""
Pydantic Schema Template
Usage: /gen schema <ResourceName>
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class __RESOURCE_PASCAL__Status(str, Enum):
    """状态枚举"""
    draft = "draft"
    published = "published"
    archived = "archived"


class __RESOURCE_PASCAL__Type(str, Enum):
    """类型枚举"""
    type_a = "type_a"
    type_b = "type_b"


# =============================================================================
# Base Schemas
# =============================================================================

class __RESOURCE_PASCAL__Base(BaseModel):
    """
    基础Schema - 包含创建和更新共享的字段
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="名称",
        examples=["示例名称"],
    )
    name_zh: Optional[str] = Field(
        None,
        max_length=200,
        description="中文名称",
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="详细描述",
    )
    type: __RESOURCE_PASCAL__Type = Field(
        __RESOURCE_PASCAL__Type.type_a,
        description="类型",
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="标签列表",
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        description="扩展元数据",
    )


# =============================================================================
# Create/Update Schemas
# =============================================================================

class __RESOURCE_PASCAL__Create(__RESOURCE_PASCAL__Base):
    """
    创建请求Schema
    """
    # 创建时必需的额外字段
    category_id: UUID = Field(..., description="分类ID")

    @validator("tags")
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError("最多10个标签")
        return v


class __RESOURCE_PASCAL__Update(BaseModel):
    """
    更新请求Schema - 所有字段可选
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    type: Optional[__RESOURCE_PASCAL__Type] = None
    tags: Optional[List[str]] = None
    status: Optional[__RESOURCE_PASCAL__Status] = None
    metadata: Optional[dict[str, Any]] = None


# =============================================================================
# Response Schemas
# =============================================================================

class __RESOURCE_PASCAL__Response(__RESOURCE_PASCAL__Base):
    """
    响应Schema - 包含数据库生成的字段
    """
    id: UUID
    slug: str
    category_id: UUID
    status: __RESOURCE_PASCAL__Status
    created_at: datetime
    updated_at: datetime

    # 计算字段
    view_count: int = 0

    class Config:
        from_attributes = True  # SQLAlchemy兼容


class __RESOURCE_PASCAL__DetailResponse(__RESOURCE_PASCAL__Response):
    """
    详情响应Schema - 包含关联数据
    """
    category: Optional["CategoryResponse"] = None
    related_items: List["__RESOURCE_PASCAL__Response"] = []

    class Config:
        from_attributes = True


class __RESOURCE_PASCAL__ListResponse(BaseModel):
    """
    列表响应Schema - 包含分页信息
    """
    items: List[__RESOURCE_PASCAL__Response]
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


# =============================================================================
# Filter/Query Schemas
# =============================================================================

class __RESOURCE_PASCAL__Filter(BaseModel):
    """
    过滤条件Schema
    """
    type: Optional[__RESOURCE_PASCAL__Type] = None
    status: Optional[__RESOURCE_PASCAL__Status] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


# =============================================================================
# Bulk Operation Schemas
# =============================================================================

class __RESOURCE_PASCAL__BulkCreate(BaseModel):
    """
    批量创建Schema
    """
    items: List[__RESOURCE_PASCAL__Create] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="批量创建项（最多100个）",
    )


class __RESOURCE_PASCAL__BulkUpdate(BaseModel):
    """
    批量更新Schema
    """
    ids: List[UUID] = Field(..., min_length=1, max_length=100)
    data: __RESOURCE_PASCAL__Update


class __RESOURCE_PASCAL__BulkDelete(BaseModel):
    """
    批量删除Schema
    """
    ids: List[UUID] = Field(..., min_length=1, max_length=100)


# =============================================================================
# Import/Export Schemas
# =============================================================================

class __RESOURCE_PASCAL__Import(BaseModel):
    """
    导入Schema
    """
    name: str
    name_zh: Optional[str] = None
    description: Optional[str] = None
    category_slug: str
    tags: List[str] = []


class __RESOURCE_PASCAL__Export(__RESOURCE_PASCAL__Response):
    """
    导出Schema
    """
    category_slug: str
