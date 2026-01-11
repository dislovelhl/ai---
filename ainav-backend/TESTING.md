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

## Test Files

### 1. `test_authentication.py` 🔧
**Automated Test Suite** - Comprehensive Python script that validates all authentication requirements.

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

- **Features:**
  - Color-coded output for easy reading
  - Detailed error reporting with response details
  - Automatic test user creation
  - Service health checks
  - Summary statistics

**Usage:**
```bash
python test_authentication.py
```

### 2. `AUTHENTICATION_TESTING_GUIDE.md` 📖
**Complete Manual Testing Guide** - Detailed documentation for manual testing.

- **What's Inside:**
  - Step-by-step cURL examples for every endpoint
  - Instructions for creating test users
  - How to obtain and use JWT tokens
  - Testing procedures for all three services
  - Troubleshooting common issues
  - Test results logging template

- **Use This When:**
  - You want to manually verify specific endpoints
  - You need to understand the authentication flow
  - You're debugging authentication issues
  - You want to test with custom data

### 3. `TEST_QUICK_START.md` 🚀
**Quick Reference Guide** - TL;DR version for developers.

- **What's Inside:**
  - Fastest way to run all tests
  - Common troubleshooting scenarios
  - Prerequisites and setup
  - CI/CD integration example
  - Service port reference

- **Use This When:**
  - You just want to run the tests quickly
  - You're setting up CI/CD
  - You need to troubleshoot test failures

### 4. `AUTHENTICATION_TEST_RESULTS.md` ✅
**Test Coverage Documentation** - Comprehensive record of what's been tested.

- **What's Inside:**
  - Detailed breakdown of all test cases
  - Coverage tables for each service
  - Acceptance criteria validation
  - Known limitations
  - Production deployment recommendations
  - Test sign-off documentation

- **Use This When:**
  - You need to verify test coverage
  - You're reviewing the implementation
  - You want to understand what's been tested
  - You're preparing for deployment

## Test Scenarios Covered

### Authentication Tests (401 Errors)
| Scenario | Tested | Services |
|----------|--------|----------|
| No Authorization header | ✅ | All |
| Invalid token format | ✅ | All |
| Expired token | ✅ | All |
| Malformed token | ✅ | All |

### Authorization Tests (403 Errors)
| Scenario | Tested | Services |
|----------|--------|----------|
| Regular user accessing admin endpoint | ✅ | Content |
| User accessing another user's private workflow | ✅ | Agent |
| User modifying another user's workflow | ✅ | Agent |
| User deleting another user's workflow | ✅ | Agent |

### Success Tests (200/201 Responses)
| Scenario | Tested | Services |
|----------|--------|----------|
| Valid token on user endpoints | ✅ | User |
| Valid token on workflow endpoints | ✅ | Agent |
| Valid token on execution endpoints | ✅ | Agent |
| Admin token on admin endpoints | ✅ | Content |
| Public read access (no auth) | ✅ | Content |

### Data Isolation Tests
| Scenario | Tested | Services |
|----------|--------|----------|
| Users only see their own workflows | ✅ | Agent |
| Users only see their own executions | ✅ | Agent |
| Users can see public workflows | ✅ | Agent |
| No cross-user data leakage | ✅ | All |

## Services Under Test

### User Service (Port 8003)
- `/v1/users/me` - Get current user profile
- `/v1/personalization/interactions` - Record user interactions
- `/v1/personalization/recommendations` - Get personalized recommendations

### Agent Service (Port 8005)
- `/v1/workflows/` - List/create workflows
- `/v1/workflows/{id}` - Get/update/delete specific workflow
- `/v1/executions/` - List executions
- `/v1/executions/{id}` - Get execution details

### Content Service (Port 8001)
- `/v1/tools/` - List/create tools (create requires admin)
- `/v1/tools/{id}` - Get/update/delete tool (write requires admin)
- `/v1/categories/` - List/create categories (create requires admin)
- `/v1/scenarios/` - List/create scenarios (create requires admin)

## Prerequisites

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Manual Service Start
```bash
# Terminal 1 - User Service
uvicorn services.user_service.app.main:app --reload --port 8003

# Terminal 2 - Agent Service
uvicorn services.agent_service.app.main:app --reload --port 8005

# Terminal 3 - Content Service
uvicorn services.content_service.app.main:app --reload --port 8001
```

### Database
```bash
# Run migrations
alembic upgrade head

# Create admin user (for admin tests)
docker exec -it $(docker ps -q -f name=postgres) psql -U ainav -d ainav_db \
  -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"
```

## Running Tests

### Automated Tests
```bash
cd ainav-backend
python test_authentication.py
```

**Expected Output:**
```
================================================================================
Authentication Testing Suite
================================================================================

Step 1: Service Health Checks
✓ PASS - User Service health check
✓ PASS - Agent Service health check
✓ PASS - Content Service health check

...

================================================================================
Test Summary
================================================================================

Total Tests: 45
Passed: 45
Failed: 0
```

### Manual Tests
See `AUTHENTICATION_TESTING_GUIDE.md` for detailed cURL examples.

### Interactive Tests (Swagger UI)
- User Service: http://localhost:8003/docs
- Agent Service: http://localhost:8005/docs
- Content Service: http://localhost:8001/docs

## Troubleshooting

### Tests Fail with Connection Errors
**Problem:** Services not running
```bash
docker-compose ps
docker-compose up -d
```

### Admin Tests Fail with 403
**Problem:** Admin user not configured
```bash
docker exec -it $(docker ps -q -f name=postgres) psql -U ainav -d ainav_db \
  -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"
```

### Token Errors
**Problem:** SECRET_KEY mismatch between services
```bash
# Check .env file
grep SECRET_KEY ainav-backend/.env

# Restart services
docker-compose restart
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run Authentication Tests
  run: |
    docker-compose up -d
    sleep 10  # Wait for services
    cd ainav-backend

    # Setup admin user
    docker exec postgres psql -U ainav -d ainav_db \
      -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"

    # Run tests
    python test_authentication.py
```

## Test Data Cleanup

Tests create persistent user accounts. To clean up:

```sql
-- Remove test users
DELETE FROM users WHERE email LIKE '%_auth@example.com';

-- Remove test workflows
DELETE FROM workflows WHERE name LIKE 'Test%';

-- Remove test data
DELETE FROM tools WHERE name LIKE 'Test%';
```

## Next Steps

After all tests pass:
1. ✅ Review test results in `AUTHENTICATION_TEST_RESULTS.md`
2. ✅ Verify all acceptance criteria are met
3. ✅ Update API documentation (next subtask)
4. ✅ Deploy to staging/production

## Support

- **Full Manual Guide:** `AUTHENTICATION_TESTING_GUIDE.md`
- **Quick Reference:** `TEST_QUICK_START.md`
- **Test Results:** `AUTHENTICATION_TEST_RESULTS.md`
- **Interactive API Docs:** http://localhost:8003/docs (and ports 8001, 8005)

## Summary

This testing suite provides comprehensive validation of:
- ✅ JWT authentication across all services
- ✅ Role-based authorization (admin vs regular users)
- ✅ Ownership enforcement (users can only access their own data)
- ✅ Data isolation (no cross-user leakage)
- ✅ Public vs private resource access

All acceptance criteria from the authentication middleware integration task have been verified and documented.
