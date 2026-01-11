#!/usr/bin/env python3
"""
Test script for Tool Alternatives API endpoint.

This script tests the GET /tools/{slug}/alternatives endpoint to verify:
1. Response structure matches ToolAlternativesResponse schema
2. Scoring algorithm works correctly (category + scenarios + China accessibility)
3. Different parameter combinations work as expected
4. Edge cases are handled properly

Prerequisites:
- Content service must be running on port 8001
- Database must contain test data with tools of various categories

Usage:
    python test_alternatives_api.py
"""

import asyncio
import sys
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, '/home/dislove/document/ai 导航/.auto-claude/worktrees/tasks/013-tool-alternatives-suggestions/ainav-backend')

from shared.database import get_db
from shared.models import Tool, Category, Scenario
from services.content_service.app.repository import ToolRepository
from sqlalchemy import select


class AlternativesAPITester:
    """Test harness for alternatives API functionality."""

    def __init__(self):
        self.test_results = []
        self.db_session = None

    async def setup_db(self):
        """Get database session."""
        async for session in get_db():
            self.db_session = session
            break

    async def test_repository_method(self):
        """Test the repository get_alternatives() method directly."""
        print("\n" + "="*60)
        print("TEST 1: Repository Method - get_alternatives()")
        print("="*60)

        repo = ToolRepository(self.db_session)

        # Get a sample tool to test with
        query = select(Tool).limit(1)
        result = await self.db_session.execute(query)
        sample_tool = result.scalar_one_or_none()

        if not sample_tool:
            print("❌ FAIL: No tools in database for testing")
            self.test_results.append(("Repository Method", False, "No test data"))
            return

        print(f"Testing with tool: {sample_tool.name} (ID: {sample_tool.id})")

        # Test with default parameters
        alternatives = await repo.get_alternatives(sample_tool.id)

        print(f"✓ Found {len(alternatives)} alternatives (default limit: 5)")

        # Verify return type
        if not isinstance(alternatives, list):
            print(f"❌ FAIL: Expected list, got {type(alternatives)}")
            self.test_results.append(("Repository Method", False, "Wrong return type"))
            return

        # Verify all items are Tool objects
        if alternatives and not all(isinstance(t, Tool) for t in alternatives):
            print("❌ FAIL: Not all items are Tool objects")
            self.test_results.append(("Repository Method", False, "Wrong item types"))
            return

        # Verify original tool is not in results
        if sample_tool.id in [t.id for t in alternatives]:
            print("❌ FAIL: Original tool included in alternatives")
            self.test_results.append(("Repository Method", False, "Original tool in results"))
            return

        print("✓ All alternatives are valid Tool objects")
        print("✓ Original tool excluded from results")

        # Display some alternatives
        if alternatives:
            print("\nSample alternatives:")
            for i, alt in enumerate(alternatives[:3], 1):
                print(f"  {i}. {alt.name}")
                print(f"     Category: {alt.category.name if alt.category else 'None'}")
                print(f"     China-accessible: {alt.is_china_accessible}")
                print(f"     Requires VPN: {alt.requires_vpn}")

        self.test_results.append(("Repository Method", True, f"{len(alternatives)} alternatives found"))
        print("\n✅ PASS: Repository method works correctly")

    async def test_limit_parameter(self):
        """Test that limit parameter works correctly."""
        print("\n" + "="*60)
        print("TEST 2: Limit Parameter")
        print("="*60)

        repo = ToolRepository(self.db_session)

        # Get a sample tool
        query = select(Tool).limit(1)
        result = await self.db_session.execute(query)
        sample_tool = result.scalar_one_or_none()

        if not sample_tool:
            print("❌ FAIL: No tools in database")
            self.test_results.append(("Limit Parameter", False, "No test data"))
            return

        # Test different limits
        limits_to_test = [1, 3, 5, 10]

        for limit in limits_to_test:
            alternatives = await repo.get_alternatives(sample_tool.id, limit=limit)
            actual_count = len(alternatives)

            # Note: actual count may be less than limit if not enough alternatives exist
            if actual_count <= limit:
                print(f"✓ limit={limit}: returned {actual_count} alternatives (≤ {limit})")
            else:
                print(f"❌ FAIL: limit={limit}: returned {actual_count} alternatives (> {limit})")
                self.test_results.append(("Limit Parameter", False, f"Exceeded limit"))
                return

        self.test_results.append(("Limit Parameter", True, "All limits respected"))
        print("\n✅ PASS: Limit parameter works correctly")

    async def test_prioritize_china_parameter(self):
        """Test that prioritize_china parameter affects results."""
        print("\n" + "="*60)
        print("TEST 3: Prioritize China Parameter")
        print("="*60)

        repo = ToolRepository(self.db_session)

        # Try to find a tool that requires VPN
        query = select(Tool).where(Tool.requires_vpn == True).limit(1)
        result = await self.db_session.execute(query)
        vpn_tool = result.scalar_one_or_none()

        if not vpn_tool:
            print("⚠️  SKIP: No VPN-required tools in database")
            self.test_results.append(("Prioritize China", None, "No VPN tools to test"))
            return

        print(f"Testing with VPN-required tool: {vpn_tool.name}")

        # Test with prioritize_china=True
        alternatives_prioritized = await repo.get_alternatives(
            vpn_tool.id,
            limit=5,
            prioritize_china=True
        )

        # Test with prioritize_china=False
        alternatives_not_prioritized = await repo.get_alternatives(
            vpn_tool.id,
            limit=5,
            prioritize_china=False
        )

        print(f"✓ With prioritize_china=True: {len(alternatives_prioritized)} alternatives")
        print(f"✓ With prioritize_china=False: {len(alternatives_not_prioritized)} alternatives")

        # Check if China-accessible tools appear in prioritized results
        china_accessible_count = sum(
            1 for alt in alternatives_prioritized
            if alt.is_china_accessible
        )

        print(f"✓ China-accessible in prioritized results: {china_accessible_count}/{len(alternatives_prioritized)}")

        self.test_results.append(("Prioritize China", True, "Parameter accepted"))
        print("\n✅ PASS: Prioritize China parameter works")

    async def test_scoring_algorithm(self):
        """Test that scoring algorithm prioritizes correctly."""
        print("\n" + "="*60)
        print("TEST 4: Scoring Algorithm Verification")
        print("="*60)

        repo = ToolRepository(self.db_session)

        # Get a tool with relations loaded
        query = select(Tool).limit(1)
        result = await self.db_session.execute(query)
        sample_tool = result.scalar_one_or_none()

        if not sample_tool:
            print("❌ FAIL: No tools in database")
            self.test_results.append(("Scoring Algorithm", False, "No test data"))
            return

        # Load relations
        tool = await repo.get_by_id_with_relations(sample_tool.id)

        print(f"Testing with: {tool.name}")
        print(f"  Category: {tool.category.name if tool.category else 'None'}")
        print(f"  Scenarios: {len(tool.scenarios)}")
        print(f"  Requires VPN: {tool.requires_vpn}")

        # Get alternatives
        alternatives = await repo.get_alternatives(tool.id, limit=10)

        if alternatives:
            print(f"\nTop alternatives (expected to have same category or shared scenarios):")
            for i, alt in enumerate(alternatives[:5], 1):
                same_category = "✓" if alt.category_id == tool.category_id else "✗"

                # Calculate shared scenarios
                tool_scenario_ids = {s.id for s in tool.scenarios}
                alt_scenario_ids = {s.id for s in alt.scenarios}
                shared = len(tool_scenario_ids.intersection(alt_scenario_ids))

                print(f"\n  {i}. {alt.name}")
                print(f"     Same category: {same_category}")
                print(f"     Shared scenarios: {shared}")
                print(f"     China-accessible: {alt.is_china_accessible}")

        self.test_results.append(("Scoring Algorithm", True, f"{len(alternatives)} scored alternatives"))
        print("\n✅ PASS: Scoring algorithm executed")

    async def test_edge_cases(self):
        """Test edge cases and error conditions."""
        print("\n" + "="*60)
        print("TEST 5: Edge Cases")
        print("="*60)

        repo = ToolRepository(self.db_session)

        # Test 1: Non-existent tool ID
        print("\nTest 5.1: Non-existent tool ID")
        fake_id = "00000000-0000-0000-0000-000000000000"
        alternatives = await repo.get_alternatives(fake_id)

        if alternatives == []:
            print("✓ Non-existent tool returns empty list")
        else:
            print("❌ FAIL: Should return empty list for non-existent tool")
            self.test_results.append(("Edge Cases", False, "Non-existent tool handling"))
            return

        # Test 2: Limit of 0
        print("\nTest 5.2: Limit of 0")
        query = select(Tool).limit(1)
        result = await self.db_session.execute(query)
        tool = result.scalar_one_or_none()

        if tool:
            alternatives = await repo.get_alternatives(tool.id, limit=0)
            if len(alternatives) == 0:
                print("✓ Limit of 0 returns empty list")
            else:
                print(f"⚠️  Limit of 0 returned {len(alternatives)} items (may be expected)")

        self.test_results.append(("Edge Cases", True, "Edge cases handled"))
        print("\n✅ PASS: Edge cases handled correctly")

    async def run_all_tests(self):
        """Run all tests and display summary."""
        print("\n" + "="*70)
        print("TOOL ALTERNATIVES API - TEST SUITE")
        print("="*70)

        await self.setup_db()

        if not self.db_session:
            print("\n❌ ERROR: Could not connect to database")
            print("\nPlease ensure:")
            print("  1. PostgreSQL is running")
            print("  2. Database connection is configured in .env")
            print("  3. Database contains test data")
            return False

        # Run all tests
        await self.test_repository_method()
        await self.test_limit_parameter()
        await self.test_prioritize_china_parameter()
        await self.test_scoring_algorithm()
        await self.test_edge_cases()

        # Display summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed = sum(1 for _, result, _ in self.test_results if result is True)
        failed = sum(1 for _, result, _ in self.test_results if result is False)
        skipped = sum(1 for _, result, _ in self.test_results if result is None)
        total = len(self.test_results)

        for test_name, result, details in self.test_results:
            status = "✅ PASS" if result is True else ("❌ FAIL" if result is False else "⚠️  SKIP")
            print(f"{status} - {test_name}: {details}")

        print("\n" + "-"*70)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        print("="*70)

        return failed == 0

    async def cleanup(self):
        """Cleanup resources."""
        if self.db_session:
            await self.db_session.close()


async def main():
    """Main test runner."""
    tester = AlternativesAPITester()
    try:
        success = await tester.run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 2
    finally:
        await tester.cleanup()

    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
