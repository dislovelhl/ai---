# API Integration Tests

This directory contains test files and documentation for verifying the faceted search API integration.

## Files

- **`faceted-search-api-test.md`** - Comprehensive test plan with all test cases and success criteria
- **`test-faceted-search-api.js`** - Automated Node.js test script for API endpoint testing
- **`faceted-search-browser-test.html`** - Interactive browser-based test page with visual UI

## Running Tests

### Option 1: Automated Node.js Test (Recommended)

```bash
# From ainav-web directory
node tests/test-faceted-search-api.js

# Or use npm script
npm run test:api
```

**Requirements:**
- Backend search service running on http://localhost:8002
- Database populated with sample tools

**Output:**
- ✓ Color-coded pass/fail results
- Response time measurements
- Facet count verification
- Exit code 0 on success, 1 on failure

### Option 2: Browser-Based Interactive Test

1. Start the backend search service:
   ```bash
   cd ainav-backend
   uvicorn services.search_service.app.main:app --reload --port 8002
   ```

2. Open the test page:
   ```bash
   open tests/faceted-search-browser-test.html
   # or
   firefox tests/faceted-search-browser-test.html
   ```

3. Use the interactive UI to:
   - Test different filter combinations
   - View facet counts in real-time
   - Inspect response structure
   - Verify China accessibility filtering

### Option 3: Manual curl Testing

```bash
# Test 1: Basic faceted search
curl "http://localhost:8002/v1/search/faceted" | jq

# Test 2: China accessible only
curl "http://localhost:8002/v1/search/faceted?is_china_accessible=true" | jq

# Test 3: Combined filters
curl "http://localhost:8002/v1/search/faceted?is_china_accessible=true&pricing_type=free" | jq
```

## Test Coverage

The tests verify:

✅ **Core Functionality:**
- Faceted search endpoint accessibility
- Response structure matches TypeScript types
- All facet counts are returned correctly

✅ **Filter Functionality:**
- `is_china_accessible` filter (true/false)
- `pricing_type` filter (free, freemium, paid, etc.)
- `has_api` filter (true/false)
- `category` filter
- Text search query (`q`)

✅ **Pagination:**
- Page and page_size parameters
- Correct result counts per page

✅ **Performance:**
- Response time < 200ms for most queries
- Facet count calculation efficiency

✅ **Edge Cases:**
- No results found
- Invalid filter combinations
- Empty queries

## Expected Response Structure

```typescript
{
  hits: Tool[];              // Array of matching tools
  query: string;             // Search query used
  processing_time_ms: number;
  estimated_total_hits: number;
  facets: {
    pricing_type: Record<string, number>;
    is_china_accessible: {
      accessible: number;
      not_accessible: number;
    };
    has_api: {
      with_api: number;
      without_api: number;
    };
    category_slug: Record<string, number>;
  };
  page: number;
  page_size: number;
}
```

## Troubleshooting

### "Failed to fetch" or Connection Refused

**Problem:** Backend service is not running

**Solution:**
```bash
cd ainav-backend
docker-compose up -d
# OR
uvicorn services.search_service.app.main:app --reload --port 8002
```

### "No results found"

**Problem:** Database is empty or not indexed in Meilisearch

**Solution:**
1. Check database has tools:
   ```sql
   SELECT COUNT(*) FROM tools WHERE is_china_accessible = true;
   ```

2. Re-index Meilisearch:
   ```bash
   # Trigger reindexing via admin endpoint
   curl -X POST http://localhost:8002/v1/admin/reindex
   ```

### CORS Errors in Browser Test

**Problem:** CORS not enabled for localhost

**Solution:** Backend should include CORS middleware for `http://localhost:3000` origin. Check `ainav-backend/services/search_service/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Facet Counts Don't Match

**Problem:** Meilisearch index is stale

**Solution:**
```bash
# Force reindex
curl -X POST http://localhost:8002/v1/admin/reindex
```

## Success Criteria

✅ All automated tests pass (7/7)
✅ Response time < 200ms
✅ Facet counts are accurate
✅ Filters work in isolation and combination
✅ No console errors

## Next Steps

After verifying API integration:

1. **Phase 3:** Create ToolFilters UI component
2. **Phase 4:** Integrate filters into tools page
3. **Phase 5:** Add sidebar quick filter
4. **Phase 6:** Final testing and polish
