from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, UUID, ForeignKey, Boolean, Float, ARRAY, Table, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Junction table for Tool and Scenarios (Simplified for now)
tool_scenarios = Table(
    "tool_scenarios",
    Base.metadata,
    Column("tool_id", UUID(as_uuid=True), ForeignKey("tools.id"), primary_key=True),
    Column("scenario_id", UUID(as_uuid=True), ForeignKey("scenarios.id"), primary_key=True),
)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    order = Column(Integer, default=0)

    tools = relationship("Tool", back_populates="category")

class Scenario(Base, TimestampMixin):
    __tablename__ = "scenarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(255))

class Tool(Base, TimestampMixin):
    __tablename__ = "tools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    name_zh = Column(String(255))
    description_zh = Column(Text)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    url = Column(String(512), nullable=False)
    logo_url = Column(String(512))
    pricing_type = Column(String(50)) # e.g., free, freemium, paid
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    
    is_china_accessible = Column(Boolean, default=True)
    requires_vpn = Column(Boolean, default=False)
    
    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    github_stars = Column(Integer, default=0)

    category = relationship("Category", back_populates="tools")
    scenarios = relationship("Scenario", secondary=tool_scenarios)
