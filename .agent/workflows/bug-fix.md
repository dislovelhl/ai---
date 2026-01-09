---
name: bug-fix
description: Workflow for fixing bugs
triggers:
  - "/workflow bug-fix"
  - "fix bug"
  - "debug issue"
---

# Bug Fix Workflow

Bug修复的标准流程。

## Phase 1: Issue Analysis

### 1.1 Gather Information
- [ ] 复现步骤
- [ ] 预期行为 vs 实际行为
- [ ] 影响范围
- [ ] 首次发现时间
- [ ] 错误日志/截图

### 1.2 Severity Assessment
| Level | Description | Response Time |
|-------|-------------|---------------|
| P0 | 系统崩溃/数据丢失 | 立即 |
| P1 | 核心功能不可用 | 4小时内 |
| P2 | 功能异常但有变通方法 | 24小时内 |
| P3 | 小问题/UI瑕疵 | 下个Sprint |

## Phase 2: Reproduction

### 2.1 Setup Debug Environment
```bash
cd "/home/dislove/document/ai 导航"

# Start all services with debug mode
docker-compose up -d

# Backend with debug
cd ainav-backend
DEBUG=1 uvicorn app.main:app --reload --port 8000

# Frontend with debug
cd ainav-web
NEXT_PUBLIC_DEBUG=true pnpm dev
```

### 2.2 Reproduce Issue
```bash
# Check backend logs
docker-compose logs -f api

# Check frontend console
# Open browser DevTools > Console

# Check database
docker exec -it ainav-postgres psql -U postgres ainav
```

### 2.3 Document Reproduction
```markdown
## Bug Reproduction

**Steps:**
1. Navigate to /tools
2. Click on search box
3. Type "chatgpt"
4. Press Enter

**Expected:** Search results displayed
**Actual:** Page shows loading spinner indefinitely

**Environment:**
- Browser: Chrome 120
- OS: macOS 14.2
- Backend: v1.2.3
- Frontend: v1.2.3

**Logs:**
```
Error: Connection timeout to search service
```
```

## Phase 3: Root Cause Analysis

### 3.1 Debug Tools

**Backend:**
```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

async def search_tools(query: str):
    logger.debug(f"Search query: {query}")
    # ... code
    logger.debug(f"Results: {len(results)}")
```

**Frontend:**
```typescript
// Add debug logging
console.log('[Search] Query:', query)
console.log('[Search] Response:', response)

// React Query debugging
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
```

**Database:**
```sql
-- Check slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds';

-- Explain query
EXPLAIN ANALYZE SELECT * FROM tools WHERE name ILIKE '%chatgpt%';
```

### 3.2 Common Issues

**API Issues:**
- Connection timeouts
- Rate limiting
- Authentication errors
- Validation failures

**Database Issues:**
- Slow queries
- Missing indexes
- Deadlocks
- Connection pool exhaustion

**Frontend Issues:**
- State management bugs
- Race conditions
- Memory leaks
- Hydration mismatches

## Phase 4: Fix Implementation

### 4.1 Create Fix Branch
```bash
git checkout main
git pull origin main
git checkout -b fix/<issue-description>
```

### 4.2 Write Failing Test First
```python
# tests/test_search_bug.py
import pytest

@pytest.mark.asyncio
async def test_search_timeout_handling(client):
    """Test that search handles timeout gracefully"""
    # This should fail before fix
    response = await client.get("/api/v1/search?q=test&timeout=1")
    assert response.status_code == 200
    assert "error" not in response.json()
```

### 4.3 Implement Fix
```python
# Apply minimal fix
async def search_tools(query: str, timeout: int = 30):
    try:
        async with asyncio.timeout(timeout):
            results = await search_service.search(query)
            return results
    except asyncio.TimeoutError:
        logger.warning(f"Search timeout for query: {query}")
        return SearchResponse(items=[], error="Search timeout, please try again")
```

### 4.4 Verify Fix
```bash
# Run specific test
pytest tests/test_search_bug.py -v

# Run all related tests
pytest tests/test_search*.py -v

# Run full test suite
pytest
```

## Phase 5: Review & Deploy

### 5.1 Code Review Checklist
- [ ] 修复了根本原因，不是临时解决方案
- [ ] 没有引入新问题
- [ ] 测试覆盖了修复场景
- [ ] 代码符合项目规范
- [ ] 性能影响可接受

### 5.2 Create Pull Request
```bash
git add .
git commit -m "fix(<scope>): <description>

Fixes #123

Root cause: <explanation>
Solution: <explanation>"

git push origin fix/<issue-description>
```

### 5.3 Deploy Fix
```bash
# For P0/P1: Hotfix to production
/deploy production

# For P2/P3: Normal release process
/deploy staging
# Verify on staging
/deploy production
```

## Phase 6: Post-Fix

### 6.1 Verify in Production
- [ ] Bug no longer reproducible
- [ ] No new errors in logs
- [ ] Performance metrics normal
- [ ] User feedback positive

### 6.2 Update Documentation
```markdown
## Known Issues (Resolved)

### Search Timeout Issue
**Date Fixed:** 2024-01-15
**PR:** #456
**Root Cause:** Missing timeout handling in search service
**Solution:** Added timeout handling with graceful degradation
```

### 6.3 Prevent Recurrence
- [ ] Add monitoring for similar issues
- [ ] Update testing guidelines
- [ ] Consider adding to code review checklist
- [ ] Document in runbook if applicable

## Quick Fix Checklist

```markdown
- [ ] Issue reproduced locally
- [ ] Root cause identified
- [ ] Fix branch created
- [ ] Test written (fails before fix)
- [ ] Fix implemented
- [ ] Test passes
- [ ] All tests pass
- [ ] PR created
- [ ] Code reviewed
- [ ] Deployed to staging
- [ ] Verified on staging
- [ ] Deployed to production
- [ ] Verified in production
- [ ] Issue ticket closed
```
