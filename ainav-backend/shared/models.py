from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, UUID, ForeignKey, Boolean, Float, ARRAY, Table, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSON
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
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

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


# =============================================================================
# SUBSCRIPTION & BILLING MODELS
# =============================================================================

class SubscriptionPlan(Base, TimestampMixin):
    """
    SubscriptionPlan: Defines tiered subscription plans with execution limits and pricing.
    Supports Chinese payment methods via Stripe (Alipay, WeChat Pay).
    """
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Plan identification
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Free", "Pro"
    name_zh = Column(String(100), nullable=False)  # e.g., "免费版", "专业版"
    slug = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "free", "pro"
    description = Column(Text)
    description_zh = Column(Text)

    # Tier level (for easy comparison)
    tier = Column(String(50), nullable=False, index=True)  # 'free', 'pro', 'enterprise'

    # Execution limits
    daily_execution_limit = Column(Integer, nullable=False, default=50)  # Executions per day
    monthly_execution_limit = Column(Integer, nullable=False, default=1500)  # Executions per month

    # Pricing (in CNY - Chinese Yuan)
    price_monthly = Column(Float, nullable=False, default=0.0)  # Monthly price in CNY
    price_yearly = Column(Float, nullable=False, default=0.0)  # Yearly price in CNY (with discount)

    # Stripe integration
    stripe_price_id_monthly = Column(String(255), nullable=True)  # Stripe Price ID for monthly billing
    stripe_price_id_yearly = Column(String(255), nullable=True)  # Stripe Price ID for yearly billing
    stripe_product_id = Column(String(255), nullable=True)  # Stripe Product ID

    # Features (stored as JSON for flexibility)
    features = Column(JSON)  # {"priority_support": true, "advanced_analytics": true, etc.}
    features_zh = Column(JSON)  # Chinese feature descriptions

    # Chinese payment method support
    supports_alipay = Column(Boolean, default=True)
    supports_wechat_pay = Column(Boolean, default=True)

    # Plan settings
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # Highlight as "most popular"
    display_order = Column(Integer, default=0)  # For sorting on pricing page

    # Priority level for execution queue
    priority_level = Column(Integer, default=0)  # 0=normal, 1=high, 2=critical

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base, TimestampMixin):
    """
    UserSubscription: Tracks user subscription status, Stripe integration, and billing information.
    Links users to their active subscription plan and manages payment methods.
    """
    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)

    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, index=True, nullable=True)  # Stripe Customer ID
    stripe_subscription_id = Column(String(255), unique=True, index=True, nullable=True)  # Stripe Subscription ID
    stripe_payment_method_id = Column(String(255), nullable=True)  # Stripe Payment Method ID

    # Payment method details
    payment_method = Column(String(50), nullable=True)  # 'card', 'alipay', 'wechat_pay'
    payment_method_last4 = Column(String(4), nullable=True)  # Last 4 digits of card or account
    payment_method_brand = Column(String(50), nullable=True)  # 'visa', 'mastercard', 'alipay', 'wechat'

    # Subscription status
    status = Column(String(50), default="active", nullable=False, index=True)  # 'active', 'cancelled', 'past_due', 'trialing', 'expired'

    # Billing cycle
    billing_cycle = Column(String(20), default="monthly")  # 'monthly', 'yearly'
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True, index=True)

    # Cancellation tracking
    cancel_at_period_end = Column(Boolean, default=False)  # Auto-cancel at end of billing period
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Trial tracking
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata = Column(JSON)  # Additional Stripe metadata

    # Relationships
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


class UsageRecord(Base, TimestampMixin):
    """
    UsageRecord: Tracks daily and monthly workflow execution counts per user.
    Used for enforcing subscription limits and analytics.
    """
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Date tracking
    record_date = Column(DateTime(timezone=True), nullable=False, index=True)  # Date for this usage record
    period_type = Column(String(20), nullable=False, index=True)  # 'daily' or 'monthly'

    # Year and month for efficient monthly queries
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)  # 1-12
    day = Column(Integer, nullable=True)  # 1-31 (null for monthly records)

    # Execution counts
    execution_count = Column(Integer, default=0, nullable=False)  # Number of workflow executions

    # Usage metadata
    workflow_ids = Column(JSON)  # List of workflow IDs executed (for analytics)

    # Relationships
    user = relationship("User", backref="usage_records")


class PaymentTransaction(Base, TimestampMixin):
    """
    PaymentTransaction: Records all payment transactions and billing history.
    Supports Stripe payments with Chinese payment methods (Alipay, WeChat Pay).
    """
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("user_subscriptions.id"), nullable=True)

    # Stripe transaction IDs
    stripe_payment_intent_id = Column(String(255), unique=True, index=True, nullable=True)  # Stripe PaymentIntent ID
    stripe_charge_id = Column(String(255), unique=True, index=True, nullable=True)  # Stripe Charge ID
    stripe_invoice_id = Column(String(255), unique=True, index=True, nullable=True)  # Stripe Invoice ID

    # Transaction details
    amount = Column(Float, nullable=False)  # Transaction amount
    currency = Column(String(3), default="CNY", nullable=False)  # ISO currency code (CNY, USD, etc.)

    # Payment method
    payment_method = Column(String(50), nullable=False)  # 'card', 'alipay', 'wechat_pay'
    payment_method_brand = Column(String(50), nullable=True)  # 'visa', 'mastercard', 'alipay', 'wechat'
    payment_method_last4 = Column(String(4), nullable=True)  # Last 4 digits for reference

    # Transaction status
    status = Column(String(50), default="pending", nullable=False, index=True)  # 'pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded'

    # Transaction type
    transaction_type = Column(String(50), nullable=False)  # 'subscription', 'upgrade', 'renewal', 'refund'

    # Billing period (for subscription payments)
    billing_period_start = Column(DateTime(timezone=True), nullable=True)
    billing_period_end = Column(DateTime(timezone=True), nullable=True)

    # Error tracking (for failed transactions)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Refund tracking
    refunded_amount = Column(Float, default=0.0)  # Amount refunded (if applicable)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    refund_reason = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON)  # Additional Stripe metadata and custom fields

    # Payment provider details (for Chinese payment methods)
    provider = Column(String(50), default="stripe")  # 'stripe', 'alipay_direct', 'wechat_direct' (future expansion)
    provider_transaction_id = Column(String(255), nullable=True)  # Provider-specific transaction ID

    # Relationships
    user = relationship("User", backref="payment_transactions")
    subscription = relationship("UserSubscription", backref="payment_transactions")
