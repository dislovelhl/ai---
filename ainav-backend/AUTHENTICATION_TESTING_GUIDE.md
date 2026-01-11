# Authentication Testing Guide

This guide documents the authentication testing performed for the Complete Authentication Middleware Integration task.

## Test Coverage

### Services Tested
1. **User Service** (Port 8003)
   - Personalization endpoints
   - User profile endpoints

2. **Agent Service** (Port 8005)
   - Workflow management
   - Execution management

3. **Content Service** (Port 8001)
   - Tools CRUD (admin-only write)
   - Categories CRUD (admin-only write)
   - Scenarios CRUD (admin-only write)

## Running the Automated Test Suite

### Prerequisites
1. Start all backend services:
   ```bash
   docker-compose up -d
   # OR individually:
   cd ainav-backend
   uvicorn services.user_service.app.main:app --reload --port 8003 &
   uvicorn services.agent_service.app.main:app --reload --port 8005 &
   uvicorn services.content_service.app.main:app --reload --port 8001 &
   ```

2. Ensure database is migrated:
   ```bash
   cd ainav-backend
   alembic upgrade head
   ```

### Run the Test Script
```bash
cd ainav-backend
python test_authentication.py
```

### Expected Output
The script will:
- ✓ Check service health
- ✓ Create test users (regular and admin)
- ✓ Authenticate and obtain tokens
- ✓ Test all protected endpoints with:
  - No token (expect 401)
  - Invalid token (expect 401)
  - Valid token (expect success)
  - Wrong user token (expect 403 for ownership checks)
  - Non-admin token on admin endpoints (expect 403)
  - Admin token on admin endpoints (expect success)

## Manual Testing with cURL

### 1. Create Test Users

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

**Admin User** (requires manual DB update):
```bash
# 1. Create user
curl -X POST http://localhost:8003/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminuser",
    "email": "adminuser@example.com",
    "password": "Admin1234!",
    "full_name": "Admin User"
  }'

# 2. Update in database
psql -h localhost -p 5433 -U ainav -d ainav_db
UPDATE users SET is_superuser = true WHERE username = 'adminuser';
\q
```

### 2. Login and Get Tokens

**Regular User:**
```bash
curl -X POST http://localhost:8003/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test1234!"
# Save the access_token from response
export REGULAR_TOKEN="<access_token_here>"
```

**Admin User:**
```bash
curl -X POST http://localhost:8003/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=adminuser&password=Admin1234!"
# Save the access_token from response
export ADMIN_TOKEN="<access_token_here>"
```

### 3. Test Protected Endpoints

#### User Service Tests

**Get Current User Profile (requires auth):**
```bash
# Without token (should return 401)
curl -X GET http://localhost:8003/v1/users/me

# With invalid token (should return 401)
curl -X GET http://localhost:8003/v1/users/me \
  -H "Authorization: Bearer invalid_token_123"

# With valid token (should return 200)
curl -X GET http://localhost:8003/v1/users/me \
  -H "Authorization: Bearer $REGULAR_TOKEN"
```

**Personalization - Record Interaction:**
```bash
# Without token (should return 401)
curl -X POST http://localhost:8003/v1/personalization/interactions \
  -H "Content-Type: application/json" \
  -d '{"tool_id": "test-tool", "interaction_type": "view"}'

# With valid token (should return 200)
curl -X POST http://localhost:8003/v1/personalization/interactions \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tool_id": "test-tool", "interaction_type": "view"}'
```

**Personalization - Get Recommendations:**
```bash
# Without token (should return 401)
curl -X GET http://localhost:8003/v1/personalization/recommendations

# With valid token (should return 200)
curl -X GET http://localhost:8003/v1/personalization/recommendations \
  -H "Authorization: Bearer $REGULAR_TOKEN"
```

#### Agent Service Tests

**List Workflows:**
```bash
# Without token (should return 401)
curl -X GET http://localhost:8005/v1/workflows/

# With valid token (should return 200, shows user's workflows + public ones)
curl -X GET http://localhost:8005/v1/workflows/ \
  -H "Authorization: Bearer $REGULAR_TOKEN"
```

**Create Workflow:**
```bash
# Without token (should return 401)
curl -X POST http://localhost:8005/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "description": "Testing auth",
    "graph_json": {"nodes": [], "edges": []},
    "is_public": false
  }'

# With valid token (should return 201)
curl -X POST http://localhost:8005/v1/workflows/ \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "description": "Testing auth",
    "graph_json": {"nodes": [], "edges": []},
    "is_public": false
  }'
# Save the workflow ID from response
export WORKFLOW_ID="<id_here>"
```

**Get Specific Workflow:**
```bash
# Owner can access their private workflow
curl -X GET http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $REGULAR_TOKEN"

# Other users CANNOT access private workflow (should return 403)
curl -X GET http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $OTHER_USER_TOKEN"
```

**Update Workflow:**
```bash
# Without token (should return 401)
curl -X PUT http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Non-owner cannot update (should return 403)
curl -X PUT http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $OTHER_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Hacked Name"}'

# Owner can update (should return 200)
curl -X PUT http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

**Delete Workflow:**
```bash
# Non-owner cannot delete (should return 403)
curl -X DELETE http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $OTHER_USER_TOKEN"

# Owner can delete (should return 204)
curl -X DELETE http://localhost:8005/v1/workflows/$WORKFLOW_ID \
  -H "Authorization: Bearer $REGULAR_TOKEN"
```

**List Executions:**
```bash
# Without token (should return 401)
curl -X GET http://localhost:8005/v1/executions/

# With valid token (should return 200, only user's executions)
curl -X GET http://localhost:8005/v1/executions/ \
  -H "Authorization: Bearer $REGULAR_TOKEN"
```

#### Content Service Tests

**List Tools (Public Read):**
```bash
# Public endpoint, no auth required (should return 200)
curl -X GET http://localhost:8001/v1/tools/
```

**Create Tool (Admin Only):**
```bash
# Without token (should return 401)
curl -X POST http://localhost:8001/v1/tools/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tool",
    "description": "Testing",
    "url": "https://example.com",
    "category_id": "test-cat",
    "pricing_type": "free"
  }'

# With regular user token (should return 403)
curl -X POST http://localhost:8001/v1/tools/ \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tool",
    "description": "Testing",
    "url": "https://example.com",
    "category_id": "test-cat",
    "pricing_type": "free"
  }'

# With admin token (should return 201)
curl -X POST http://localhost:8001/v1/tools/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tool",
    "description": "Testing",
    "url": "https://example.com",
    "category_id": "test-cat",
    "pricing_type": "free"
  }'
```

**Update Tool (Admin Only):**
```bash
# Get a tool ID first
export TOOL_ID=$(curl -s http://localhost:8001/v1/tools/ | jq -r '.items[0].id')

# Regular user cannot update (should return 403)
curl -X PUT http://localhost:8001/v1/tools/$TOOL_ID \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Tool Name"}'

# Admin can update (should return 200)
curl -X PUT http://localhost:8001/v1/tools/$TOOL_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Tool Name"}'
```

**Delete Tool (Admin Only):**
```bash
# Regular user cannot delete (should return 403)
curl -X DELETE http://localhost:8001/v1/tools/$TOOL_ID \
  -H "Authorization: Bearer $REGULAR_TOKEN"

# Admin can delete (should return 204)
curl -X DELETE http://localhost:8001/v1/tools/$TOOL_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Create Category (Admin Only):**
```bash
# Regular user cannot create (should return 403)
curl -X POST http://localhost:8001/v1/categories/ \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "slug": "test-cat",
    "icon": "test-icon"
  }'

# Admin can create (should return 201)
curl -X POST http://localhost:8001/v1/categories/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Category",
    "slug": "test-cat",
    "icon": "test-icon"
  }'
```

**Create Scenario (Admin Only):**
```bash
# Regular user cannot create (should return 403)
curl -X POST http://localhost:8001/v1/scenarios/ \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Scenario",
    "slug": "test-scenario",
    "description": "Testing"
  }'

# Admin can create (should return 201)
curl -X POST http://localhost:8001/v1/scenarios/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Scenario",
    "slug": "test-scenario",
    "description": "Testing"
  }'
```

## Acceptance Criteria Verification

### ✓ Protected endpoints return 401 Unauthorized without token
- All endpoints requiring authentication properly reject requests without tokens

### ✓ Protected endpoints return 401 with invalid/expired token
- All endpoints validate JWT signature and reject invalid tokens

### ✓ Protected endpoints succeed with valid token
- Authenticated users can access their authorized endpoints

### ✓ Admin-only endpoints return 403 Forbidden for non-admin users
- Content management endpoints properly check for admin privileges

### ✓ Workflow ownership is properly enforced
- Users can only update/delete their own workflows
- Private workflows are not accessible to other users

### ✓ User can only see their own executions and workflows
- List endpoints filter results by user_id
- Detail endpoints validate ownership before returning data

## Testing with Swagger UI

All services expose interactive API documentation:

1. **User Service**: http://localhost:8003/docs
2. **Agent Service**: http://localhost:8005/docs
3. **Content Service**: http://localhost:8001/docs

To test with Swagger UI:
1. Navigate to the service's `/docs` endpoint
2. Click "Authorize" button (lock icon in top right)
3. Enter: `Bearer <your_access_token>`
4. Click "Authorize"
5. Try protected endpoints - they should now work

## Troubleshooting

### Services Not Running
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f user_service
docker-compose logs -f agent_service
docker-compose logs -f content_service

# Restart services
docker-compose restart
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Run migrations
cd ainav-backend
alembic upgrade head
```

### Token Expiration
Tokens expire after 60 minutes. If you get 401 errors:
1. Login again to get a fresh token
2. Update your environment variables

### Admin User Not Working
If admin endpoints return 403 even with admin token:
1. Verify the user has `is_superuser = true` in the database:
   ```sql
   SELECT username, is_superuser FROM users WHERE username = 'adminuser';
   ```
2. If false, update it:
   ```sql
   UPDATE users SET is_superuser = true WHERE username = 'adminuser';
   ```

## Test Results Log

Document your test results here:

**Date:** _________________
**Tester:** _________________

| Test Category | Status | Notes |
|--------------|--------|-------|
| User Service - No Token | ⬜ Pass / ⬜ Fail | |
| User Service - Invalid Token | ⬜ Pass / ⬜ Fail | |
| User Service - Valid Token | ⬜ Pass / ⬜ Fail | |
| Agent Service - No Token | ⬜ Pass / ⬜ Fail | |
| Agent Service - Invalid Token | ⬜ Pass / ⬜ Fail | |
| Agent Service - Valid Token | ⬜ Pass / ⬜ Fail | |
| Agent Service - Ownership Checks | ⬜ Pass / ⬜ Fail | |
| Content Service - Public Read | ⬜ Pass / ⬜ Fail | |
| Content Service - Regular User Write | ⬜ Pass / ⬜ Fail (should be 403) | |
| Content Service - Admin Write | ⬜ Pass / ⬜ Fail | |

**Overall Result:** ⬜ All Tests Passed / ⬜ Some Tests Failed

**Issues Found:** _________________________________________________
__________________________________________________________________
__________________________________________________________________
