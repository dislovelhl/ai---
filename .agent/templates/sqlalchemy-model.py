"""
SQLAlchemy Model Template
Usage: /gen model <ModelName>
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import uuid
from datetime import datetime
import re

from app.core.database import Base


# =============================================================================
# Model Definition
# =============================================================================

class __MODEL_NAME__(Base):
    """
    __MODEL_DESCRIPTION__

    Attributes:
        id: 主键UUID
        name: 名称
        slug: URL友好的标识符
        ...
    """

    __tablename__ = "__TABLE_NAME__"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="主键",
    )

    # =========================================================================
    # Basic Fields
    # =========================================================================

    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="名称",
    )

    name_zh = Column(
        String(200),
        nullable=True,
        comment="中文名称",
    )

    slug = Column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
        comment="URL标识符",
    )

    description = Column(
        Text,
        nullable=True,
        comment="详细描述",
    )

    # =========================================================================
    # Classification
    # =========================================================================

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="分类ID",
    )

    tags = Column(
        ARRAY(String),
        default=[],
        comment="标签列表",
    )

    # =========================================================================
    # Status Fields
    # =========================================================================

    status = Column(
        String(20),
        default="draft",
        nullable=False,
        index=True,
        comment="状态: draft, published, archived",
    )

    is_featured = Column(
        Boolean,
        default=False,
        index=True,
        comment="是否精选",
    )

    priority = Column(
        Integer,
        default=0,
        index=True,
        comment="优先级排序",
    )

    # =========================================================================
    # Metrics
    # =========================================================================

    view_count = Column(
        Integer,
        default=0,
        comment="浏览次数",
    )

    rating_sum = Column(
        Float,
        default=0,
        comment="评分总和",
    )

    rating_count = Column(
        Integer,
        default=0,
        comment="评分数量",
    )

    # =========================================================================
    # Metadata
    # =========================================================================

    metadata = Column(
        JSONB,
        default={},
        comment="扩展元数据",
    )

    # =========================================================================
    # Vector Embedding (pgvector)
    # =========================================================================

    # Uncomment if using pgvector
    # from pgvector.sqlalchemy import Vector
    # embedding = Column(
    #     Vector(1024),
    #     nullable=True,
    #     comment="向量嵌入",
    # )

    # =========================================================================
    # Timestamps
    # =========================================================================

    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    published_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="发布时间",
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    category = relationship(
        "Category",
        back_populates="__TABLE_NAME__",
        lazy="selectin",
    )

    ratings = relationship(
        "Rating",
        back_populates="__SINGULAR_NAME__",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # =========================================================================
    # Table Configuration
    # =========================================================================

    __table_args__ = (
        # Indexes
        Index("idx___TABLE_NAME___category_status", "category_id", "status"),
        Index("idx___TABLE_NAME___featured_priority", "is_featured", "priority"),
        Index("idx___TABLE_NAME___created_at", "created_at", postgresql_using="brin"),

        # Unique constraints
        UniqueConstraint("slug", name="uq___TABLE_NAME___slug"),

        # Check constraints
        CheckConstraint("priority >= 0", name="ck___TABLE_NAME___priority_positive"),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck___TABLE_NAME___status_valid",
        ),

        # Table comment
        {"comment": "__MODEL_DESCRIPTION__"},
    )

    # =========================================================================
    # Hybrid Properties
    # =========================================================================

    @hybrid_property
    def average_rating(self) -> float:
        """计算平均评分"""
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_sum / self.rating_count, 2)

    @hybrid_property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == "published"

    # =========================================================================
    # Validators
    # =========================================================================

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("名称不能为空")
        return value.strip()

    @validates("slug")
    def validate_slug(self, key, value):
        if not value:
            return value
        # 只允许小写字母、数字和连字符
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value):
            raise ValueError("slug格式无效")
        return value

    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ["draft", "published", "archived"]
        if value not in valid_statuses:
            raise ValueError(f"状态必须是: {', '.join(valid_statuses)}")
        return value

    # =========================================================================
    # Methods
    # =========================================================================

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "name_zh": self.name_zh,
            "slug": self.slug,
            "description": self.description,
            "category_id": str(self.category_id) if self.category_id else None,
            "tags": self.tags,
            "status": self.status,
            "is_featured": self.is_featured,
            "average_rating": self.average_rating,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def publish(self) -> None:
        """发布"""
        self.status = "published"
        self.published_at = datetime.utcnow()

    def archive(self) -> None:
        """归档"""
        self.status = "archived"

    def increment_view(self) -> None:
        """增加浏览次数"""
        self.view_count += 1

    def add_rating(self, score: float) -> None:
        """添加评分"""
        self.rating_sum += score
        self.rating_count += 1

    def __repr__(self) -> str:
        return f"<__MODEL_NAME__(id={self.id}, name={self.name}, slug={self.slug})>"


# =============================================================================
# Event Listeners
# =============================================================================

@event.listens_for(__MODEL_NAME__, "before_insert")
def before_insert(mapper, connection, target):
    """插入前生成slug"""
    if not target.slug:
        target.slug = _generate_slug(target.name)


@event.listens_for(__MODEL_NAME__, "before_update")
def before_update(mapper, connection, target):
    """更新前处理"""
    pass


def _generate_slug(name: str) -> str:
    """从名称生成slug"""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "untitled"
