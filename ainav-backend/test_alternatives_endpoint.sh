#!/bin/bash
#
# HTTP Test Script for Tool Alternatives API Endpoint
#
# This script tests the GET /tools/{slug}/alternatives endpoint via HTTP requests.
# It verifies response structure, status codes, and parameter handling.
#
# Prerequisites:
# - Content service running on http://localhost:8001
# - Database with test data
# - jq installed (for JSON parsing)
#
# Usage:
#   ./test_alternatives_endpoint.sh
#

set -e

BASE_URL="http://localhost:8001/v1"
ENDPOINT="/tools"

echo "========================================================================"
echo "TOOL ALTERNATIVES API - HTTP ENDPOINT TEST"
echo "========================================================================"
echo ""

# Check if service is running
echo "Checking if content service is running on port 8001..."
if ! curl -s -f "${BASE_URL}/health" > /dev/null 2>&1; then
    echo "❌ ERROR: Content service is not running or not accessible"
    echo ""
    echo "Please start the service with:"
    echo "  cd ainav-backend"
    echo "  uvicorn services.content_service.app.main:app --reload --port 8001"
    echo ""
    exit 1
fi
echo "✓ Service is running"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  WARNING: jq is not installed. Output will not be formatted."
    echo "Install with: sudo apt install jq"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi
echo ""

# Test 1: Get a list of tools to find a valid slug
echo "========================================================================"
echo "TEST 1: Getting sample tool for testing"
echo "========================================================================"

RESPONSE=$(curl -s "${BASE_URL}/tools?limit=1")

if [ "$JQ_AVAILABLE" = true ]; then
    TOOL_SLUG=$(echo "$RESPONSE" | jq -r '.[0].slug // empty')
    TOOL_NAME=$(echo "$RESPONSE" | jq -r '.[0].name // empty')
else
    TOOL_SLUG=$(echo "$RESPONSE" | grep -o '"slug":"[^"]*"' | head -1 | cut -d'"' -f4)
    TOOL_NAME=$(echo "$RESPONSE" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ -z "$TOOL_SLUG" ]; then
    echo "❌ ERROR: No tools found in database"
    echo "Please add some tools to the database first"
    exit 1
fi

echo "✓ Found test tool: $TOOL_NAME (slug: $TOOL_SLUG)"
echo ""

# Test 2: Basic alternatives request
echo "========================================================================"
echo "TEST 2: Basic Alternatives Request (default parameters)"
echo "========================================================================"

RESPONSE=$(curl -s "${BASE_URL}/tools/${TOOL_SLUG}/alternatives")
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tools/${TOOL_SLUG}/alternatives")

echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ FAIL: Expected 200, got $HTTP_CODE"
    echo "Response: $RESPONSE"
    exit 1
fi
echo "✓ Status code is 200"

# Validate response structure
if [ "$JQ_AVAILABLE" = true ]; then
    TOTAL_COUNT=$(echo "$RESPONSE" | jq -r '.total_count // "missing"')
    PRIORITIZED_COUNT=$(echo "$RESPONSE" | jq -r '.prioritized_count // "missing"')
    ALTERNATIVES_COUNT=$(echo "$RESPONSE" | jq '.alternatives | length')

    echo ""
    echo "Response structure:"
    echo "  total_count: $TOTAL_COUNT"
    echo "  prioritized_count: $PRIORITIZED_COUNT"
    echo "  alternatives count: $ALTERNATIVES_COUNT"

    if [ "$TOTAL_COUNT" = "missing" ] || [ "$PRIORITIZED_COUNT" = "missing" ]; then
        echo "❌ FAIL: Response missing required fields"
        exit 1
    fi
    echo "✓ Response has correct structure"

    # Display first alternative if available
    if [ "$ALTERNATIVES_COUNT" -gt 0 ]; then
        echo ""
        echo "Sample alternative:"
        echo "$RESPONSE" | jq '.alternatives[0] | {name, slug, is_china_accessible, requires_vpn}'
    fi
else
    echo "Response (raw): $RESPONSE"
fi

echo ""
echo "✅ PASS: Basic alternatives request works"
echo ""

# Test 3: Custom limit parameter
echo "========================================================================"
echo "TEST 3: Custom Limit Parameter"
echo "========================================================================"

for LIMIT in 1 3 10; do
    RESPONSE=$(curl -s "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?limit=${LIMIT}")
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?limit=${LIMIT}")

    if [ "$HTTP_CODE" != "200" ]; then
        echo "❌ FAIL: limit=$LIMIT returned HTTP $HTTP_CODE"
        exit 1
    fi

    if [ "$JQ_AVAILABLE" = true ]; then
        COUNT=$(echo "$RESPONSE" | jq '.alternatives | length')
        if [ "$COUNT" -le "$LIMIT" ]; then
            echo "✓ limit=$LIMIT: returned $COUNT alternatives (≤ $LIMIT)"
        else
            echo "❌ FAIL: limit=$LIMIT: returned $COUNT alternatives (> $LIMIT)"
            exit 1
        fi
    else
        echo "✓ limit=$LIMIT: HTTP 200"
    fi
done

echo ""
echo "✅ PASS: Limit parameter works correctly"
echo ""

# Test 4: prioritize_china parameter
echo "========================================================================"
echo "TEST 4: Prioritize China Parameter"
echo "========================================================================"

RESPONSE_TRUE=$(curl -s "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?prioritize_china=true")
HTTP_CODE_TRUE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?prioritize_china=true")

RESPONSE_FALSE=$(curl -s "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?prioritize_china=false")
HTTP_CODE_FALSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tools/${TOOL_SLUG}/alternatives?prioritize_china=false")

if [ "$HTTP_CODE_TRUE" = "200" ] && [ "$HTTP_CODE_FALSE" = "200" ]; then
    echo "✓ prioritize_china=true: HTTP $HTTP_CODE_TRUE"
    echo "✓ prioritize_china=false: HTTP $HTTP_CODE_FALSE"

    if [ "$JQ_AVAILABLE" = true ]; then
        COUNT_TRUE=$(echo "$RESPONSE_TRUE" | jq '.alternatives | length')
        COUNT_FALSE=$(echo "$RESPONSE_FALSE" | jq '.alternatives | length')
        echo "✓ Results with prioritize_china=true: $COUNT_TRUE alternatives"
        echo "✓ Results with prioritize_china=false: $COUNT_FALSE alternatives"
    fi
else
    echo "❌ FAIL: prioritize_china parameter failed"
    echo "  true: HTTP $HTTP_CODE_TRUE"
    echo "  false: HTTP $HTTP_CODE_FALSE"
    exit 1
fi

echo ""
echo "✅ PASS: Prioritize China parameter accepted"
echo ""

# Test 5: Invalid tool slug
echo "========================================================================"
echo "TEST 5: Invalid Tool Slug (Error Handling)"
echo "========================================================================"

RESPONSE=$(curl -s "${BASE_URL}/tools/nonexistent-tool-slug-12345/alternatives")
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tools/nonexistent-tool-slug-12345/alternatives")

echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" = "404" ]; then
    echo "✓ Returns 404 for non-existent tool"
else
    echo "❌ FAIL: Expected 404, got $HTTP_CODE"
    exit 1
fi

echo ""
echo "✅ PASS: Error handling works correctly"
echo ""

# Summary
echo "========================================================================"
echo "TEST SUMMARY"
echo "========================================================================"
echo ""
echo "✅ All tests passed!"
echo ""
echo "Tested:"
echo "  ✓ Service availability"
echo "  ✓ Basic alternatives request"
echo "  ✓ Response structure validation"
echo "  ✓ Limit parameter (1, 3, 10)"
echo "  ✓ Prioritize China parameter (true/false)"
echo "  ✓ Error handling (404 for invalid slug)"
echo ""
echo "========================================================================"
