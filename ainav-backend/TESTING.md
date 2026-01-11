# Backend Testing Documentation

This directory contains comprehensive testing tools for validating the authentication and authorization implementation across all backend services.

## Quick Start

```bash
# 1. Start all services
docker-compose up -d

# 2. Run authentication tests
cd ainav-backend
python test_authentication.py
```

## Test Coverage Status

**Last Updated:** 2026-01-10
**Status:** Initial Baseline Established

### Coverage Summary

| Service                | Files  | Statements | Coverage | Priority |
| ---------------------- | ------ | ---------- | -------- | -------- |
| **agent_service**      | 21     | 2,037      | 0.0%     | HIGH     |
| **user_service**       | 11     | 466        | 0.0%     | HIGH     |
| **automation_service** | 12     | 383        | 0.0%     | MEDIUM   |
| **content_service**    | 6      | 181        | 0.0%     | LOW      |
| **search_service**     | 3      | 10         | 0.0%     | MEDIUM   |
| **TOTAL**              | **53** | **3,077**  | **0.0%** | -        |

## Test Files

### Automated Test Suite

**`test_authentication.py`** - Comprehensive Python script that validates all authentication requirements.

- **45+ Test Cases** covering:

  - Authentication (401 errors for missing/invalid tokens)
  - Authorization (403 errors for insufficient permissions)
  - Ownership validation (users can only access their own data)
  - Admin privileges (admin-only endpoints)
  - User isolation (no cross-user data leakage)

- **Coverage:**
  - ✅ User Service (personalization, user profiles)
  - ✅ Agent Service (workflows, executions)
  - ✅ Content Service (tools, categories, scenarios)

### Existing Test Files

1. **tests/test_content_crud.py** (3 integration tests)

   - Tests: categories, scenarios, tools CRUD
   - Status: ⚠️ Requires running service on localhost:8000

2. **tests/test_automation.py** (2 integration tests)
   - Tests: health check, trigger crawl
   - Status: ⚠️ Requires running service on localhost:8004

### Documentation

- **`AUTHENTICATION_TESTING_GUIDE.md`** - Complete manual testing guide
- **`TEST_QUICK_START.md`** - Quick reference guide
- **`AUTHENTICATION_TEST_RESULTS.md`** - Test coverage documentation

## Test Scenarios Covered

### Authentication Tests (401 Errors)

| Scenario                | Tested | Services |
| ----------------------- | ------ | -------- |
| No Authorization header | ✅     | All      |
| Invalid token format    | ✅     | All      |
| Expired token           | ✅     | All      |
| Malformed token         | ✅     | All      |

### Authorization Tests (403 Errors)

| Scenario                                       | Tested | Services |
| ---------------------------------------------- | ------ | -------- |
| Regular user accessing admin endpoint          | ✅     | Content  |
| User accessing another user's private workflow | ✅     | Agent    |
| User modifying another user's workflow         | ✅     | Agent    |
| User deleting another user's workflow          | ✅     | Agent    |

### Success Tests (200/201 Responses)

| Scenario                           | Tested | Services |
| ---------------------------------- | ------ | -------- |
| Valid token on user endpoints      | ✅     | User     |
| Valid token on workflow endpoints  | ✅     | Agent    |
| Valid token on execution endpoints | ✅     | Agent    |
| Admin token on admin endpoints     | ✅     | Content  |
| Public read access (no auth)       | ✅     | Content  |

## Services Under Test

| Service         | Port | Endpoints                                            |
| --------------- | ---- | ---------------------------------------------------- |
| User Service    | 8003 | `/v1/users/me`, `/v1/personalization/*`              |
| Agent Service   | 8005 | `/v1/workflows/*`, `/v1/executions/*`                |
| Content Service | 8001 | `/v1/tools/*`, `/v1/categories/*`, `/v1/scenarios/*` |

## Testing Infrastructure

**Installed:**

- pytest 7.4.4
- pytest-cov 4.1.0
- pytest-asyncio 0.23.0
- pytest-mock 3.12.0

**Configured:**

- ✅ pytest.ini configuration with coverage settings
- ✅ conftest.py with shared fixtures
- ✅ .coveragerc for coverage reporting
- ✅ Test environment setup
- ✅ Async testing support
- ✅ Mock fixtures for Redis, Meilisearch, Celery, LLM

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_content_crud.py -v

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests

# Run tests with coverage report
pytest --cov-report=html

# Run tests without coverage (faster)
pytest --no-cov
```

## Troubleshooting

### Tests Fail with Connection Errors

```bash
docker-compose ps
docker-compose up -d
```

### Admin Tests Fail with 403

```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U ainav -d ainav_db \
  -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"
```

## Coverage Goals

**Target:** ≥70% coverage for core modules

**Priority Modules:**

1. `shared/models.py` - Core data models (261 lines)
2. `user_service/app/routers/auth.py` - Authentication (140 stmts)
3. `agent_service/app/core/executor.py` - Execution engine (282 stmts)
4. `agent_service/app/engine/langgraph_engine.py` - LangGraph (339 stmts)
5. `agent_service/app/routers/workflows.py` - Workflow CRUD (174 stmts)

---

For detailed coverage analysis, see `.auto-claude/specs/006-core-test-coverage-expansion/COVERAGE_BASELINE.md`
