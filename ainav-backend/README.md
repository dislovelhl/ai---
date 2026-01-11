# AI Navigation Backend (ainav-backend)

Backend microservices for the AI Navigation Platform - an AI tool directory and agentic platform for the Chinese market.

## Architecture Overview

This backend is built as a microservices architecture with five core services:

| Service | Port | Purpose | Authentication |
|---------|------|---------|----------------|
| **Content Service** | 8001 | Tool & category CRUD | Public read, Admin write |
| **Search Service** | 8002 | Meilisearch full-text search | Public |
| **User Service** | 8003 | Auth & user profiles (JWT) | Public registration, Protected profile |
| **Automation Service** | 8004 | GitHub/ProductHunt crawlers | Internal |
| **Agent Service** | 8005 | LangGraph workflow orchestration | User-scoped |

### Infrastructure

- **PostgreSQL 16** (Port 5433) - Primary database with pgvector for embeddings
- **Redis** (Port 6379) - Cache & Celery message broker
- **Meilisearch** (Port 7700) - Full-text search engine

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 (if running without Docker)

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

**Required environment variables:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://ainav:ainavpassword@localhost:5433/ainav_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Search
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=masterKey

# Security (CRITICAL for production)
SECRET_KEY=your_32_char_minimum_secret_key  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
ENVIRONMENT=development  # Set to 'production' for prod

# Agent LLM
DEEPSEEK_API_KEY=your_deepseek_api_key

# CORS (update for production)
CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_URL=http://localhost:3000
```

### 3. Start Services (Docker)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f user_service
docker-compose logs -f agent_service
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Seed Initial Data (Optional)

```bash
# Seed AI tools and categories
python seed_tools.py

# Seed sample agent workflows
python seed_agents.py
```

## Development

### Running Services Individually

If you prefer to run services without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run individual services (from ainav-backend directory)
uvicorn services.user_service.app.main:app --reload --port 8003
uvicorn services.agent_service.app.main:app --reload --port 8005
uvicorn services.content_service.app.main:app --reload --port 8001
uvicorn services.search_service.app.main:app --reload --port 8002

# Run Celery worker (for automation tasks)
celery -A services.automation_service.app.celery_app worker --loglevel=info

# Run Celery beat (for scheduled tasks)
celery -A services.automation_service.app.celery_app beat --loglevel=info
```

### Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description of changes"

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

## Authentication & Authorization

All backend services use **JWT (JSON Web Token)** authentication. The system supports:

- **User authentication** - JWT tokens for regular users
- **Admin authorization** - Role-based access control for content management
- **OAuth2 social login** - GitHub and WeChat integration (optional)

### Authentication Flow

```
1. User registers → POST /v1/auth/register
2. User logs in → POST /v1/auth/login → Returns access_token
3. Client stores token → Include in subsequent requests
4. Protected endpoints validate token → Require: Authorization: Bearer <token>
```

### Token Lifecycle

- **Access Token**: Expires in 60 minutes
- **Refresh Token**: Expires in 7 days
- **Token Format**: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### Creating Users

**Regular User:**
```bash
curl -X POST http://localhost:8003/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "Test1234!",
    "full_name": "Test User"
  }'
```

**Admin User** (requires database update):
```bash
# 1. Create user via registration
curl -X POST http://localhost:8003/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminuser",
    "email": "admin@example.com",
    "password": "Admin1234!",
    "full_name": "Admin User"
  }'

# 2. Grant admin privileges
psql -h localhost -p 5433 -U ainav -d ainav_db
UPDATE users SET is_superuser = true WHERE username = 'adminuser';
\q
```

### Getting Access Tokens

```bash
# Login
curl -X POST http://localhost:8003/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test1234!"

# Response includes access_token
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Protected Endpoints

All protected endpoints require the `Authorization` header:

```bash
# Example: Get current user profile
curl -X GET http://localhost:8003/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Example: Create a workflow
curl -X POST http://localhost:8005/v1/workflows/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Workflow",
    "description": "Automated data pipeline",
    "graph_json": {"nodes": [], "edges": []},
    "is_public": false
  }'
```

## API Documentation (Swagger UI)

All services provide interactive OpenAPI documentation with **built-in authentication support**.

### Accessing Swagger UI

- **User Service**: http://localhost:8003/docs
- **Agent Service**: http://localhost:8005/docs
- **Content Service**: http://localhost:8001/docs
- **Search Service**: http://localhost:8002/docs

### Using Swagger UI with Authentication

1. **Navigate to any service's `/docs` endpoint**
   - Example: http://localhost:8005/docs

2. **Click the "Authorize" button** (🔒 lock icon in top right corner)

3. **Enter your access token:**
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   - You can paste the full token with or without the "Bearer " prefix
   - Swagger UI will add "Bearer " automatically if missing

4. **Click "Authorize"** to save the token

5. **Test protected endpoints:**
   - Protected endpoints now display a closed lock icon 🔒
   - Click "Try it out" and execute requests
   - The Authorization header is automatically included

6. **Logout** by clicking "Authorize" again and then "Logout"

### Understanding Security Indicators in Swagger UI

- 🔓 **Open lock** - Public endpoint, no authentication required
- 🔒 **Closed lock** - Protected endpoint, requires valid JWT token
- 🔒🔑 **Lock with key** - Admin-only endpoint, requires admin user token

### Testing Authentication Flows

See [AUTHENTICATION_TESTING_GUIDE.md](./AUTHENTICATION_TESTING_GUIDE.md) for comprehensive testing instructions including:
- Automated test suite
- Manual cURL examples
- Expected responses for all scenarios
- Troubleshooting guide

## Service-Specific Details

### User Service (Port 8003)

**Endpoints:**
- `POST /v1/auth/register` - Create new user account
- `POST /v1/auth/login` - Authenticate and get JWT token
- `GET /v1/users/me` - Get current user profile (requires auth)
- `PUT /v1/users/me` - Update profile (requires auth)
- `POST /v1/personalization/interactions` - Record user interactions (requires auth)
- `GET /v1/personalization/recommendations` - Get AI recommendations (requires auth)

### Agent Service (Port 8005)

**Endpoints:**
- `GET /v1/workflows/` - List workflows (requires auth, returns user's + public)
- `POST /v1/workflows/` - Create workflow (requires auth)
- `GET /v1/workflows/{id}` - Get workflow details (requires auth + ownership check)
- `PUT /v1/workflows/{id}` - Update workflow (requires auth + ownership)
- `DELETE /v1/workflows/{id}` - Delete workflow (requires auth + ownership)
- `POST /v1/executions/run` - Execute workflow (requires auth)
- `GET /v1/executions/` - List executions (requires auth, user-scoped)

### Content Service (Port 8001)

**Public Read Endpoints:**
- `GET /v1/tools/` - List all AI tools
- `GET /v1/tools/{id}` - Get tool details
- `GET /v1/categories/` - List categories
- `GET /v1/scenarios/` - List usage scenarios

**Admin-Only Write Endpoints:**
- `POST /v1/tools/` - Create tool (requires admin)
- `PUT /v1/tools/{id}` - Update tool (requires admin)
- `DELETE /v1/tools/{id}` - Delete tool (requires admin)
- `POST /v1/categories/` - Create category (requires admin)
- `PUT /v1/categories/{id}` - Update category (requires admin)
- `DELETE /v1/categories/{id}` - Delete category (requires admin)

## Security Best Practices

### Development
- Use `.env` file for secrets (never commit to git)
- Use different `SECRET_KEY` for each environment
- Keep dependencies updated: `pip install -r requirements.txt --upgrade`

### Production
1. **Generate a strong SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Set environment to production:**
   ```bash
   ENVIRONMENT=production
   ```

3. **Configure CORS for your frontend domain:**
   ```bash
   CORS_ORIGINS=["https://your-production-domain.com"]
   ```

4. **Use HTTPS** to prevent token interception

5. **Enable rate limiting** on authentication endpoints (already configured):
   - Login: 5 attempts per minute
   - Password reset: 3 attempts per 5 minutes

6. **Monitor logs** for suspicious authentication attempts

## Troubleshooting

### Service Won't Start

```bash
# Check if port is already in use
lsof -i :8003

# View service logs
docker-compose logs -f user_service

# Restart all services
docker-compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify DATABASE_URL in .env
# Ensure migrations are applied
alembic upgrade head
```

### Authentication Errors

**401 Unauthorized:**
- Token is missing, invalid, or expired
- Solution: Login again to get a fresh token

**403 Forbidden:**
- User lacks required permissions (e.g., non-admin trying to create tools)
- Solution: Verify user role in database or use appropriate account

**Token Expiration:**
- Tokens expire after 60 minutes
- Solution: Re-authenticate or implement token refresh logic

### Admin Endpoints Return 403

```bash
# Verify user has admin privileges
psql -h localhost -p 5433 -U ainav -d ainav_db
SELECT username, is_superuser FROM users WHERE username = 'your_username';

# Grant admin if needed
UPDATE users SET is_superuser = true WHERE username = 'your_username';
```

## Testing

### Automated Authentication Tests

Run the comprehensive test suite:

```bash
cd ainav-backend
python test_authentication.py
```

This tests:
- ✓ All services are running
- ✓ Protected endpoints reject requests without tokens (401)
- ✓ Protected endpoints reject invalid tokens (401)
- ✓ Protected endpoints accept valid tokens (200/201)
- ✓ Admin endpoints reject non-admin users (403)
- ✓ Ownership checks work correctly (403 for wrong user)

### Manual Testing

See [AUTHENTICATION_TESTING_GUIDE.md](./AUTHENTICATION_TESTING_GUIDE.md) for detailed cURL examples and Swagger UI testing instructions.

## Project Structure

```
ainav-backend/
├── services/
│   ├── agent_service/          # LangGraph workflows, skills, executions
│   │   ├── app/
│   │   │   ├── main.py        # FastAPI app
│   │   │   ├── dependencies.py # JWT auth dependencies
│   │   │   ├── routers/       # API endpoints
│   │   │   ├── core/          # LangGraph execution engine
│   │   │   └── engine/        # Workflow processing
│   │   └── tests/
│   ├── automation_service/     # Celery tasks, content crawlers
│   │   ├── app/
│   │   │   ├── celery_app.py  # Celery configuration
│   │   │   ├── tasks/         # Scheduled tasks
│   │   │   └── clients/       # API clients (GitHub, ProductHunt)
│   │   └── tests/
│   ├── content_service/        # Tools, categories, scenarios
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── dependencies.py # JWT + admin auth
│   │   │   └── routers/
│   │   └── tests/
│   ├── search_service/         # Meilisearch integration
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   └── routers/
│   │   └── tests/
│   └── user_service/           # Authentication, user management
│       ├── app/
│       │   ├── main.py
│       │   ├── dependencies.py # JWT auth
│       │   ├── routers/       # auth, users, personalization
│       │   └── utils/         # Password hashing, JWT utils
│       └── tests/
├── shared/
│   ├── models.py              # SQLAlchemy ORM models (shared)
│   ├── database.py            # Async DB connection
│   └── config.py              # Pydantic settings
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                     # Integration tests
├── requirements.txt           # Python dependencies
├── alembic.ini               # Alembic configuration
├── .env.example              # Environment template
└── README.md                 # This file
```

## Technology Stack

- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 16 + pgvector
- **Cache**: Redis 7.2
- **Search**: Meilisearch 1.5
- **Task Queue**: Celery 5.3
- **Agent Framework**: LangGraph 0.0.25
- **Authentication**: python-jose (JWT), passlib (bcrypt)

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and small

### Commit Messages
- Use descriptive commit messages
- Prefix with service name for service-specific changes
  - Example: `user_service: Add password reset endpoint`

### Testing
- Write tests for new endpoints
- Ensure authentication tests pass
- Test both success and error cases

## Additional Resources

- **Full Testing Guide**: [AUTHENTICATION_TESTING_GUIDE.md](./AUTHENTICATION_TESTING_GUIDE.md)
- **Test Results**: [AUTHENTICATION_TEST_RESULTS.md](./AUTHENTICATION_TEST_RESULTS.md)
- **Quick Start Testing**: [TEST_QUICK_START.md](./TEST_QUICK_START.md)
- **Main Project Guide**: [../CLAUDE.md](../CLAUDE.md)
- **API Specification**: [../design-specs/api-specification.md](../design-specs/api-specification.md)
- **Database Schema**: [../design-specs/database-schema.md](../design-specs/database-schema.md)

## License

[Add your license here]

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the testing guides
3. Check service logs: `docker-compose logs -f <service_name>`
4. Open an issue in the project repository
