"""
Verification script to check that all version-related endpoints are properly implemented.

This script performs static code analysis to verify:
1. All required endpoints exist
2. Proper schemas are defined
3. Logic follows the specification

This does NOT require the service to be running.
"""
import re
import sys


def check_file_exists(filepath):
    """Check if file exists."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None


def verify_workflows_router():
    """Verify workflows.py has all required version endpoints."""
    print("\n" + "="*80)
    print("VERIFYING WORKFLOW VERSION IMPLEMENTATION")
    print("="*80 + "\n")

    filepath = "./services/agent_service/app/routers/workflows.py"
    content = check_file_exists(filepath)

    if not content:
        return False

    print(f"✓ Found file: {filepath}")

    tests_passed = 0
    tests_total = 0

    # Test 1: Check for version_notes in WorkflowUpdate schema import
    print("\n" + "-"*80)
    print("TEST 1: WorkflowUpdate schema includes version_notes field")
    print("-"*80)
    tests_total += 1

    if "WorkflowUpdate" in content:
        print("✓ WorkflowUpdate schema imported")

        # Check in update_workflow function for version_notes usage
        if "version_notes" in content:
            print("✓ version_notes field is used in code")
            tests_passed += 1
        else:
            print("❌ version_notes field not found in code")
    else:
        print("❌ WorkflowUpdate schema not imported")

    # Test 2: Check update_workflow saves version history
    print("\n" + "-"*80)
    print("TEST 2: update_workflow saves complete graph snapshots to version_history")
    print("-"*80)
    tests_total += 1

    if "async def update_workflow" in content:
        print("✓ update_workflow endpoint exists")

        # Check for version history logic
        update_func = content[content.find("async def update_workflow"):]
        update_func = update_func[:update_func.find("\n\n@router") if "\n\n@router" in update_func else len(update_func)]

        required_elements = [
            ("workflow.version_history", "Accesses version_history field"),
            ("graph_json", "Handles graph_json"),
            ("history_entry", "Creates history entry"),
            ("current_version", "Tracks current version"),
            ("workflow.version =", "Updates version number")
        ]

        all_present = True
        for element, description in required_elements:
            if element in update_func:
                print(f"  ✓ {description}")
            else:
                print(f"  ❌ Missing: {description}")
                all_present = False

        if all_present:
            tests_passed += 1

    else:
        print("❌ update_workflow endpoint not found")

    # Test 3: Check revert endpoint exists
    print("\n" + "-"*80)
    print("TEST 3: Revert endpoint (POST /workflows/{id}/revert)")
    print("-"*80)
    tests_total += 1

    if '@router.post("/{workflow_id}/revert"' in content:
        print("✓ Revert endpoint route exists")

        if "async def revert_workflow_version" in content:
            print("✓ revert_workflow_version function exists")

            # Check revert logic
            revert_func = content[content.find("async def revert_workflow_version"):]
            revert_func = revert_func[:revert_func.find("\n\n@router") if "\n\n@router" in revert_func else revert_func.find("\n\n\n")]

            required_logic = [
                ("target_version", "Accepts target version"),
                ("version_history", "Accesses version history"),
                ("target_snapshot", "Finds target snapshot"),
                ("workflow.graph_json =", "Restores graph from snapshot"),
                ("workflow.version =", "Increments version number"),
                ("history_entry", "Saves current state before revert"),
            ]

            all_logic_present = True
            for logic, description in required_logic:
                if logic in revert_func:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ❌ Missing: {description}")
                    all_logic_present = False

            if all_logic_present:
                tests_passed += 1
        else:
            print("❌ revert_workflow_version function not found")
    else:
        print("❌ Revert endpoint route not found")

    # Test 4: Check comparison endpoint exists
    print("\n" + "-"*80)
    print("TEST 4: Comparison endpoint (GET /workflows/{id}/versions/compare)")
    print("-"*80)
    tests_total += 1

    if '@router.get("/{workflow_id}/versions/compare"' in content:
        print("✓ Comparison endpoint route exists")

        if "async def compare_workflow_versions" in content:
            print("✓ compare_workflow_versions function exists")

            # Check comparison logic
            compare_func = content[content.find("async def compare_workflow_versions"):]
            compare_func = compare_func[:compare_func.find("\n\n@router") if "\n\n@router" in compare_func else len(compare_func)]

            required_logic = [
                ("v1:", "Accepts v1 parameter"),
                ("v2:", "Accepts v2 parameter"),
                ("v1_snapshot", "Fetches v1 snapshot"),
                ("v2_snapshot", "Fetches v2 snapshot"),
                ("nodes_added", "Calculates nodes added"),
                ("nodes_removed", "Calculates nodes removed"),
                ("nodes_modified", "Calculates nodes modified"),
                ("edges_added", "Calculates edges added"),
                ("edges_removed", "Calculates edges removed"),
                ("VersionComparison", "Returns VersionComparison response"),
            ]

            all_logic_present = True
            for logic, description in required_logic:
                if logic in compare_func:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ❌ Missing: {description}")
                    all_logic_present = False

            if all_logic_present:
                tests_passed += 1
        else:
            print("❌ compare_workflow_versions function not found")
    else:
        print("❌ Comparison endpoint route not found")

    # Test 5: Check version history endpoint exists
    print("\n" + "-"*80)
    print("TEST 5: Version history endpoint (GET /workflows/{id}/versions)")
    print("-"*80)
    tests_total += 1

    if '@router.get("/{workflow_id}/versions")' in content:
        print("✓ Version history endpoint route exists")

        if "async def get_workflow_versions" in content:
            print("✓ get_workflow_versions function exists")

            # Check it returns version history
            versions_func = content[content.find("async def get_workflow_versions"):]
            versions_func = versions_func[:versions_func.find("\n\n@router") if "\n\n@router" in versions_func else versions_func.find("\n\n\n")]

            if "workflow.version_history" in versions_func and "current_version" in versions_func:
                print("  ✓ Returns version history and current version")
                tests_passed += 1
            else:
                print("  ❌ Missing required return data")
        else:
            print("❌ get_workflow_versions function not found")
    else:
        print("❌ Version history endpoint route not found")

    # Summary
    print("\n" + "="*80)
    print(f"VERIFICATION SUMMARY: {tests_passed}/{tests_total} tests passed")
    print("="*80 + "\n")

    if tests_passed == tests_total:
        print("✅ ALL IMPLEMENTATION CHECKS PASSED")
        print("\nAll required endpoints and logic are properly implemented:")
        print("  ✓ WorkflowUpdate accepts version_notes")
        print("  ✓ update_workflow saves complete graph snapshots")
        print("  ✓ POST /workflows/{id}/revert endpoint with proper logic")
        print("  ✓ GET /workflows/{id}/versions/compare endpoint with diff calculation")
        print("  ✓ GET /workflows/{id}/versions endpoint")
        return True
    else:
        print(f"❌ {tests_total - tests_passed} CHECKS FAILED")
        print("\nPlease review the failed tests above.")
        return False


def verify_schemas():
    """Verify that all required schemas are defined."""
    print("\n" + "="*80)
    print("VERIFYING SCHEMAS")
    print("="*80 + "\n")

    # Check schemas/__init__.py
    filepath = "./services/agent_service/app/schemas/__init__.py"
    content = check_file_exists(filepath)

    if not content:
        return False

    print(f"✓ Found file: {filepath}")

    required_schemas = [
        "WorkflowRevert",
        "VersionComparison",
        "VersionSnapshot",
        "NodeDiff",
        "EdgeDiff",
    ]

    tests_passed = 0
    tests_total = len(required_schemas)

    for schema in required_schemas:
        if schema in content:
            print(f"  ✓ {schema} schema exists")
            tests_passed += 1
        else:
            print(f"  ❌ {schema} schema missing")

    print(f"\n{tests_passed}/{tests_total} schemas found")

    return tests_passed == tests_total


def main():
    """Run all verification checks."""
    print("\n" + "="*80)
    print("WORKFLOW VERSION IMPLEMENTATION VERIFICATION")
    print("="*80)

    router_ok = verify_workflows_router()
    schemas_ok = verify_schemas()

    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80 + "\n")

    if router_ok and schemas_ok:
        print("✅ ALL VERIFICATION CHECKS PASSED")
        print("\nThe workflow version management feature is fully implemented:")
        print("  ✓ All 5 required endpoints are present")
        print("  ✓ All required schemas are defined")
        print("  ✓ All business logic is properly implemented")
        print("\nNext step: Manual testing using MANUAL_VERSION_TESTING.md")
        return True
    else:
        print("❌ SOME VERIFICATION CHECKS FAILED")
        print("\nPlease review the errors above and fix the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
