#!/usr/bin/env node

/**
 * Faceted Search API Integration Test Script
 *
 * Tests the faceted search API endpoint to verify:
 * - Endpoint is accessible
 * - Response structure matches expected format
 * - Filters work correctly
 * - Facet counts are returned
 *
 * Usage:
 *   node tests/test-faceted-search-api.js
 *
 * Prerequisites:
 *   - Backend search service running on http://localhost:8002
 *   - Database populated with sample tools
 */

const SEARCH_API = process.env.NEXT_PUBLIC_SEARCH_API || 'http://localhost:8002/v1';

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function success(message) {
  log(`✓ ${message}`, colors.green);
}

function error(message) {
  log(`✗ ${message}`, colors.red);
}

function info(message) {
  log(`ℹ ${message}`, colors.blue);
}

function warn(message) {
  log(`⚠ ${message}`, colors.yellow);
}

async function testEndpoint(testName, url, expectedChecks) {
  log(`\n${'='.repeat(60)}`, colors.cyan);
  log(`Test: ${testName}`, colors.cyan);
  log('='.repeat(60), colors.cyan);
  info(`URL: ${url}`);

  try {
    const startTime = Date.now();
    const response = await fetch(url);
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    if (!response.ok) {
      error(`HTTP ${response.status}: ${response.statusText}`);
      const errorBody = await response.text();
      console.log('Error response:', errorBody);
      return false;
    }

    const data = await response.json();
    success(`Response received in ${responseTime}ms`);

    // Run expected checks
    let allPassed = true;
    for (const check of expectedChecks) {
      try {
        const passed = check.fn(data);
        if (passed) {
          success(check.description);
        } else {
          error(check.description);
          allPassed = false;
        }
      } catch (err) {
        error(`${check.description} - ${err.message}`);
        allPassed = false;
      }
    }

    // Display sample data
    if (data.hits && data.hits.length > 0) {
      info(`Sample tool: ${data.hits[0].name} (is_china_accessible: ${data.hits[0].is_china_accessible})`);
    }

    if (data.facets) {
      info(`Facet counts preview:`);
      console.log(`  - China Accessible: ${JSON.stringify(data.facets.is_china_accessible)}`);
      console.log(`  - Has API: ${JSON.stringify(data.facets.has_api)}`);
    }

    return allPassed;

  } catch (err) {
    error(`Request failed: ${err.message}`);
    return false;
  }
}

async function runAllTests() {
  log('\n' + '='.repeat(60), colors.cyan);
  log('FACETED SEARCH API INTEGRATION TESTS', colors.cyan);
  log('='.repeat(60) + '\n', colors.cyan);

  const results = [];

  // Test 1: Basic faceted search (no filters)
  results.push(await testEndpoint(
    'Test 1: Basic Faceted Search (No Filters)',
    `${SEARCH_API}/search/faceted`,
    [
      {
        description: 'Response has hits array',
        fn: (data) => Array.isArray(data.hits)
      },
      {
        description: 'Response has facets object',
        fn: (data) => data.facets && typeof data.facets === 'object'
      },
      {
        description: 'Facets include is_china_accessible',
        fn: (data) => data.facets.is_china_accessible !== undefined
      },
      {
        description: 'is_china_accessible has accessible count',
        fn: (data) => typeof data.facets.is_china_accessible.accessible === 'number'
      },
      {
        description: 'is_china_accessible has not_accessible count',
        fn: (data) => typeof data.facets.is_china_accessible.not_accessible === 'number'
      },
      {
        description: 'Facets include has_api',
        fn: (data) => data.facets.has_api !== undefined
      },
      {
        description: 'Response has estimated_total_hits',
        fn: (data) => typeof data.estimated_total_hits === 'number' && data.estimated_total_hits >= 0
      },
      {
        description: 'Response has page number',
        fn: (data) => typeof data.page === 'number'
      },
      {
        description: 'Response has page_size',
        fn: (data) => typeof data.page_size === 'number'
      }
    ]
  ));

  // Test 2: Filter by China accessibility (accessible only)
  results.push(await testEndpoint(
    'Test 2: Filter China Accessible Tools Only',
    `${SEARCH_API}/search/faceted?is_china_accessible=true`,
    [
      {
        description: 'Response has hits',
        fn: (data) => Array.isArray(data.hits)
      },
      {
        description: 'All tools are China accessible',
        fn: (data) => data.hits.every(tool => tool.is_china_accessible === true)
      },
      {
        description: 'Facets are present',
        fn: (data) => data.facets !== undefined
      }
    ]
  ));

  // Test 3: Filter by China accessibility (not accessible)
  results.push(await testEndpoint(
    'Test 3: Filter Non-Accessible Tools',
    `${SEARCH_API}/search/faceted?is_china_accessible=false`,
    [
      {
        description: 'All tools are NOT China accessible',
        fn: (data) => data.hits.every(tool => tool.is_china_accessible === false)
      }
    ]
  ));

  // Test 4: Combined filters (China accessible + free)
  results.push(await testEndpoint(
    'Test 4: Combined Filters (China Accessible + Free)',
    `${SEARCH_API}/search/faceted?is_china_accessible=true&pricing_type=free`,
    [
      {
        description: 'All tools are China accessible',
        fn: (data) => data.hits.every(tool => tool.is_china_accessible === true)
      },
      {
        description: 'All tools are free',
        fn: (data) => data.hits.length === 0 || data.hits.every(tool => tool.pricing_type === 'free')
      }
    ]
  ));

  // Test 5: Pagination
  results.push(await testEndpoint(
    'Test 5: Pagination (Page 1, Size 5)',
    `${SEARCH_API}/search/faceted?page=1&page_size=5`,
    [
      {
        description: 'Returns at most 5 results',
        fn: (data) => data.hits.length <= 5
      },
      {
        description: 'Page number is 1',
        fn: (data) => data.page === 1
      },
      {
        description: 'Page size is 5',
        fn: (data) => data.page_size === 5
      }
    ]
  ));

  // Test 6: Has API filter
  results.push(await testEndpoint(
    'Test 6: Filter Tools with API',
    `${SEARCH_API}/search/faceted?has_api=true`,
    [
      {
        description: 'All tools have API',
        fn: (data) => data.hits.length === 0 || data.hits.every(tool => tool.has_api === true)
      }
    ]
  ));

  // Test 7: Search query with filter
  results.push(await testEndpoint(
    'Test 7: Search Query + China Accessible Filter',
    `${SEARCH_API}/search/faceted?q=AI&is_china_accessible=true`,
    [
      {
        description: 'Response contains query field',
        fn: (data) => data.query === 'AI'
      },
      {
        description: 'All results are China accessible',
        fn: (data) => data.hits.length === 0 || data.hits.every(tool => tool.is_china_accessible === true)
      }
    ]
  ));

  // Summary
  log('\n' + '='.repeat(60), colors.cyan);
  log('TEST SUMMARY', colors.cyan);
  log('='.repeat(60), colors.cyan);

  const passed = results.filter(r => r).length;
  const failed = results.filter(r => !r).length;
  const total = results.length;

  log(`\nTotal Tests: ${total}`, colors.blue);
  success(`Passed: ${passed}`);
  if (failed > 0) {
    error(`Failed: ${failed}`);
  } else {
    log(`Failed: ${failed}`, colors.reset);
  }

  if (failed === 0) {
    log('\n🎉 All tests passed!', colors.green);
    log('✅ Faceted search API integration is working correctly', colors.green);
    process.exit(0);
  } else {
    log('\n❌ Some tests failed', colors.red);
    log('Please check the backend service and database content', colors.yellow);
    process.exit(1);
  }
}

// Run tests
info('Starting faceted search API integration tests...');
info(`Backend URL: ${SEARCH_API}\n`);

runAllTests().catch(err => {
  error(`Fatal error: ${err.message}`);
  console.error(err);
  process.exit(1);
});
