# Testing Documentation

## Current Test Coverage Status

**Last Updated:** 2026-01-10
**Status:** Initial Baseline Established

### Coverage Summary

| Service | Files | Statements | Coverage | Priority |
|---------|-------|------------|----------|----------|
| **agent_service** | 21 | 2,037 | 0.0% | HIGH |
| **user_service** | 11 | 466 | 0.0% | HIGH |
| **automation_service** | 12 | 383 | 0.0% | MEDIUM |
| **content_service** | 6 | 181 | 0.0% | LOW |
| **search_service** | 3 | 10 | 0.0% | MEDIUM |
| **TOTAL** | **53** | **3,077** | **0.0%** | - |

### Existing Test Files

1. **tests/test_content_crud.py** (3 integration tests)
   - Tests: categories, scenarios, tools CRUD
   - Status: ⚠️ Requires running service on localhost:8000

2. **tests/test_automation.py** (2 integration tests)
   - Tests: health check, trigger crawl
   - Status: ⚠️ Requires running service on localhost:8004

3. **tests/test_github_client.py**
   - Status: ❌ Import error - needs fixing

### Testing Infrastructure

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

**In Progress:**
- ⏳ Test database setup (subtask 1.3)
- ⏳ Unit tests
- ⏳ CI/CD integration

### Coverage Goals

**Target:** ≥70% coverage for core modules

**Priority Modules:**
1. `shared/models.py` - Core data models (261 lines)
2. `user_service/app/routers/auth.py` - Authentication (140 stmts)
3. `agent_service/app/core/executor.py` - Execution engine (282 stmts)
4. `agent_service/app/engine/langgraph_engine.py` - LangGraph (339 stmts)
5. `agent_service/app/routers/workflows.py` - Workflow CRUD (174 stmts)

### Running Tests

```bash
# Run all tests (pytest.ini handles coverage automatically)
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_content_crud.py -v

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests

# Run tests with specific coverage output
pytest --cov-report=html    # Generate HTML coverage report
pytest --cov-report=term    # Terminal output only

# Run tests without coverage (faster for development)
pytest --no-cov

# Run specific test function
pytest tests/test_content_crud.py::test_categories_crud -v
```

### Using Test Fixtures

The `conftest.py` provides many useful fixtures:

**Database Fixtures:**
```python
async def test_create_user(db_session: AsyncSession):
    """Test using database session with automatic rollback."""
    user = User(username="test")
    db_session.add(user)
    await db_session.commit()
    # Changes automatically rolled back after test
```

**HTTP Client Fixtures:**
```python
async def test_api_endpoint(async_client: AsyncClient):
    """Test using async HTTP client."""
    response = await async_client.get("/v1/health")
    assert response.status_code == 200
```

**Mock Fixtures:**
```python
def test_with_mocks(mock_redis, mock_meilisearch, mock_celery):
    """Test using mocked external services."""
    mock_redis.get.return_value = "cached_value"
    # Your test code here
```

**Data Factories:**
```python
def test_create_category(category_factory, db_session):
    """Test using data factories."""
    category_data = category_factory(name="Custom Category")
    # Use category_data in your test
```

**Note:** Current integration tests require services to be running. Future unit tests will work in isolation with mocks.

### Next Steps

1. ✅ Setup pytest infrastructure (pytest.ini, conftest.py) - **COMPLETED**
2. Create test database configuration (subtask 1.3)
3. Implement unit tests for shared models
4. Add auth and JWT middleware tests
5. Implement workflow and execution engine tests
6. Setup CI/CD pipeline

### Pytest Configuration

**pytest.ini** includes:
- Automatic test discovery (`test_*.py` pattern)
- Coverage reporting for `services/` and `shared/`
- HTML and JSON coverage reports
- Test markers for categorization (unit, integration, slow, auth, etc.)
- Asyncio mode set to auto
- Strict marker and config validation

**conftest.py** provides:
- Database fixtures with transaction rollback
- Async HTTP client fixtures
- Mock fixtures for external services
- Data factory fixtures for common models
- Test environment configuration

---

For detailed coverage analysis, see `.auto-claude/specs/006-core-test-coverage-expansion/COVERAGE_BASELINE.md`
