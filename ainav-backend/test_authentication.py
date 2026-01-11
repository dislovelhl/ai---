#!/usr/bin/env python3
"""
Comprehensive Authentication Testing Script
Tests all protected endpoints with valid and invalid tokens
"""
import requests
import json
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Service URLs
USER_SERVICE = "http://localhost:8003/v1"
AGENT_SERVICE = "http://localhost:8005/v1"
CONTENT_SERVICE = "http://localhost:8001/v1"

# Test results tracker
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}")
    print(f"{message}")
    print(f"{'='*80}{Colors.RESET}\n")


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    if passed:
        print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - {test_name}")
        test_results["passed"] += 1
    else:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {test_name}")
        if details:
            print(f"  {Colors.YELLOW}Details: {details}{Colors.RESET}")
        test_results["failed"] += 1
        test_results["errors"].append({"test": test_name, "details": details})


def check_service_health(service_url: str, service_name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        healthy = response.status_code == 200
        print_test(f"{service_name} health check", healthy,
                   f"Status: {response.status_code}" if not healthy else "")
        return healthy
    except Exception as e:
        print_test(f"{service_name} health check", False, str(e))
        return False


def create_test_user(username: str, email: str, password: str, is_superuser: bool = False) -> Optional[str]:
    """Create a test user and return their ID"""
    try:
        response = requests.post(
            f"{USER_SERVICE}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": f"Test User {username}"
            }
        )
        if response.status_code in [200, 201]:
            user_data = response.json()
            user_id = user_data.get("id")

            # If we need to make this user a superuser, we'd need direct DB access
            # For now, we'll just note this limitation
            if is_superuser:
                print(f"{Colors.YELLOW}  Note: Cannot set superuser flag via API. Manual DB update required.{Colors.RESET}")

            return user_id
        elif response.status_code == 400 and "already exists" in response.text.lower():
            # User already exists, try to get token
            return "existing"
        else:
            print(f"  Failed to create user {username}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating user {username}: {e}")
        return None


def login_user(username: str, password: str) -> Optional[str]:
    """Login and return access token"""
    try:
        response = requests.post(
            f"{USER_SERVICE}/auth/login",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"  Failed to login {username}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error logging in {username}: {e}")
        return None


def test_endpoint_without_token(method: str, url: str, endpoint_name: str, expected_status: int = 401):
    """Test an endpoint without authentication token"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json={}, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            response = requests.request(method, url, timeout=10)

        passed = response.status_code == expected_status
        print_test(
            f"{endpoint_name} - No Token (expects {expected_status})",
            passed,
            f"Got {response.status_code}" if not passed else ""
        )
    except Exception as e:
        print_test(f"{endpoint_name} - No Token", False, str(e))


def test_endpoint_with_invalid_token(method: str, url: str, endpoint_name: str, expected_status: int = 401):
    """Test an endpoint with invalid token"""
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={}, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json={}, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            response = requests.request(method, url, headers=headers, timeout=10)

        passed = response.status_code == expected_status
        print_test(
            f"{endpoint_name} - Invalid Token (expects {expected_status})",
            passed,
            f"Got {response.status_code}" if not passed else ""
        )
    except Exception as e:
        print_test(f"{endpoint_name} - Invalid Token", False, str(e))


def test_endpoint_with_valid_token(method: str, url: str, endpoint_name: str, token: str,
                                   data: Optional[Dict] = None, expected_status: int = 200):
    """Test an endpoint with valid token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        request_data = data or {}

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=request_data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=request_data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            response = requests.request(method, url, json=request_data, headers=headers, timeout=10)

        # Accept a range of success codes
        if expected_status == 200:
            passed = response.status_code in [200, 201]
        else:
            passed = response.status_code == expected_status

        print_test(
            f"{endpoint_name} - Valid Token (expects {expected_status})",
            passed,
            f"Got {response.status_code}: {response.text[:200]}" if not passed else ""
        )
        return response
    except Exception as e:
        print_test(f"{endpoint_name} - Valid Token", False, str(e))
        return None


def main():
    """Run all authentication tests"""
    print_header("Authentication Testing Suite")
    print(f"Testing started at: {datetime.now().isoformat()}\n")

    # Step 1: Check service health
    print_header("Step 1: Service Health Checks")
    user_service_ok = check_service_health(USER_SERVICE, "User Service")
    agent_service_ok = check_service_health(AGENT_SERVICE, "Agent Service")
    content_service_ok = check_service_health(CONTENT_SERVICE, "Content Service")

    if not (user_service_ok and agent_service_ok and content_service_ok):
        print(f"\n{Colors.RED}Some services are not healthy. Please start all services first.{Colors.RESET}")
        print(f"{Colors.YELLOW}Run: docker-compose up -d{Colors.RESET}")
        return 1

    # Step 2: Create test users
    print_header("Step 2: Create Test Users")
    print("Creating regular test user...")
    regular_user_id = create_test_user("testuser_auth", "testuser_auth@example.com", "Test1234!")
    if regular_user_id:
        print(f"  {Colors.GREEN}Regular user created/exists: {regular_user_id}{Colors.RESET}")

    print("Creating admin test user...")
    admin_user_id = create_test_user("adminuser_auth", "adminuser_auth@example.com", "Admin1234!", is_superuser=True)
    if admin_user_id:
        print(f"  {Colors.GREEN}Admin user created/exists: {admin_user_id}{Colors.RESET}")
        print(f"  {Colors.YELLOW}Note: You may need to manually set is_superuser=true in the database{Colors.RESET}")

    # Step 3: Login and get tokens
    print_header("Step 3: Authenticate Test Users")
    regular_token = login_user("testuser_auth", "Test1234!")
    if regular_token:
        print(f"  {Colors.GREEN}Regular user token obtained{Colors.RESET}")
    else:
        print(f"  {Colors.RED}Failed to get regular user token{Colors.RESET}")
        return 1

    admin_token = login_user("adminuser_auth", "Admin1234!")
    if admin_token:
        print(f"  {Colors.GREEN}Admin user token obtained{Colors.RESET}")
    else:
        print(f"  {Colors.RED}Failed to get admin user token{Colors.RESET}")
        return 1

    # Step 4: Test User Service Endpoints
    print_header("Step 4: Test User Service Protected Endpoints")

    # Personalization endpoints
    test_endpoint_without_token("POST", f"{USER_SERVICE}/personalization/interactions",
                                "Personalization - Record Interaction")
    test_endpoint_with_invalid_token("POST", f"{USER_SERVICE}/personalization/interactions",
                                     "Personalization - Record Interaction")
    test_endpoint_with_valid_token("POST", f"{USER_SERVICE}/personalization/interactions",
                                   "Personalization - Record Interaction", regular_token,
                                   {"tool_id": "test-tool-123", "interaction_type": "view"})

    test_endpoint_without_token("GET", f"{USER_SERVICE}/personalization/recommendations",
                                "Personalization - Get Recommendations")
    test_endpoint_with_invalid_token("GET", f"{USER_SERVICE}/personalization/recommendations",
                                     "Personalization - Get Recommendations")
    test_endpoint_with_valid_token("GET", f"{USER_SERVICE}/personalization/recommendations",
                                   "Personalization - Get Recommendations", regular_token)

    # User profile endpoints
    test_endpoint_without_token("GET", f"{USER_SERVICE}/users/me",
                                "Users - Get Current User Profile")
    test_endpoint_with_invalid_token("GET", f"{USER_SERVICE}/users/me",
                                     "Users - Get Current User Profile")
    test_endpoint_with_valid_token("GET", f"{USER_SERVICE}/users/me",
                                   "Users - Get Current User Profile", regular_token)

    # Step 5: Test Agent Service Endpoints
    print_header("Step 5: Test Agent Service Protected Endpoints")

    # Workflows endpoints
    test_endpoint_without_token("GET", f"{AGENT_SERVICE}/workflows/",
                                "Workflows - List Workflows")
    test_endpoint_with_invalid_token("GET", f"{AGENT_SERVICE}/workflows/",
                                     "Workflows - List Workflows")
    test_endpoint_with_valid_token("GET", f"{AGENT_SERVICE}/workflows/",
                                   "Workflows - List Workflows", regular_token)

    test_endpoint_without_token("POST", f"{AGENT_SERVICE}/workflows/",
                                "Workflows - Create Workflow")
    test_endpoint_with_invalid_token("POST", f"{AGENT_SERVICE}/workflows/",
                                     "Workflows - Create Workflow")

    # Create a workflow with valid token
    workflow_data = {
        "name": "Test Auth Workflow",
        "description": "Testing authentication",
        "graph_json": {"nodes": [], "edges": []},
        "is_public": False
    }
    create_response = test_endpoint_with_valid_token("POST", f"{AGENT_SERVICE}/workflows/",
                                                     "Workflows - Create Workflow", regular_token,
                                                     workflow_data)
    workflow_id = None
    if create_response and create_response.status_code in [200, 201]:
        workflow_id = create_response.json().get("id")
        print(f"  {Colors.GREEN}Created workflow: {workflow_id}{Colors.RESET}")

    # Executions endpoints
    test_endpoint_without_token("GET", f"{AGENT_SERVICE}/executions/",
                                "Executions - List Executions")
    test_endpoint_with_invalid_token("GET", f"{AGENT_SERVICE}/executions/",
                                     "Executions - List Executions")
    test_endpoint_with_valid_token("GET", f"{AGENT_SERVICE}/executions/",
                                   "Executions - List Executions", regular_token)

    # Step 6: Test Content Service Admin Endpoints
    print_header("Step 6: Test Content Service Admin-Only Endpoints")

    # Tools endpoints - public read
    public_response = requests.get(f"{CONTENT_SERVICE}/tools/", timeout=10)
    print_test("Tools - List Tools (Public Read)",
              public_response.status_code == 200,
              f"Got {public_response.status_code}" if public_response.status_code != 200 else "")

    # Tools endpoints - admin write
    tool_data = {
        "name": "Test Auth Tool",
        "description": "Testing authentication",
        "url": "https://example.com",
        "category_id": "test-category",
        "pricing_type": "free"
    }

    test_endpoint_without_token("POST", f"{CONTENT_SERVICE}/tools/",
                                "Tools - Create Tool (Admin Only)")
    test_endpoint_with_invalid_token("POST", f"{CONTENT_SERVICE}/tools/",
                                     "Tools - Create Tool (Admin Only)")

    # Test with regular user token (should fail with 403)
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/tools/",
                                   "Tools - Create Tool with Regular User", regular_token,
                                   tool_data, expected_status=403)

    # Test with admin token (should succeed)
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/tools/",
                                   "Tools - Create Tool with Admin User", admin_token,
                                   tool_data, expected_status=200)

    # Categories endpoints
    category_data = {
        "name": "Test Auth Category",
        "slug": "test-auth-cat",
        "icon": "test-icon"
    }

    test_endpoint_without_token("POST", f"{CONTENT_SERVICE}/categories/",
                                "Categories - Create Category (Admin Only)")
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/categories/",
                                   "Categories - Create Category with Regular User", regular_token,
                                   category_data, expected_status=403)
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/categories/",
                                   "Categories - Create Category with Admin User", admin_token,
                                   category_data, expected_status=200)

    # Scenarios endpoints
    scenario_data = {
        "name": "Test Auth Scenario",
        "slug": "test-auth-scenario",
        "description": "Testing"
    }

    test_endpoint_without_token("POST", f"{CONTENT_SERVICE}/scenarios/",
                                "Scenarios - Create Scenario (Admin Only)")
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/scenarios/",
                                   "Scenarios - Create Scenario with Regular User", regular_token,
                                   scenario_data, expected_status=403)
    test_endpoint_with_valid_token("POST", f"{CONTENT_SERVICE}/scenarios/",
                                   "Scenarios - Create Scenario with Admin User", admin_token,
                                   scenario_data, expected_status=200)

    # Step 7: Test Ownership Validation
    print_header("Step 7: Test Ownership Validation")

    if workflow_id:
        # Create a second user to test ownership
        print("Creating second test user...")
        second_user_id = create_test_user("testuser2_auth", "testuser2_auth@example.com", "Test1234!")
        second_token = login_user("testuser2_auth", "Test1234!")

        if second_token:
            # Try to access first user's private workflow with second user's token
            test_endpoint_with_valid_token("GET", f"{AGENT_SERVICE}/workflows/{workflow_id}",
                                          "Workflows - Access Other User's Private Workflow",
                                          second_token, expected_status=403)

            # Try to update first user's workflow with second user's token
            test_endpoint_with_valid_token("PUT", f"{AGENT_SERVICE}/workflows/{workflow_id}",
                                          "Workflows - Update Other User's Workflow",
                                          second_token,
                                          {"name": "Hacked Name"},
                                          expected_status=403)

            # Try to delete first user's workflow with second user's token
            test_endpoint_with_valid_token("DELETE", f"{AGENT_SERVICE}/workflows/{workflow_id}",
                                          "Workflows - Delete Other User's Workflow",
                                          second_token, expected_status=403)

    # Print Summary
    print_header("Test Summary")
    total_tests = test_results["passed"] + test_results["failed"]
    print(f"Total Tests: {total_tests}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")

    if test_results["failed"] > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for error in test_results["errors"]:
            print(f"  - {error['test']}")
            if error['details']:
                print(f"    {error['details']}")

    print(f"\nTesting completed at: {datetime.now().isoformat()}")

    return 0 if test_results["failed"] == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testing interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
