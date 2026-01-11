#!/bin/bash
# AI Navigator Platform - Standardized Test Runner
# Resolves PYTHONPATH issues for microservice testing.

set -e

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${BASE_DIR}/ainav-backend"

# Set PYTHONPATH to include the backend root for shared module access
export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH}"

echo "🚀 Starting AI Navigator Test Runner..."
echo "📂 Backend Directory: ${BACKEND_DIR}"
echo "🐍 PYTHONPATH: ${PYTHONPATH}"

# Function to run tests for a specific service
run_service_tests() {
    local service=$1
    echo "🧪 Running tests for ${service}..."
    pytest "${BACKEND_DIR}/services/${service}/tests" || echo "❌ Tests failed for ${service}"
}

# If arguments provided, run specific service tests
if [ $# -gt 0 ]; then
    for service in "$@"; do
        if [ "$service" == "shared" ]; then
            pytest "${BACKEND_DIR}/tests"
        else
            run_service_tests "$service"
        fi
    done
else
    # Default: Run all core tests
    echo "🧪 Running full test suite..."
    pytest "${BACKEND_DIR}/tests/verify_user_service.py"
    # Add more core tests as needed
fi
