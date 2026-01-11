# Faceted Search API Integration Test Plan

## Overview
This document describes how to test the faceted search API integration between the frontend (`facetedSearchTools` function) and the backend (`/v1/search/faceted` endpoint).

## Prerequisites

1. **Backend services must be running:**
   ```bash
   cd ainav-backend
   docker-compose up -d
   # OR start services individually:
   uvicorn services.search_service.app.main:app --reload --port 8002
   ```

2. **Database must have sample tools with China accessibility data**
3. **Meilisearch must be running and indexed**

## Test Cases

### Test 1: Basic Faceted Search (No Filters)
**Purpose:** Verify that the endpoint returns facet counts without any filters

**Request:**
```javascript
const response = await facetedSearchTools();
```

**Expected Response Structure:**
```json
{
  "hits": [...],  // Array of Tool objects
  "query": "",
  "processing_time_ms": 5,
  "estimated_total_hits": 50,
  "facets": {
    "pricing_type": {
      "free": 15,
      "freemium": 20,
      "paid": 10,
      "beta_free": 3,
      "open_source": 2
    },
    "is_china_accessible": {
      "accessible": 30,
      "not_accessible": 20
    },
    "has_api": {
      "with_api": 25,
      "without_api": 25
    },
    "category_slug": {
      "ai-writing": 10,
      "image-generation": 15,
      ...
    }
  },
  "page": 1,
  "page_size": 20
}
```

**Verification:**
- [ ] Response includes all facet counts
- [ ] `hits` array contains Tool objects with expected fields
- [ ] `estimated_total_hits` is a positive number
- [ ] `facets.is_china_accessible` has both `accessible` and `not_accessible` keys

---

### Test 2: Filter by China Accessibility (Accessible Only)
**Purpose:** Verify filtering for China-accessible tools works correctly

**Request:**
```javascript
const response = await facetedSearchTools({
  is_china_accessible: true
});
```

**Expected Behavior:**
- [ ] All tools in `hits` array have `is_china_accessible: true`
- [ ] `estimated_total_hits` equals `facets.is_china_accessible.accessible`
- [ ] Facet counts reflect available options within filtered results
- [ ] Response time is < 100ms (Meilisearch is fast)

**Verification:**
```javascript
// All returned tools should be China accessible
response.hits.forEach(tool => {
  console.assert(tool.is_china_accessible === true,
    `Tool ${tool.name} is not China accessible`);
});
```

---

### Test 3: Filter by China Accessibility (Blocked Only)
**Purpose:** Verify filtering for non-accessible tools

**Request:**
```javascript
const response = await facetedSearchTools({
  is_china_accessible: false
});
```

**Expected Behavior:**
- [ ] All tools in `hits` array have `is_china_accessible: false`
- [ ] No tools with `is_china_accessible: true` are returned
- [ ] Facet counts update correctly

---

### Test 4: Combined Filters (China Accessible + Free)
**Purpose:** Test multiple filter combinations

**Request:**
```javascript
const response = await facetedSearchTools({
  is_china_accessible: true,
  pricing_type: 'free'
});
```

**Expected Behavior:**
- [ ] All tools are China accessible AND free
- [ ] `estimated_total_hits` matches the count
- [ ] Facets reflect available options within this subset

**Verification:**
```javascript
response.hits.forEach(tool => {
  console.assert(tool.is_china_accessible === true, 'Not accessible');
  console.assert(tool.pricing_type === 'free', 'Not free');
});
```

---

### Test 5: Search Query + Filters
**Purpose:** Test text search combined with faceted filters

**Request:**
```javascript
const response = await facetedSearchTools({
  q: 'ChatGPT',
  is_china_accessible: true
});
```

**Expected Behavior:**
- [ ] Results match search query 'ChatGPT'
- [ ] All results are China accessible
- [ ] Search relevance is maintained
- [ ] Facets show counts for matching results

---

### Test 6: Pagination
**Purpose:** Verify pagination works with filters

**Request:**
```javascript
// Page 1
const page1 = await facetedSearchTools({
  is_china_accessible: true,
  page: 1,
  page_size: 10
});

// Page 2
const page2 = await facetedSearchTools({
  is_china_accessible: true,
  page: 2,
  page_size: 10
});
```

**Expected Behavior:**
- [ ] Page 1 returns first 10 results
- [ ] Page 2 returns next 10 results (different tools)
- [ ] No overlap between pages
- [ ] `estimated_total_hits` is the same for both requests
- [ ] Facet counts are the same for both requests

---

### Test 7: Category Filter + China Accessibility
**Purpose:** Test category filtering with accessibility filter

**Request:**
```javascript
const response = await facetedSearchTools({
  category: 'ai-writing',
  is_china_accessible: true
});
```

**Expected Behavior:**
- [ ] All tools belong to 'ai-writing' category
- [ ] All tools are China accessible
- [ ] Facets show counts within this category

---

### Test 8: API Availability Filter
**Purpose:** Test has_api filter combination

**Request:**
```javascript
const response = await facetedSearchTools({
  is_china_accessible: true,
  has_api: true
});
```

**Expected Behavior:**
- [ ] All tools have `has_api: true`
- [ ] All tools have `is_china_accessible: true`
- [ ] Facet counts reflect the intersection

---

### Test 9: Edge Case - No Results
**Purpose:** Verify behavior when filters return no results

**Request:**
```javascript
const response = await facetedSearchTools({
  q: 'nonexistenttoolthatdoesnotexist12345',
  is_china_accessible: true
});
```

**Expected Behavior:**
- [ ] `hits` array is empty
- [ ] `estimated_total_hits` is 0
- [ ] Facets show zero counts
- [ ] No errors thrown

---

### Test 10: All Filters Combined
**Purpose:** Stress test with all filter parameters

**Request:**
```javascript
const response = await facetedSearchTools({
  q: 'AI',
  pricing_type: 'freemium',
  is_china_accessible: true,
  has_api: true,
  category: 'ai-chat',
  page: 1,
  page_size: 5
});
```

**Expected Behavior:**
- [ ] All filters are applied correctly
- [ ] Results match all criteria
- [ ] Pagination works
- [ ] Facets show counts within filtered subset

---

## Performance Benchmarks

| Test Case | Expected Response Time | Acceptable Range |
|-----------|----------------------|------------------|
| No filters | < 50ms | < 100ms |
| Single filter | < 50ms | < 100ms |
| Multiple filters | < 75ms | < 150ms |
| Text search + filters | < 100ms | < 200ms |

---

## Error Handling Tests

### Test 11: Invalid Filter Values
**Purpose:** Verify error handling for invalid parameters

**Request:**
```javascript
const response = await facetedSearchTools({
  pricing_type: 'invalid_type'
});
```

**Expected Behavior:**
- [ ] Backend returns 422 Validation Error
- [ ] Frontend catches error gracefully
- [ ] Error message is descriptive

---

### Test 12: Backend Service Down
**Purpose:** Test frontend resilience when backend is unavailable

**Simulation:** Stop search service temporarily

**Expected Behavior:**
- [ ] Frontend shows appropriate error message
- [ ] No unhandled promise rejections
- [ ] UI remains responsive

---

## Integration Test Checklist

Before marking subtask 2.3 as complete:

- [ ] All 12 test cases pass
- [ ] Response structure matches TypeScript types
- [ ] Facet counts are accurate
- [ ] Filters work in isolation and combination
- [ ] Pagination works correctly
- [ ] Performance is acceptable (< 200ms for most queries)
- [ ] Error handling is robust
- [ ] No console errors in browser
- [ ] Network tab shows correct request/response

---

## How to Run Tests

### Option 1: Browser Console (Quick Test)
1. Start backend services
2. Open http://localhost:3000/tools in browser
3. Open Developer Console
4. Import API client:
   ```javascript
   import { facetedSearchTools } from '@/lib/api';
   ```
5. Run test cases manually

### Option 2: Automated Test Script
Run the provided test script:
```bash
cd ainav-web
npm run test:faceted-search
```

### Option 3: Manual API Testing with curl
```bash
# Test 1: Basic faceted search
curl "http://localhost:8002/v1/search/faceted"

# Test 2: China accessible only
curl "http://localhost:8002/v1/search/faceted?is_china_accessible=true"

# Test 3: Combined filters
curl "http://localhost:8002/v1/search/faceted?is_china_accessible=true&pricing_type=free"
```

---

## Success Criteria

✅ **Subtask 2.3 is complete when:**

1. Backend `/v1/search/faceted` endpoint returns correct data
2. Frontend `facetedSearchTools()` function successfully calls endpoint
3. Response data matches `FacetedSearchResponse` TypeScript type
4. All filter parameters work correctly
5. Facet counts are accurate and update based on filters
6. Pagination works as expected
7. Performance is acceptable (< 200ms)
8. Error handling is robust

---

## Notes

- This test plan assumes the backend search service is already implemented and working
- If backend returns different facet structure, update `FacetCounts` type in `types.ts`
- Facet counts may vary based on database content - actual numbers don't matter, structure does
- The `is_china_accessible` facet uses readable keys (`accessible`, `not_accessible`) instead of boolean strings
