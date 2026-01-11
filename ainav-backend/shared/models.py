from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, UUID, ForeignKey, Boolean, Float, ARRAY, Table, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

# Conditional import for pgvector
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # pgvector not installed - will fail at runtime if Vector columns are accessed
    Vector = None

Base = declarative_base()


class UserTier(str, enum.Enum):
    """User subscription tier for rate limiting and feature access."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


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

# Junction table for AgentWorkflow and WorkflowTag
workflow_workflow_tags = Table(
    "workflow_workflow_tags",
    Base.metadata,
    Column("workflow_id", UUID(as_uuid=True), ForeignKey("agent_workflows.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("workflow_tags.id"), primary_key=True),
)

# Junction table for User and AgentWorkflow stars (prevents duplicate stars, enables unstar)
workflow_stars = Table(
    "workflow_stars",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("workflow_id", UUID(as_uuid=True), ForeignKey("agent_workflows.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


# Junction table for LearningPath and Tools (recommended tools)
learning_path_tools = Table(
    "learning_path_tools",
    Base.metadata,
    Column("learning_path_id", UUID(as_uuid=True), ForeignKey("learning_paths.id"), primary_key=True),
    Column("tool_id", UUID(as_uuid=True), ForeignKey("tools.id"), primary_key=True),
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
    user_tier = Column(Enum(UserTier), default=UserTier.FREE, nullable=False)

    # Admin and authorization fields
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    permissions = Column(ARRAY(String), default=list)  # Flexible permissions array

    # OAuth provider IDs
    github_id = Column(String(50), unique=True, index=True, nullable=True)
    wechat_id = Column(String(50), unique=True, index=True, nullable=True)

    # Relationship to agent workflows
    workflows = relationship("AgentWorkflow", back_populates="user")
    starred_workflows = relationship("AgentWorkflow", secondary=workflow_stars, backref="starred_by")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    learning_progress = relationship("UserLearningProgress", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("LearningCertificate", back_populates="user", cascade="all, delete-orphan")


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
    description = Column(Text)
    description_zh = Column(Text)
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

    # Manual override fields for accessibility status
    manual_override_enabled = Column(Boolean, default=False)
    manual_override_reason = Column(Text, nullable=True)
    manual_override_set_by = Column(String(255), nullable=True)
    manual_override_set_at = Column(DateTime(timezone=True), nullable=True)

    # Accessibility check tracking
    last_accessibility_check = Column(DateTime(timezone=True), nullable=True)

    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    github_stars = Column(Integer, default=0)
    
    # NEW: Flag indicating tool has API skills available
    has_api = Column(Boolean, default=False)

    category = relationship("Category", back_populates="tools")
    scenarios = relationship("Scenario", secondary=tool_scenarios)
    # Relationship to skills
    skills = relationship("Skill", back_populates="tool", cascade="all, delete-orphan")
    # Relationship to learning paths
    learning_paths = relationship("LearningPath", secondary=learning_path_tools, back_populates="recommended_tools")


class LearningPath(Base, TimestampMixin):
    """
    LearningPath: Structured learning roadmaps for AI skills and tools.
    """
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    name_zh = Column(String(255))
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    description_zh = Column(Text)
    icon = Column(String(255))

    # Difficulty and time estimation
    difficulty_level = Column(String(20), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    estimated_hours = Column(Integer)

    # Categorization and ordering
    category = Column(String(100))
    order = Column(Integer, default=0)

    # Publishing status
    is_published = Column(Boolean, default=False)

    # Learning structure (JSON arrays)
    prerequisites = Column(JSON, default=list)  # ["Python basics", "SQL fundamentals"]
    learning_outcomes = Column(JSON, default=list)  # ["Build REST APIs", "Deploy to cloud"]

    # Relationships
    modules = relationship("LearningPathModule", back_populates="learning_path", cascade="all, delete-orphan")
    user_progress = relationship("UserLearningProgress", back_populates="learning_path", cascade="all, delete-orphan")
    certificates = relationship("LearningCertificate", back_populates="learning_path", cascade="all, delete-orphan")
    recommended_tools = relationship("Tool", secondary=learning_path_tools, back_populates="learning_paths")


class LearningPathModule(Base, TimestampMixin):
    """
    LearningPathModule: Individual learning modules within a learning path.
    Each module represents a discrete learning unit (video, article, tutorial, exercise).
    """
    __tablename__ = "learning_path_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)

    # Module ordering and identification
    order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    title_zh = Column(String(255))
    description = Column(Text)
    description_zh = Column(Text)

    # Content details
    content_type = Column(String(20), nullable=False)  # 'video', 'article', 'tutorial', 'exercise'
    content_url = Column(String(512))
    estimated_minutes = Column(Integer)

    # Requirement and assessment
    is_required = Column(Boolean, default=True)
    quiz_data = Column(JSON)  # {"questions": [...], "passing_score": 80}

    # Relationship
    learning_path = relationship("LearningPath", back_populates="modules")


class UserLearningProgress(Base, TimestampMixin):
    """
    UserLearningProgress: Tracks user progress through learning paths.
    """
    __tablename__ = "user_learning_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)

    # Progress tracking
    status = Column(String(20), nullable=False, default="not_started")  # 'not_started', 'in_progress', 'completed'
    progress_percentage = Column(Float, default=0.0)  # 0.0 - 100.0
    completed_modules = Column(JSON, default=list)  # Array of module UUIDs (as strings)

    # Timestamps for progress lifecycle
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="learning_progress")
    learning_path = relationship("LearningPath", back_populates="user_progress")


class LearningCertificate(Base, TimestampMixin):
    """
    LearningCertificate: Represents completion certificates issued to users
    after successfully completing a learning path.
    """
    __tablename__ = "learning_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)

    # Certificate identification
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)

    # Certificate file and sharing
    certificate_url = Column(String(512), nullable=False)  # Path to generated PDF
    share_token = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)

    # Engagement metrics
    view_count = Column(Integer, default=0)

    # Issuance timestamp
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="certificates")
    learning_path = relationship("LearningPath", back_populates="certificates")


# =============================================================================
# AGENTIC PLATFORM MODELS
# =============================================================================

class WorkflowCategory(Base, TimestampMixin):
    """
    WorkflowCategory: Categories for organizing agent workflows in the gallery.
    """
    __tablename__ = "workflow_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_zh = Column(String(100))
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    description_zh = Column(Text)
    icon = Column(String(255))
    order = Column(Integer, default=0)

    # Relationship to workflows
    workflows = relationship("AgentWorkflow", back_populates="category")


class WorkflowTag(Base, TimestampMixin):
    """
    WorkflowTag: Tags for filtering and searching workflows.
    """
    __tablename__ = "workflow_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, index=True, nullable=False)
    name_zh = Column(String(50))
    slug = Column(String(50), unique=True, index=True, nullable=False)
    usage_count = Column(Integer, default=0)  # Track how many workflows use this tag

    # Relationship to workflows (many-to-many)
    workflows = relationship("AgentWorkflow", secondary=workflow_workflow_tags, back_populates="tags")


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

    # Category for organization
    category_id = Column(UUID(as_uuid=True), ForeignKey("workflow_categories.id"), nullable=True)
    
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

    # Template-specific metadata
    category = Column(String(100), nullable=True)  # 'content-generation', 'translation', 'summarization', 'data-analysis'
    use_case = Column(String(255), nullable=True)  # Specific use case description
    usage_instructions_zh = Column(Text, nullable=True)  # Step-by-step usage guide in Chinese
    tags = Column(ARRAY(String), nullable=True)  # Flexible tags for discovery and filtering
    
    # Version tracking
    version = Column(Integer, default=1, nullable=False)
    version_history = Column(JSON, default=list)  # [{version, changes, timestamp}, ...]
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    category = relationship("WorkflowCategory", back_populates="workflows")
    tags = relationship("WorkflowTag", secondary=workflow_workflow_tags, back_populates="workflows")
    executions = relationship("AgentExecution", back_populates="workflow", cascade="all, delete-orphan")
    forked_from = relationship("AgentWorkflow", remote_side=[id])


class AgentExecution(Base, TimestampMixin):
    """
    AgentExecution: Runtime execution logs for agent workflows.
    """
    __tablename__ = "agent_executions"
    __table_args__ = (
        # Index for querying executions by workflow and status
        {"schema": None}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("agent_workflows.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Replay tracking - link to original execution if this is a replay
    parent_execution_id = Column(UUID(as_uuid=True), ForeignKey("agent_executions.id"), nullable=True, index=True)
    replayed_from_step = Column(String(100), nullable=True)  # Node ID from which replay started

    # Execution status
    status = Column(String(20), default="pending", index=True)  # 'pending', 'running', 'completed', 'failed', 'cancelled'

    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)

    # Execution trace - step-by-step log of node executions (deprecated, use execution_steps)
    execution_log = Column(JSON)  # [{node_id, status, input, output, duration_ms, timestamp}, ...]

    # Detailed per-node execution data for real-time debugging
    # Format: [
    #   {
    #     "node_id": "uuid",
    #     "status": "pending|running|completed|failed",
    #     "input_data": {...},
    #     "output_data": {...},
    #     "error_message": "...",
    #     "token_usage": {"input": 0, "output": 0, "total": 0},
    #     "started_at": "2024-01-01T00:00:00Z",
    #     "completed_at": "2024-01-01T00:00:01Z"
    #   },
    #   ...
    # ]
    execution_steps = Column(JSON, default=list)

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
    embedding = Column(Vector(384)) if Vector is not None else None


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
