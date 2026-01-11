# Testing Guide: Tool Alternatives API

This document describes how to test the Tool Alternatives API endpoint implementation.

## Overview

The alternatives API endpoint (`GET /tools/{slug}/alternatives`) finds similar tools based on category, scenarios, and China accessibility. This testing guide covers both repository-level and HTTP endpoint testing.

## Test Files

1. **`test_alternatives_api.py`** - Python test script for repository method testing
2. **`test_alternatives_endpoint.sh`** - Bash script for HTTP endpoint testing
3. **This document** - Testing guide and manual test scenarios

## Prerequisites

### For All Tests
- PostgreSQL database running with test data
- Database connection configured in `.env` file
- At least 10+ tools in various categories for meaningful results

### For HTTP Endpoint Tests
- Content service running on port 8001:
  ```bash
  cd ainav-backend
  uvicorn services.content_service.app.main:app --reload --port 8001
  ```

### For Python Repository Tests
- Python dependencies installed:
  ```bash
  cd ainav-backend
  pip install -r requirements.txt
  ```

## Running Tests

### Option 1: HTTP Endpoint Test (Recommended)

Tests the complete API endpoint via HTTP requests:

```bash
cd ainav-backend
./test_alternatives_endpoint.sh
```

**What it tests:**
- Service availability
- Basic alternatives request with default parameters
- Response structure validation (alternatives, total_count, prioritized_count)
- Limit parameter (1, 3, 10)
- Prioritize China parameter (true/false)
- Error handling (404 for invalid slug)

**Expected output:**
```
========================================================================
TOOL ALTERNATIVES API - HTTP ENDPOINT TEST
========================================================================

✓ Service is running

========================================================================
TEST 1: Getting sample tool for testing
========================================================================
✓ Found test tool: ChatGPT (slug: chatgpt)

...

========================================================================
TEST SUMMARY
========================================================================

✅ All tests passed!
```

### Option 2: Python Repository Test

Tests the repository method directly without HTTP layer:

```bash
cd ainav-backend
python test_alternatives_api.py
```

**What it tests:**
- Repository `get_alternatives()` method
- Return type validation (List[Tool])
- Original tool exclusion from results
- Limit parameter functionality
- Prioritize China parameter behavior
- Scoring algorithm execution
- Edge cases (non-existent tool, limit=0)

**Expected output:**
```
======================================================================
TOOL ALTERNATIVES API - TEST SUITE
======================================================================

TEST 1: Repository Method - get_alternatives()
...
✅ PASS: Repository method works correctly

...

======================================================================
TEST SUMMARY
======================================================================
✅ PASS - Repository Method: 5 alternatives found
✅ PASS - Limit Parameter: All limits respected
✅ PASS - Prioritize China: Parameter accepted
✅ PASS - Scoring Algorithm: 5 scored alternatives
✅ PASS - Edge Cases: Edge cases handled

Total: 5 | Passed: 5 | Failed: 0 | Skipped: 0
```

## Manual Testing Scenarios

### Scenario 1: VPN-Required Tool with China Alternatives

**Purpose:** Verify China-accessible alternatives are prioritized for blocked tools

**Steps:**
1. Find a tool that requires VPN (e.g., ChatGPT, Midjourney)
2. Call: `GET /tools/{slug}/alternatives?prioritize_china=true`
3. Verify response includes China-accessible alternatives
4. Check `prioritized_count` > 0 in response

**Expected:**
- Alternatives should include Chinese tools (e.g., 文心一言, 通义千问)
- `prioritized_count` should reflect number of China-accessible alternatives
- China-accessible tools should appear higher in the list

**Example:**
```bash
curl "http://localhost:8001/v1/tools/chatgpt/alternatives?prioritize_china=true" | jq
```

### Scenario 2: China-Accessible Tool

**Purpose:** Verify algorithm works for already accessible tools

**Steps:**
1. Find a China-accessible tool
2. Call: `GET /tools/{slug}/alternatives`
3. Verify alternatives are in the same category
4. Check for shared scenarios

**Expected:**
- Alternatives should match by category first
- Then by shared scenarios
- `prioritized_count` should be 0 (original doesn't require VPN)

### Scenario 3: Different Categories

**Purpose:** Test category matching works across different tool types

**Test cases:**
- AI Chat tools → should return other chat tools
- Image Generation → should return other image tools
- Code Assistants → should return other code tools
- Video Generation → should return other video tools

**Expected:**
- Alternatives primarily from the same category
- If not enough in same category, may include tools with shared scenarios

### Scenario 4: Limit Parameter

**Purpose:** Verify limit parameter controls result count

**Test cases:**
```bash
# Request 1 alternative
curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=1"

# Request 3 alternatives
curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=3"

# Request 10 alternatives
curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=10"
```

**Expected:**
- Response should contain ≤ limit items
- If database has fewer matching tools, return all available

### Scenario 5: Edge Cases

**Test cases:**

1. **Non-existent tool slug:**
   ```bash
   curl "http://localhost:8001/v1/tools/fake-tool/alternatives"
   # Expected: 404 Not Found
   ```

2. **Limit of 0:**
   ```bash
   curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=0"
   # Expected: Empty alternatives array
   ```

3. **Very large limit:**
   ```bash
   curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=1000"
   # Expected: Returns all available alternatives
   ```

4. **Tool with no category:**
   - Find a tool without category assignment
   - Verify alternatives still returned based on scenarios

5. **Tool with no scenarios:**
   - Find a tool without scenario associations
   - Verify alternatives based on category only

## Scoring Algorithm Verification

The scoring algorithm assigns points as follows:

- **Same category:** +3 points
- **Each shared scenario:** +1 point per scenario
- **China-accessible bonus:** +2 points (when original requires VPN and prioritize_china=true)

### Manual Verification Steps:

1. **Pick a test tool with known properties:**
   - Example: ChatGPT (AI Chat category, requires VPN)

2. **Get alternatives:**
   ```bash
   curl "http://localhost:8001/v1/tools/chatgpt/alternatives?limit=5" | jq
   ```

3. **Manually verify scores for top alternatives:**
   - Check if they're in AI Chat category (+3 points)
   - Count shared scenarios (e.g., "content creation", "productivity")
   - If China-accessible and original requires VPN (+2 points)

4. **Expected ranking:**
   - Tools with same category + China-accessible should rank highest
   - Then same category + shared scenarios
   - Then just same category
   - Finally, different category with many shared scenarios

## Response Schema Validation

Every response should match this schema:

```json
{
  "alternatives": [
    {
      "id": "uuid",
      "name": "string",
      "slug": "string",
      "description": "string",
      "website_url": "string",
      "logo_url": "string | null",
      "is_china_accessible": "boolean",
      "requires_vpn": "boolean",
      "category_id": "uuid | null",
      "category": {
        "id": "uuid",
        "name": "string",
        "slug": "string"
      },
      "scenarios": [
        {
          "id": "uuid",
          "name": "string",
          "slug": "string"
        }
      ]
    }
  ],
  "total_count": 5,
  "prioritized_count": 3
}
```

### Validation Checklist:

- [ ] `alternatives` is an array of Tool objects
- [ ] `total_count` equals length of `alternatives` array
- [ ] `prioritized_count` ≤ `total_count`
- [ ] `prioritized_count` > 0 only when original tool requires VPN and prioritize_china=true
- [ ] Each alternative has all required Tool fields
- [ ] Category and scenarios are populated (not null/empty if data exists)

## Success Criteria

All tests pass if:

1. ✅ HTTP endpoint returns 200 for valid requests
2. ✅ Response matches ToolAlternativesResponse schema
3. ✅ Limit parameter correctly limits results
4. ✅ Prioritize China parameter affects results for VPN-required tools
5. ✅ Alternatives are sorted by relevance (scoring algorithm)
6. ✅ Original tool is never included in alternatives
7. ✅ 404 returned for non-existent tool slugs
8. ✅ Edge cases handled gracefully

## Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to database

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Start services if needed
docker-compose up -d

# Check environment variables
cat ainav-backend/.env | grep DATABASE_URL
```

### No Test Data

**Problem:** Tests fail because no tools in database

**Solution:**
1. Run database migrations: `alembic upgrade head`
2. Add sample tools via API or admin panel
3. Ensure at least 10+ tools across 3+ categories

### Service Not Running

**Problem:** HTTP tests fail with connection refused

**Solution:**
```bash
# Start content service manually
cd ainav-backend
uvicorn services.content_service.app.main:app --reload --port 8001

# Or via Docker
docker-compose up content_service
```

### Import Errors in Python Tests

**Problem:** Python test script fails with import errors

**Solution:**
```bash
# Install dependencies
cd ainav-backend
pip install -r requirements.txt

# Verify Python path
python -c "import sys; print(sys.path)"
```

## Conclusion

This testing guide provides comprehensive coverage of the Tool Alternatives API. Run both automated test scripts and perform manual testing scenarios to ensure the feature works correctly across all use cases.

For issues or questions, refer to the implementation notes in `build-progress.txt`.
