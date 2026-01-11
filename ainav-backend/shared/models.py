from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, UUID, ForeignKey, Boolean, Float, ARRAY, Table, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enum for authorization"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class ModerationStatus(str, enum.Enum):
    """Moderation status for submitted content"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


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
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Admin and authorization fields
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    permissions = Column(ARRAY(String), default=list)  # Flexible permissions array

    # OAuth provider IDs
    github_id = Column(String(50), unique=True, index=True, nullable=True)
    wechat_id = Column(String(50), unique=True, index=True, nullable=True)

    # Relationship to agent workflows
    workflows = relationship("AgentWorkflow", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")


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
    pricing_type = Column(String(50))  # e.g., free, freemium, paid
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    
    is_china_accessible = Column(Boolean, default=True)
    requires_vpn = Column(Boolean, default=False)
    
    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    github_stars = Column(Integer, default=0)
    
    # NEW: Flag indicating tool has API skills available
    has_api = Column(Boolean, default=False)

    category = relationship("Category", back_populates="tools")
    scenarios = relationship("Scenario", secondary=tool_scenarios)
    # Relationship to skills
    skills = relationship("Skill", back_populates="tool", cascade="all, delete-orphan")


# =============================================================================
# AGENTIC PLATFORM MODELS
# =============================================================================

class Skill(Base, TimestampMixin):
    """
    Skill: Represents what a tool CAN DO via API.
    This abstracts tool capabilities into callable actions for the agent system.
    """
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    
    # Skill identification
    name = Column(String(100), nullable=False)  # e.g., "Search GitHub Repos"
    name_zh = Column(String(100))
    slug = Column(String(100), index=True, nullable=False)
    description = Column(Text)
    description_zh = Column(Text)
    
    # API Definition (OpenAPI-style)
    api_endpoint = Column(String(512))
    http_method = Column(String(10))  # GET, POST, PUT, DELETE, PATCH
    input_schema = Column(JSON)   # JSON Schema for request parameters
    output_schema = Column(JSON)  # JSON Schema for response
    headers_template = Column(JSON)  # Template for request headers
    
    # Authentication configuration
    auth_type = Column(String(50), default="none")  # 'api_key', 'oauth2', 'bearer', 'none'
    auth_config = Column(JSON)  # {"header": "Authorization", "prefix": "Bearer", "env_var": "GITHUB_TOKEN"}
    
    # Status and usage
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    avg_latency_ms = Column(Float, default=0.0)
    
    # Relationship
    tool = relationship("Tool", back_populates="skills")


class AgentWorkflow(Base, TimestampMixin):
    """
    AgentWorkflow: User-created agent blueprints stored as React Flow graph definitions.
    """
    __tablename__ = "agent_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Workflow metadata
    name = Column(String(255), nullable=False)
    name_zh = Column(String(255))
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    description_zh = Column(Text)
    icon = Column(String(100))  # Emoji or icon name
    
    # React Flow graph definition
    graph_json = Column(JSON, nullable=False)  # {nodes: [], edges: [], viewport: {}}
    
    # Execution configuration
    trigger_type = Column(String(50), default="manual")  # 'manual', 'schedule', 'webhook'
    trigger_config = Column(JSON)  # {"cron": "0 9 * * *"} or {"webhook_secret": "..."}
    
    # Default input schema (what the workflow expects)
    input_schema = Column(JSON)
    # LLM settings
    llm_model = Column(String(100), default="deepseek-chat")
    system_prompt = Column(Text)
    temperature = Column(Float, default=0.7)
    
    # Sharing and stats
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    forked_from_id = Column(UUID(as_uuid=True), ForeignKey("agent_workflows.id"), nullable=True)
    fork_count = Column(Integer, default=0)
    run_count = Column(Integer, default=0)
    star_count = Column(Integer, default=0)
    
    # Version tracking
    version = Column(Integer, default=1, nullable=False)
    version_history = Column(JSON, default=list)  # [{version, changes, timestamp}, ...]
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    executions = relationship("AgentExecution", back_populates="workflow", cascade="all, delete-orphan")
    forked_from = relationship("AgentWorkflow", remote_side=[id])


class AgentExecution(Base, TimestampMixin):
    """
    AgentExecution: Runtime execution logs for agent workflows.
    """
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("agent_workflows.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Execution status
    status = Column(String(20), default="pending")  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    
    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Execution trace - step-by-step log of node executions
    execution_log = Column(JSON)  # [{node_id, status, input, output, duration_ms, timestamp}, ...]
    
    # Usage metrics
    token_usage = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)
    duration_ms = Column(Integer)
    
    # Trigger info
    trigger_type = Column(String(50))  # How was this execution triggered
    trigger_metadata = Column(JSON)  # Additional trigger context
    
    # Relationships
    workflow = relationship("AgentWorkflow", back_populates="executions")


class AgentMemory(Base, TimestampMixin):
    """
    AgentMemory: Long-term memory storage for RAG retrieval (Phase 3).
    Uses pgvector for semantic search.
    """
    __tablename__ = "agent_memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("agent_workflows.id"), nullable=False)
    
    # Memory content
    content = Column(Text, nullable=False)
    content_type = Column(String(50))  # 'conversation', 'document', 'fact', 'summary'
    
    # Metadata for filtering
    meta_data = Column(JSON)  # Flexible metadata (source, timestamp, tags, etc.)
    
    # Vector embedding for semantic search
    # Using 384 dimensions for MiniLM-L12-v2
    from pgvector.sqlalchemy import Vector
    embedding = Column(Vector(384))


class UserInteraction(Base, TimestampMixin):
    """
    Tracks user interactions with tools and agents for personalization.
    """
    __tablename__ = "user_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Target item
    item_type = Column(String(50), nullable=False)  # 'tool', 'agent', 'roadmap'
    item_id = Column(UUID(as_uuid=True), nullable=False)

    # Action details
    action = Column(String(50), nullable=False)  # 'view', 'click', 'run', 'like', 'fork'
    weight = Column(Float, default=1.0)

    # Metadata
    meta_data = Column(JSON)  # {"search_query": "...", "referral": "..."}

    # Relationship
    user = relationship("User", back_populates="interactions")


class ModerationQueue(Base, TimestampMixin):
    """
    Tracks user-submitted content pending admin review.
    Used for workflows shared publicly, tool suggestions, etc.
    """
    __tablename__ = "moderation_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Content type and reference
    content_type = Column(String(50), nullable=False)  # 'workflow', 'tool_suggestion', etc.
    content_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to actual content (workflow_id, etc.)

    # Submission data (for tool suggestions or draft content)
    content_data = Column(JSON, nullable=True)  # Flexible storage for submitted data

    # Status
    status = Column(Enum(ModerationStatus), default=ModerationStatus.PENDING, nullable=False)

    # People involved
    submitter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Review details
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Relationships
    submitter = relationship("User", foreign_keys=[submitter_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])


class AdminActivityLog(Base, TimestampMixin):
    """
    Audit trail for admin actions.
    Tracks all create/update/delete operations and moderation actions.
    """
    __tablename__ = "admin_activity_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Admin who performed the action
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Action details
    action_type = Column(String(50), nullable=False)  # 'create', 'update', 'delete', 'approve', 'reject'
    resource_type = Column(String(50), nullable=False)  # 'tool', 'category', 'scenario', 'workflow', etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)  # UUID of the affected resource

    # Change tracking (JSON for flexibility)
    old_value = Column(JSON, nullable=True)  # Previous state before the change
    new_value = Column(JSON, nullable=True)  # New state after the change

    # Additional context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(255), nullable=True)

    # Relationship
    admin = relationship("User", foreign_keys=[admin_id])
