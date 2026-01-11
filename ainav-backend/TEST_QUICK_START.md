# Authentication Testing - Quick Start

## TL;DR - Run All Tests

```bash
# 1. Start services (if not already running)
docker-compose up -d

# 2. Run automated tests
cd ainav-backend
python test_authentication.py
```

## What Gets Tested

The automated test suite validates all acceptance criteria:

### 🔐 Authentication Tests
- ✅ Endpoints reject requests without tokens (401)
- ✅ Endpoints reject requests with invalid tokens (401)
- ✅ Endpoints accept requests with valid tokens (200)

### 👤 User Authorization Tests
- ✅ Regular users can access user-level endpoints
- ✅ Regular users CANNOT access admin endpoints (403)
- ✅ Admin users CAN access admin endpoints (200)

### 🔒 Ownership Tests
- ✅ Users can only see their own workflows
- ✅ Users can only see their own executions
- ✅ Users cannot modify other users' workflows (403)
- ✅ Private workflows are not accessible to other users (403)

## Services Under Test

| Service | Port | Endpoints Tested |
|---------|------|------------------|
| User Service | 8003 | `/users/me`, `/personalization/*` |
| Agent Service | 8005 | `/workflows/*`, `/executions/*` |
| Content Service | 8001 | `/tools/*`, `/categories/*`, `/scenarios/*` |

## Prerequisites

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Option 2: Manual Service Start
```bash
cd ainav-backend

# Terminal 1 - User Service
uvicorn services.user_service.app.main:app --reload --port 8003

# Terminal 2 - Agent Service
uvicorn services.agent_service.app.main:app --reload --port 8005

# Terminal 3 - Content Service
uvicorn services.content_service.app.main:app --reload --port 8001
```

### Database Setup
```bash
cd ainav-backend
alembic upgrade head
```

## Running Tests

### Full Test Suite
```bash
cd ainav-backend
python test_authentication.py
```

### Expected Output
```
================================================================================
Authentication Testing Suite
================================================================================

Testing started at: 2026-01-11T04:30:00.000000

================================================================================
Step 1: Service Health Checks
================================================================================

✓ PASS - User Service health check
✓ PASS - Agent Service health check
✓ PASS - Content Service health check

================================================================================
Step 2: Create Test Users
================================================================================

Creating regular test user...
  Regular user created/exists: <uuid>
Creating admin test user...
  Admin user created/exists: <uuid>
  Note: You may need to manually set is_superuser=true in the database

================================================================================
Step 3: Authenticate Test Users
================================================================================

  Regular user token obtained
  Admin user token obtained

================================================================================
Step 4: Test User Service Protected Endpoints
================================================================================

✓ PASS - Personalization - Record Interaction - No Token (expects 401)
✓ PASS - Personalization - Record Interaction - Invalid Token (expects 401)
✓ PASS - Personalization - Record Interaction - Valid Token (expects 200)
...

================================================================================
Test Summary
================================================================================

Total Tests: 45
Passed: 45
Failed: 0

Testing completed at: 2026-01-11T04:30:45.000000
```

## Verifying Admin User

The test script cannot set admin privileges via API. You need to manually set it in the database:

```bash
# Connect to database
docker exec -it $(docker ps -q -f name=postgres) psql -U ainav -d ainav_db

# OR if running locally:
psql -h localhost -p 5433 -U ainav -d ainav_db

# Set admin flag
UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';

# Verify
SELECT username, email, is_superuser FROM users WHERE username = 'adminuser_auth';

# Exit
\q
```

## Troubleshooting

### Tests Fail with "Connection Refused"
**Problem:** Services are not running

**Solution:**
```bash
docker-compose up -d
# Wait 10 seconds for services to start
docker-compose ps  # Verify all services are "Up"
```

### Tests Fail with "401 Unauthorized" on Valid Token
**Problem:** Token expired or SECRET_KEY mismatch

**Solution:**
```bash
# Check all services use same SECRET_KEY
grep SECRET_KEY ainav-backend/.env

# Restart services to reload config
docker-compose restart
```

### Admin Tests Fail with "403 Forbidden"
**Problem:** Admin user not properly configured

**Solution:**
```bash
# Manually set is_superuser flag (see "Verifying Admin User" above)
docker exec -it $(docker ps -q -f name=postgres) psql -U ainav -d ainav_db \
  -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"
```

### Tests Fail with Database Errors
**Problem:** Database not migrated

**Solution:**
```bash
cd ainav-backend
alembic upgrade head
docker-compose restart
```

## Manual Testing

For detailed manual testing instructions, see:
- **Full Guide:** `AUTHENTICATION_TESTING_GUIDE.md`
- **Swagger UI:**
  - User Service: http://localhost:8003/docs
  - Agent Service: http://localhost:8005/docs
  - Content Service: http://localhost:8001/docs

## CI/CD Integration

To integrate into CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Authentication Tests
  run: |
    docker-compose up -d
    sleep 10  # Wait for services to be ready
    cd ainav-backend

    # Set admin user
    docker exec postgres psql -U ainav -d ainav_db \
      -c "UPDATE users SET is_superuser = true WHERE username = 'adminuser_auth';"

    # Run tests
    python test_authentication.py

    # Cleanup
    docker-compose down
```

## Next Steps

After all tests pass:
1. ✅ Mark subtask 5.1 as completed
2. ✅ Update API documentation (subtask 5.2)
3. ✅ Commit all changes
4. ✅ Update build-progress.txt

## Support

If you encounter issues not covered here:
1. Check service logs: `docker-compose logs -f <service_name>`
2. Verify database connection: `docker-compose ps postgres`
3. Review full testing guide: `AUTHENTICATION_TESTING_GUIDE.md`
