# C4 Code Level: Shared Backend Module

## Overview

- **Name**: Shared Backend Module
- **Description**: Common utilities, models, database configuration, email service, and embedding service shared across all backend microservices
- **Location**: `/ainav-backend/shared`
- **Language**: Python 3.11+
- **Purpose**: Provides centralized database models, ORM session management, application configuration, transactional email delivery, and vector embeddings for RAG functionality

## Code Elements

### Configuration Management

#### `Settings` (config.py)
- **Description**: Pydantic BaseSettings class for environment-based configuration
- **Location**: `/ainav-backend/shared/config.py:1-96`
- **Responsibilities**:
  - Load environment variables from `.env` file
  - Provide type-safe configuration access across all services
  - Validate security settings in production environments
  - Manage credentials, OAuth settings, email configuration, and API keys

**Key Attributes**:
- `DATABASE_URL: str` - PostgreSQL async connection string
- `REDIS_URL: str` - Redis cache connection URL
- `MEILISEARCH_URL: str` - Search service endpoint
- `MEILISEARCH_KEY: str` - Meilisearch API key
- `DEEPSEEK_API_KEY: Optional[str]` - LLM provider API key
- `GITHUB_CLIENT_ID: Optional[str]` - OAuth2 GitHub client identifier
- `GITHUB_CLIENT_SECRET: Optional[str]` - OAuth2 GitHub client secret
- `GITHUB_REDIRECT_URI: str` - OAuth2 callback URL for GitHub
- `WECHAT_APP_ID: Optional[str]` - OAuth2 WeChat app identifier
- `WECHAT_APP_SECRET: Optional[str]` - OAuth2 WeChat app secret
- `WECHAT_REDIRECT_URI: str` - OAuth2 callback URL for WeChat
- `FRONTEND_URL: str` - Frontend application base URL
- `DEBUG: bool` - Debug mode flag
- `ENVIRONMENT: str` - Environment identifier (development/production)
- `CORS_ORIGINS: list[str]` - Allowed CORS origins
- `DEFAULT_PAGE_SIZE: int` - Default pagination size (20)
- `MAX_PAGE_SIZE: int` - Maximum pagination size (100)
- `SECRET_KEY: str` - JWT signing key (32+ chars in production)
- `ALGORITHM: str` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES: int` - Access token TTL (60 minutes)
- `REFRESH_TOKEN_EXPIRE_DAYS: int` - Refresh token TTL (7 days)
- `SMTP_HOST: str` - Email server hostname (default: smtp.qq.com)
- `SMTP_PORT: int` - Email server port (default: 465 for SSL)
- `SMTP_USER: Optional[str]` - Email account username
- `SMTP_PASSWORD: Optional[str]` - Email account password
- `SMTP_FROM_EMAIL: Optional[str]` - Sender email address
- `SMTP_FROM_NAME: str` - Sender display name (AI导航)
- `SMTP_USE_SSL: bool` - Enable SSL for SMTP
- `SMTP_USE_TLS: bool` - Enable TLS for SMTP

**Key Methods**:
- `validate_security_settings() -> None` - Validates SECRET_KEY requirements in production (line 65-73)
- `get_utc_now() -> datetime` - Returns current UTC datetime (line 89-91)

**Singleton Instance**: `settings` (line 96)

### Database Session Management

#### `engine` (database.py)
- **Description**: SQLAlchemy async engine configured for PostgreSQL with asyncpg driver
- **Location**: `/ainav-backend/shared/database.py:3-11`
- **Responsibilities**:
  - Create async connection pool to PostgreSQL
  - Enable connection health checks (pool_pre_ping=True)
  - Echo SQL statements in development mode

#### `SessionLocal` (database.py)
- **Description**: Async session factory for creating database sessions
- **Location**: `/ainav-backend/shared/database.py:14-20`
- **Responsibilities**:
  - Bind sessions to async engine
  - Configure session behavior (autocommit=False, autoflush=False)
  - Expire objects after commit (for fresh reads)

#### `get_async_session()` (database.py)
- **Description**: FastAPI dependency function for async database session injection
- **Signature**: `async def get_async_session() -> AsyncSession`
- **Location**: `/ainav-backend/shared/database.py:23-27`
- **Dependencies**: Depends on SQLAlchemy `AsyncSession`, `SessionLocal` factory
- **Usage**: Used as FastAPI Depends() parameter in route handlers for transactional database access

### Object-Relational Mapping

#### `TimestampMixin` (models.py)
- **Description**: Mixin class providing automatic timestamp tracking for all entities
- **Location**: `/ainav-backend/shared/models.py:12-15`
- **Attributes**:
  - `created_at: Column[DateTime(timezone=True)]` - Record creation timestamp (server-side default: now())
  - `updated_at: Column[DateTime(timezone=True)]` - Last update timestamp (server-side default: now(), auto-update: func.now())

#### `User` (models.py)
- **Description**: User account model for authentication and authorization
- **Location**: `/ainav-backend/shared/models.py:31-52`
- **Table**: `users`
- **Primary Key**: `id: UUID`
- **Attributes**:
  - `email: String(255)` - Email address (unique, indexed)
  - `phone: String(20)` - Phone number (unique, indexed, nullable)
  - `username: String(50)` - Username (unique, indexed)
  - `hashed_password: String(255)` - Bcrypt-hashed password
  - `is_active: Boolean` - Account activation status (default: True)
  - `is_superuser: Boolean` - Admin privilege flag (default: False)
  - `github_id: String(50)` - GitHub OAuth provider ID (unique, nullable)
  - `wechat_id: String(50)` - WeChat OAuth provider ID (unique, nullable)
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `workflows: relationship[AgentWorkflow]` - User-created agent workflows (back_populates: user)
  - `interactions: relationship[UserInteraction]` - User action tracking (cascade: all, delete-orphan)

#### `Category` (models.py)
- **Description**: Tool categorization model for organizing AI tools
- **Location**: `/ainav-backend/shared/models.py:55-65`
- **Table**: `categories`
- **Primary Key**: `id: UUID`
- **Attributes**:
  - `name: String(100)` - Category display name
  - `slug: String(100)` - URL-safe identifier (unique, indexed)
  - `description: Text` - Category description
  - `icon: String(255)` - Icon reference (emoji or icon name)
  - `order: Integer` - Display ordering (default: 0)
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `tools: relationship[Tool]` - Tools in this category (back_populates: category)

#### `Scenario` (models.py)
- **Description**: Use case scenarios for AI tool discovery and workflow creation
- **Location**: `/ainav-backend/shared/models.py:68-75`
- **Table**: `scenarios`
- **Primary Key**: `id: UUID`
- **Attributes**:
  - `name: String(100)` - Scenario name
  - `slug: String(100)` - URL-safe identifier (unique, indexed)
  - `icon: String(255)` - Icon reference
  - Inherits: `TimestampMixin` (created_at, updated_at)

#### `Tool` (models.py)
- **Description**: AI tool registry with metadata, pricing, accessibility, and API capabilities
- **Location**: `/ainav-backend/shared/models.py:78-104`
- **Table**: `tools`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `category_id: UUID` -> Categories.id
- **Attributes**:
  - `name: String(255)` - English tool name
  - `name_zh: String(255)` - Chinese tool name (nullable)
  - `description_zh: Text` - Chinese description (nullable)
  - `slug: String(255)` - URL-safe identifier (unique, indexed)
  - `description: Text` - English description
  - `url: String(512)` - Official tool URL
  - `logo_url: String(512)` - Logo image URL (nullable)
  - `pricing_type: String(50)` - Pricing model (free/freemium/paid)
  - `is_china_accessible: Boolean` - China accessibility flag (default: True)
  - `requires_vpn: Boolean` - VPN requirement flag (default: False)
  - `avg_rating: Float` - Average user rating (default: 0.0)
  - `review_count: Integer` - Total review count (default: 0)
  - `github_stars: Integer` - GitHub star count (default: 0)
  - `has_api: Boolean` - API availability flag (default: False)
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `category: relationship[Category]` - Parent category (back_populates: tools)
  - `scenarios: relationship[Scenario]` - Related use case scenarios (secondary: tool_scenarios)
  - `skills: relationship[Skill]` - Tool API capabilities (back_populates: tool, cascade: all, delete-orphan)

#### `tool_scenarios` (models.py)
- **Description**: Junction table for many-to-many relationship between tools and scenarios
- **Location**: `/ainav-backend/shared/models.py:18-24`
- **Columns**:
  - `tool_id: UUID` (FK -> tools.id, primary_key)
  - `scenario_id: UUID` (FK -> scenarios.id, primary_key)

#### `Skill` (models.py)
- **Description**: Tool API capability abstraction for agent system integration
- **Location**: `/ainav-backend/shared/models.py:109-154`
- **Table**: `skills`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `tool_id: UUID` -> Tools.id (required)
- **Attributes**:
  - `name: String(100)` - Skill name (e.g., "Search GitHub Repos")
  - `name_zh: String(100)` - Chinese skill name (nullable)
  - `slug: String(100)` - URL-safe identifier (indexed)
  - `description: Text` - Skill description
  - `description_zh: Text` - Chinese description (nullable)
  - `api_endpoint: String(512)` - API endpoint URL (nullable)
  - `http_method: String(10)` - HTTP verb (GET, POST, PUT, DELETE, PATCH)
  - `input_schema: JSON` - JSON Schema for request parameters
  - `output_schema: JSON` - JSON Schema for response data
  - `headers_template: JSON` - Header configuration template
  - `auth_type: String(50)` - Authentication method (api_key/oauth2/bearer/none, default: none)
  - `auth_config: JSON` - Auth configuration ({header, prefix, env_var})
  - `is_active: Boolean` - Activation status (default: True)
  - `usage_count: Integer` - Invocation counter (default: 0)
  - `avg_latency_ms: Float` - Average API response time (default: 0.0)
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `tool: relationship[Tool]` - Parent tool (back_populates: skills)

#### `AgentWorkflow` (models.py)
- **Description**: User-created agent workflow blueprints stored as React Flow graph definitions
- **Location**: `/ainav-backend/shared/models.py:157-217`
- **Table**: `agent_workflows`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `user_id: UUID` -> Users.id (required)
  - `forked_from_id: UUID` -> AgentWorkflows.id (self-referential, nullable)
- **Attributes**:
  - `name: String(255)` - Workflow name
  - `name_zh: String(255)` - Chinese workflow name (nullable)
  - `slug: String(255)` - URL-safe identifier (unique, indexed)
  - `description: Text` - Workflow description
  - `description_zh: Text` - Chinese description (nullable)
  - `icon: String(100)` - Emoji or icon name
  - `graph_json: JSON` - React Flow graph definition ({nodes: [], edges: [], viewport: {}})
  - `trigger_type: String(50)` - Execution trigger (manual/schedule/webhook, default: manual)
  - `trigger_config: JSON` - Trigger configuration ({cron, webhook_secret, etc})
  - `input_schema: JSON` - Expected workflow input schema
  - `llm_model: String(100)` - LLM model selector (default: deepseek-chat)
  - `system_prompt: Text` - System-level prompt for agent
  - `temperature: Float` - LLM temperature setting (default: 0.7)
  - `is_public: Boolean` - Public sharing flag (default: False)
  - `is_template: Boolean` - Template flag for reusability (default: False)
  - `fork_count: Integer` - Number of forks (default: 0)
  - `run_count: Integer` - Total execution count (default: 0)
  - `star_count: Integer` - User star count (default: 0)
  - `version: Integer` - Workflow version (default: 1)
  - `version_history: JSON` - Changelog ({version, changes, timestamp})
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `user: relationship[User]` - Workflow owner (back_populates: workflows)
  - `executions: relationship[AgentExecution]` - Execution history (back_populates: workflow, cascade: all, delete-orphan)
  - `forked_from: relationship[AgentWorkflow]` - Origin workflow for forks (remote_side: [id])

#### `AgentExecution` (models.py)
- **Description**: Runtime execution logs for agent workflow invocations
- **Location**: `/ainav-backend/shared/models.py:220-260`
- **Table**: `agent_executions`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `workflow_id: UUID` -> AgentWorkflows.id (required)
  - `user_id: UUID` -> Users.id (required)
- **Attributes**:
  - `status: String(20)` - Execution status (pending/running/completed/failed/cancelled, default: pending)
  - `input_data: JSON` - Workflow input values
  - `output_data: JSON` - Workflow output result
  - `error_message: Text` - Error details on failure (nullable)
  - `execution_log: JSON` - Step-by-step trace ({node_id, status, input, output, duration_ms, timestamp})
  - `token_usage: Integer` - LLM token consumption (default: 0)
  - `total_api_calls: Integer` - External API call count (default: 0)
  - `duration_ms: Integer` - Total execution time in milliseconds
  - `trigger_type: String(50)` - Trigger method (manual/schedule/webhook/api)
  - `trigger_metadata: JSON` - Trigger context and additional info
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `workflow: relationship[AgentWorkflow]` - Parent workflow (back_populates: executions)

#### `AgentMemory` (models.py)
- **Description**: Long-term memory storage for RAG retrieval with vector embeddings
- **Location**: `/ainav-backend/shared/models.py:263-285`
- **Table**: `agent_memories`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `workflow_id: UUID` -> AgentWorkflows.id (required)
- **Attributes**:
  - `content: Text` - Memory content (required)
  - `content_type: String(50)` - Memory classification (conversation/document/fact/summary)
  - `meta_data: JSON` - Flexible metadata (source, timestamp, tags, etc.)
  - `embedding: Vector(384)` - pgvector embedding (384 dimensions from MiniLM-L12-v2)
- **Dependencies**: Uses pgvector extension for semantic search
- **Inherits**: `TimestampMixin` (created_at, updated_at)

#### `UserInteraction` (models.py)
- **Description**: User behavior tracking for personalization and analytics
- **Location**: `/ainav-backend/shared/models.py:288-316`
- **Table**: `user_interactions`
- **Primary Key**: `id: UUID`
- **Foreign Keys**:
  - `user_id: UUID` -> Users.id (required)
- **Attributes**:
  - `item_type: String(50)` - Target entity type (tool/agent/roadmap)
  - `item_id: UUID` - Target entity identifier
  - `action: String(50)` - Action type (view/click/run/like/fork)
  - `weight: Float` - Interaction importance (default: 1.0)
  - `meta_data: JSON` - Context ({search_query, referral, etc})
  - Inherits: `TimestampMixin` (created_at, updated_at)
- **Relationships**:
  - `user: relationship[User]` - Acting user (back_populates: interactions)

### Email Service

#### `EmailService` (email.py)
- **Description**: Transactional email service with HTML/plain-text templates and security features
- **Location**: `/ainav-backend/shared/email.py:28-80`
- **Responsibilities**:
  - Send transactional emails via SMTP
  - Generate secure password reset emails with token links
  - Generate welcome emails for new users
  - HTML escape user content to prevent XSS
  - URL-encode tokens for safe inclusion in URLs
  - Support multiple SMTP configurations (SSL/TLS)

**Key Methods**:

- `__init__()`
  - **Description**: Initialize email service with SMTP configuration from settings
  - **Location**: Line 32-39
  - **Dependencies**: Reads from `settings` singleton (config.py)

- `is_configured() -> bool`
  - **Description**: Validate that required email credentials are set
  - **Signature**: `is_configured() -> bool`
  - **Location**: Line 41-43
  - **Returns**: True if SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL are configured

- `_create_smtp_connection()`
  - **Description**: Create SMTP connection with SSL/TLS configuration
  - **Signature**: `_create_smtp_connection() -> smtplib.SMTP | smtplib.SMTP_SSL`
  - **Location**: Line 45-55
  - **Dependencies**: Python stdlib smtplib, ssl modules

- `send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str], cc: Optional[List[str]], bcc: Optional[List[str]]) -> bool`
  - **Description**: Send multipart email with HTML and plain-text versions
  - **Signature**: `send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None, cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> bool`
  - **Location**: Line 57-101
  - **Parameters**:
    - `to_email`: Recipient address
    - `subject`: Email subject
    - `html_content`: HTML email body
    - `text_content`: Plain-text fallback (optional)
    - `cc`: CC recipients list (optional)
    - `bcc`: BCC recipients list (optional)
  - **Returns**: True on successful send, False on failure
  - **Error Handling**: Catches SMTPAuthenticationError, SMTPException, and generic Exception
  - **Logging**: Logs success and error details

- `send_password_reset_email(to_email: str, reset_token: str) -> bool`
  - **Description**: Send password reset email with token-based reset URL
  - **Signature**: `send_password_reset_email(to_email: str, reset_token: str) -> bool`
  - **Location**: Line 103-161
  - **Parameters**:
    - `to_email`: User's email address
    - `reset_token`: URL-safe reset token
  - **Returns**: True if email sent successfully
  - **Security**:
    - URL-encodes token for safe URL inclusion
    - HTML-escapes URL in email body
    - Includes note about 1-hour expiration
  - **Languages**: Provides Chinese templates (subject, HTML, plain-text)

- `send_welcome_email(to_email: str, username: str) -> bool`
  - **Description**: Send welcome email to new registered users
  - **Signature**: `send_welcome_email(to_email: str, username: str) -> bool`
  - **Location**: Line 163-242
  - **Parameters**:
    - `to_email`: User's email address
    - `username`: User's username
  - **Returns**: True if email sent successfully
  - **Security**: HTML-escapes username to prevent XSS
  - **Features**: Lists platform features with emojis and formatted sections
  - **Languages**: Provides Chinese templates

**Singleton Instance**: `email_service` (line 245)

**Helper Functions**:

- `escape_html(text: str) -> str` (line 20-22)
  - HTML-escapes special characters to prevent XSS injection
  - Uses Python's built-in `html.escape()`

- `escape_url_param(text: str) -> str` (line 25-27)
  - URL-encodes parameter for safe inclusion in URLs
  - Uses `urllib.parse.quote()`

### Embedding Service

#### `EmbeddingService` (embedding.py)
- **Description**: Vector embedding generation for semantic search and RAG using sentence-transformers
- **Location**: `/ainav-backend/shared/embedding.py:1-43`
- **Model**: BAAI/bge-small-zh-v1.5 (Chinese-optimized, 384-dimensional embeddings)
- **Responsibilities**:
  - Load multilingual embedding model on first use
  - Generate 384-dimensional vector embeddings from text
  - Support semantic similarity search for RAG memory retrieval
  - Cache model instance (singleton pattern)

**Key Attributes**:

- `MODEL_NAME: str` (line 8)
  - Value: "BAAI/bge-small-zh-v1.5"
  - Description: Lightweight multilingual embedding model optimized for Chinese and English

**Key Methods**:

- `__new__(cls)`
  - **Description**: Implement singleton pattern for embedding service
  - **Location**: Line 13-17
  - **Pattern**: Returns same instance across application

- `initialize()`
  - **Description**: Load embedding model from huggingface on first access
  - **Signature**: `initialize() -> None`
  - **Location**: Line 19-27
  - **Dependencies**: sentence_transformers.SentenceTransformer
  - **Error Handling**: Catches and logs exceptions during model loading
  - **Caching**: Model cached via SENTENCE_TRANSFORMERS_HOME env var

- `generate_embedding(text: str) -> list[float]`
  - **Description**: Generate 384-dimensional embedding from text input
  - **Signature**: `generate_embedding(text: str) -> list[float]`
  - **Location**: Line 29-35
  - **Parameters**:
    - `text`: Input text to embed
  - **Returns**: List of 384 float values representing semantic vector
  - **Processing**: Normalizes embeddings to unit length (normalize_embeddings=True)
  - **Lazy Loading**: Initializes model on first invocation

**Singleton Instance**: `embedding_service` (line 37)

**Dependencies**:
- sentence-transformers library
- Huggingface transformers framework
- torch (PyTorch) for model inference

## Dependencies

### Internal Dependencies

- None directly within shared module (provides shared utilities for other services)

### External Dependencies

**Core Database & ORM**:
- `sqlalchemy` (2.0+) - SQL toolkit and ORM
  - `sqlalchemy.ext.asyncio` - Async engine and session management
  - `sqlalchemy.ext.declarative` - Declarative base and mixins
  - `sqlalchemy.dialects.postgresql` - PostgreSQL-specific types (JSON, UUID)
  - `sqlalchemy.orm` - Relationship management
- `pgvector` - PostgreSQL vector extension for embeddings
  - `pgvector.sqlalchemy` - SQLAlchemy integration (Vector type)
- `asyncpg` - PostgreSQL async driver
- `PostgreSQL` 16+ with pgvector extension

**Configuration & Settings**:
- `pydantic-settings` - Environment-based settings management

**Email & SMTP**:
- Python stdlib `smtplib` - SMTP protocol
- Python stdlib `ssl` - SSL/TLS encryption
- Python stdlib `email` - Email message construction

**Embeddings & NLP**:
- `sentence-transformers` - Sentence/text embedding generation
- `torch` (PyTorch) - Deep learning framework
- Huggingface transformers - Pretrained model loading

**Utilities**:
- Python stdlib `uuid` - UUID generation
- Python stdlib `html` - HTML escaping
- Python stdlib `logging` - Structured logging
- Python stdlib `urllib.parse` - URL encoding

**Integration Services**:
- PostgreSQL database (async connection)
- Redis cache (referenced in config, used by other services)
- Meilisearch search engine (referenced in config)
- DeepSeek LLM API (referenced in config)
- GitHub OAuth API (referenced in config)
- WeChat OAuth API (referenced in config)

## Relationships Diagram

```mermaid
---
title: C4 Code Diagram - Shared Database Models & Services
---
classDiagram
    namespace Models {
        class TimestampMixin {
            <<mixin>>
            +created_at DateTime
            +updated_at DateTime
        }

        class User {
            +id UUID
            +email String~unique~
            +phone String~unique~
            +username String~unique~
            +hashed_password String
            +is_active Boolean
            +is_superuser Boolean
            +github_id String~unique~
            +wechat_id String~unique~
            +workflows List~AgentWorkflow~
            +interactions List~UserInteraction~
        }

        class Category {
            +id UUID
            +name String
            +slug String~unique~
            +description Text
            +icon String
            +order Integer
            +tools List~Tool~
        }

        class Scenario {
            +id UUID
            +name String
            +slug String~unique~
            +icon String
        }

        class Tool {
            +id UUID
            +name String
            +name_zh String
            +slug String~unique~
            +description Text
            +url String
            +logo_url String
            +pricing_type String
            +category_id UUID
            +is_china_accessible Boolean
            +requires_vpn Boolean
            +avg_rating Float
            +review_count Integer
            +github_stars Integer
            +has_api Boolean
            +category Category
            +scenarios List~Scenario~
            +skills List~Skill~
        }

        class Skill {
            +id UUID
            +tool_id UUID
            +name String
            +slug String
            +api_endpoint String
            +http_method String
            +input_schema JSON
            +output_schema JSON
            +auth_type String
            +auth_config JSON
            +is_active Boolean
            +usage_count Integer
            +avg_latency_ms Float
            +tool Tool
        }

        class AgentWorkflow {
            +id UUID
            +user_id UUID
            +name String
            +slug String~unique~
            +description Text
            +graph_json JSON
            +trigger_type String
            +trigger_config JSON
            +llm_model String
            +system_prompt Text
            +temperature Float
            +is_public Boolean
            +is_template Boolean
            +version Integer
            +version_history JSON
            +run_count Integer
            +star_count Integer
            +user User
            +executions List~AgentExecution~
            +forked_from AgentWorkflow
        }

        class AgentExecution {
            +id UUID
            +workflow_id UUID
            +user_id UUID
            +status String
            +input_data JSON
            +output_data JSON
            +error_message Text
            +execution_log JSON
            +token_usage Integer
            +total_api_calls Integer
            +duration_ms Integer
            +trigger_type String
            +workflow AgentWorkflow
        }

        class AgentMemory {
            +id UUID
            +workflow_id UUID
            +content Text
            +content_type String
            +meta_data JSON
            +embedding Vector~384~
        }

        class UserInteraction {
            +id UUID
            +user_id UUID
            +item_type String
            +item_id UUID
            +action String
            +weight Float
            +meta_data JSON
            +user User
        }
    }

    namespace Services {
        class Settings {
            <<pydantic BaseSettings>>
            +DATABASE_URL String
            +REDIS_URL String
            +MEILISEARCH_URL String
            +SECRET_KEY String
            +SMTP_HOST String
            +SMTP_PORT Integer
            +DEEPSEEK_API_KEY String
            +validate_security_settings()
            +get_utc_now() DateTime
        }

        class DatabaseSession {
            <<management>>
            +engine AsyncEngine
            +SessionLocal AsyncSessionMaker
            +get_async_session() AsyncSession
        }

        class EmailService {
            +host String
            +port Integer
            +user String
            +password String
            +is_configured() Boolean
            +send_email(to, subject, html, text) Boolean
            +send_password_reset_email(email, token) Boolean
            +send_welcome_email(email, username) Boolean
            -_create_smtp_connection() SMTP
        }

        class EmbeddingService {
            <<singleton>>
            +MODEL_NAME String
            +initialize() void
            +generate_embedding(text) List~float~
        }
    }

    namespace Database {
        class PostgreSQL_Database {
            <<external>>
            +pgvector extension
            +async connection pool
        }

        class Redis_Cache {
            <<external>>
            +cache layer
        }
    }

    %% Relationships between models
    User --|> TimestampMixin
    Category --|> TimestampMixin
    Scenario --|> TimestampMixin
    Tool --|> TimestampMixin
    Skill --|> TimestampMixin
    AgentWorkflow --|> TimestampMixin
    AgentExecution --|> TimestampMixin
    AgentMemory --|> TimestampMixin
    UserInteraction --|> TimestampMixin

    Tool --> Category : belongs_to
    Tool --> Scenario : relates_to
    Tool --> Skill : exposes

    User --> AgentWorkflow : creates
    AgentWorkflow --> AgentExecution : executes_as
    AgentWorkflow --> AgentMemory : stores_memories_in
    AgentWorkflow --> AgentWorkflow : forks_from

    User --> UserInteraction : performs

    AgentExecution --> User : belongs_to

    %% Service relationships
    Settings -.-> DatabaseSession : configures
    DatabaseSession -.-> PostgreSQL_Database : connects_to
    EmailService -.-> Settings : reads_from
    EmbeddingService -.-> PostgreSQL_Database : stores_vectors_in

    DatabaseSession -.-> User : maps
    DatabaseSession -.-> Category : maps
    DatabaseSession -.-> Tool : maps
    DatabaseSession -.-> Skill : maps
    DatabaseSession -.-> AgentWorkflow : maps
    DatabaseSession -.-> AgentExecution : maps
    DatabaseSession -.-> AgentMemory : maps
    DatabaseSession -.-> UserInteraction : maps
```

## Database Schema Summary

**Tables Created** (9 core tables + 1 junction table):
1. `users` - User accounts with OAuth support
2. `categories` - Tool categories
3. `scenarios` - Use case scenarios
4. `tools` - AI tool registry
5. `tool_scenarios` - Many-to-many junction table
6. `skills` - Tool API capabilities
7. `agent_workflows` - Workflow blueprints
8. `agent_executions` - Workflow execution logs
9. `agent_memories` - RAG memory with vector embeddings
10. `user_interactions` - User behavior tracking

**Key Indexes**:
- `users.email`, `users.username`, `users.github_id`, `users.wechat_id` (unique, indexed)
- `categories.slug` (unique, indexed)
- `scenarios.slug` (unique, indexed)
- `tools.slug`, `tools.category_id` (indexed)
- `skills.slug`, `skills.tool_id` (indexed)
- `agent_workflows.slug`, `agent_workflows.user_id` (unique/indexed)
- `agent_executions.workflow_id`, `agent_executions.user_id` (indexed)
- `user_interactions.user_id`, `item_id`, `item_type` (indexed)

## Notes

### Security Features
- **Password Reset**: Uses time-limited tokens (1-hour expiration) with HTML escaping
- **XSS Prevention**: All user-provided content escaped before inclusion in email templates
- **URL Safety**: Reset tokens URL-encoded before inclusion in URLs
- **OAuth Support**: Dual OAuth providers (GitHub, WeChat) for authentication
- **JWT Configuration**: Separate access token (1-hour) and refresh token (7-day) TTL

### Performance Considerations
- **Async Database**: Uses SQLAlchemy async engine for non-blocking I/O
- **Vector Embeddings**: 384-dimensional vectors enable fast semantic similarity search
- **Connection Pooling**: pool_pre_ping=True ensures healthy connections
- **Lazy Model Loading**: EmbeddingService loads model only on first use

### Scalability Features
- **Pagination**: Configurable page sizes (default: 20, max: 100)
- **Versioning**: AgentWorkflow supports version history tracking
- **Fork Support**: Workflows can be forked and stars tracked for popularity
- **User Analytics**: UserInteraction captures behavior for personalization

### Production Checklist
- Set `SECRET_KEY` to 32+ character random string
- Set `ENVIRONMENT` to "production" and validate security settings
- Configure SMTP credentials (email service)
- Set OAuth credentials (GitHub, WeChat)
- Enable connection pooling for database
- Configure CORS_ORIGINS for frontend domain
- Update FRONTEND_URL for password reset links
