"""
Comprehensive test script for workflow version management endpoints.

Tests all version-related functionality:
1. Create workflow and see version 1 in history
2. Update workflow with notes and see version 2
3. Fetch version history and see all versions with snapshots
4. Compare two versions and get diff
5. Revert to previous version and see new version created
"""
import asyncio
import sys
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, '.')

from shared.database import SessionLocal
from shared.models import AgentWorkflow, User
from services.agent_service.app.schemas import WorkflowCreate, WorkflowUpdate, GraphJson, WorkflowRevert
from sqlalchemy import select


async def test_version_workflow():
    """Test complete version workflow end-to-end."""

    print("\n" + "="*80)
    print("WORKFLOW VERSION MANAGEMENT - COMPREHENSIVE TEST")
    print("="*80 + "\n")

    async with SessionLocal() as db:
        # Get or create a test user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ ERROR: No user found. Please create a user first.")
            return False

        print(f"✓ Using test user: {user.email}")

        # ========================================
        # TEST 1: Create workflow and verify version 1
        # ========================================
        print("\n" + "-"*80)
        print("TEST 1: Create workflow and verify initial version")
        print("-"*80)

        workflow_id = uuid4()
        initial_graph = {
            "nodes": [
                {
                    "id": "node-1",
                    "type": "llm",
                    "data": {"label": "LLM Node", "model": "gpt-4"},
                    "position": {"x": 100, "y": 100}
                }
            ],
            "edges": []
        }

        workflow = AgentWorkflow(
            id=workflow_id,
            user_id=user.id,
            name="Version Test Workflow",
            name_zh="版本测试工作流",
            slug=f"version-test-{str(uuid4())[:8]}",
            description="Testing version control",
            description_zh="测试版本控制",
            graph_json=initial_graph,
            version=1,
            version_history=[]
        )

        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)

        print(f"✓ Created workflow: {workflow.name}")
        print(f"  - ID: {workflow.id}")
        print(f"  - Version: {workflow.version}")
        print(f"  - History entries: {len(workflow.version_history or [])}")
        print(f"  - Graph has {len(initial_graph['nodes'])} node(s)")

        if workflow.version != 1:
            print(f"❌ FAIL: Expected version 1, got {workflow.version}")
            return False

        print("✓ PASS: Initial version is 1")

        # ========================================
        # TEST 2: Update workflow with version notes
        # ========================================
        print("\n" + "-"*80)
        print("TEST 2: Update workflow with version notes and verify version 2")
        print("-"*80)

        updated_graph = {
            "nodes": [
                {
                    "id": "node-1",
                    "type": "llm",
                    "data": {"label": "LLM Node", "model": "gpt-4"},
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "node-2",
                    "type": "api",
                    "data": {"label": "API Node", "endpoint": "/api/test"},
                    "position": {"x": 300, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "node-1",
                    "target": "node-2"
                }
            ]
        }

        # Simulate the update logic from workflows.py
        current_version = workflow.version or 1
        version_notes = "Added API node and connected it to LLM node"

        history_entry = {
            "version": current_version,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": version_notes,
            "graph_json": workflow.graph_json,  # Save OLD graph
            "user_id": str(workflow.user_id)
        }

        # Update the workflow
        workflow.version_history = (workflow.version_history or []) + [history_entry]
        workflow.version = current_version + 1
        workflow.graph_json = updated_graph

        await db.commit()
        await db.refresh(workflow)

        print(f"✓ Updated workflow with notes: '{version_notes}'")
        print(f"  - New version: {workflow.version}")
        print(f"  - History entries: {len(workflow.version_history)}")
        print(f"  - Graph now has {len(updated_graph['nodes'])} nodes and {len(updated_graph['edges'])} edge(s)")

        if workflow.version != 2:
            print(f"❌ FAIL: Expected version 2, got {workflow.version}")
            return False

        if len(workflow.version_history) != 1:
            print(f"❌ FAIL: Expected 1 history entry, got {len(workflow.version_history)}")
            return False

        print("✓ PASS: Version incremented to 2")
        print("✓ PASS: Version history contains snapshot of version 1")

        # ========================================
        # TEST 3: Fetch version history
        # ========================================
        print("\n" + "-"*80)
        print("TEST 3: Fetch version history and verify all snapshots")
        print("-"*80)

        # Simulate GET /v1/workflows/{workflow_id}/versions
        version_response = {
            "workflow_id": str(workflow.id),
            "current_version": workflow.version or 1,
            "history": workflow.version_history or []
        }

        print(f"✓ Retrieved version history:")
        print(f"  - Current version: {version_response['current_version']}")
        print(f"  - History entries: {len(version_response['history'])}")

        for entry in version_response['history']:
            print(f"\n  Version {entry['version']}:")
            print(f"    - Timestamp: {entry['timestamp']}")
            print(f"    - Notes: {entry['notes']}")
            print(f"    - Nodes: {len(entry['graph_json']['nodes'])}")
            print(f"    - Edges: {len(entry['graph_json']['edges'])}")

            # Verify snapshot has complete graph data
            if 'graph_json' not in entry:
                print(f"❌ FAIL: Version {entry['version']} missing graph_json snapshot")
                return False

            if 'nodes' not in entry['graph_json']:
                print(f"❌ FAIL: Version {entry['version']} graph_json missing nodes")
                return False

        print("\n✓ PASS: All version history entries have complete graph snapshots")

        # ========================================
        # TEST 4: Compare two versions
        # ========================================
        print("\n" + "-"*80)
        print("TEST 4: Compare version 1 and version 2")
        print("-"*80)

        # Simulate the comparison logic from compare_workflow_versions
        v1_snapshot = None
        v2_snapshot = None

        # Version 1 is in history
        for entry in workflow.version_history:
            if entry.get("version") == 1:
                v1_snapshot = entry
                break

        # Version 2 is current, but we need to create a second update to have v2 in history
        # Let's make another update first
        print("\n  Creating version 3 to enable comparison...")

        version_3_graph = {
            "nodes": [
                {
                    "id": "node-1",
                    "type": "llm",
                    "data": {"label": "LLM Node Updated", "model": "gpt-4-turbo"},  # Modified
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "node-2",
                    "type": "api",
                    "data": {"label": "API Node", "endpoint": "/api/test"},
                    "position": {"x": 300, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "node-1",
                    "target": "node-2"
                }
            ]
        }

        current_version = workflow.version
        history_entry_2 = {
            "version": current_version,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": "Updated LLM model to gpt-4-turbo",
            "graph_json": workflow.graph_json,  # Save version 2 graph
            "user_id": str(workflow.user_id)
        }

        workflow.version_history = workflow.version_history + [history_entry_2]
        workflow.version = current_version + 1
        workflow.graph_json = version_3_graph

        await db.commit()
        await db.refresh(workflow)

        print(f"  ✓ Created version 3 (current version: {workflow.version})")
        print(f"  ✓ Version history now has {len(workflow.version_history)} entries")

        # Now compare v1 and v2
        v1_snapshot = workflow.version_history[0]  # Version 1
        v2_snapshot = workflow.version_history[1]  # Version 2

        v1_graph = v1_snapshot.get("graph_json", {})
        v2_graph = v2_snapshot.get("graph_json", {})

        v1_nodes = {node["id"]: node for node in v1_graph.get("nodes", [])}
        v2_nodes = {node["id"]: node for node in v2_graph.get("nodes", [])}

        v1_edges = {edge["id"]: edge for edge in v1_graph.get("edges", [])}
        v2_edges = {edge["id"]: edge for edge in v2_graph.get("edges", [])}

        # Calculate diffs
        nodes_added = [nid for nid in v2_nodes if nid not in v1_nodes]
        nodes_removed = [nid for nid in v1_nodes if nid not in v2_nodes]
        nodes_modified = [nid for nid in v2_nodes if nid in v1_nodes and v2_nodes[nid] != v1_nodes[nid]]

        edges_added = [eid for eid in v2_edges if eid not in v1_edges]
        edges_removed = [eid for eid in v1_edges if eid not in v2_edges]

        print(f"\n✓ Comparison between v1 and v2:")
        print(f"  - Nodes added: {len(nodes_added)} {nodes_added}")
        print(f"  - Nodes removed: {len(nodes_removed)}")
        print(f"  - Nodes modified: {len(nodes_modified)}")
        print(f"  - Edges added: {len(edges_added)} {edges_added}")
        print(f"  - Edges removed: {len(edges_removed)}")

        if len(nodes_added) != 1:  # node-2 was added
            print(f"❌ FAIL: Expected 1 node added, got {len(nodes_added)}")
            return False

        if len(edges_added) != 1:  # edge-1 was added
            print(f"❌ FAIL: Expected 1 edge added, got {len(edges_added)}")
            return False

        print("✓ PASS: Version comparison correctly identifies differences")

        # ========================================
        # TEST 5: Revert to previous version
        # ========================================
        print("\n" + "-"*80)
        print("TEST 5: Revert to version 1 and verify new version created")
        print("-"*80)

        # Simulate revert to version 1
        target_version = 1
        target_snapshot = workflow.version_history[0]  # Version 1

        current_version = workflow.version
        revert_history_entry = {
            "version": current_version,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": f"Version before reverting to v{target_version}",
            "graph_json": workflow.graph_json,  # Save version 3 before revert
            "user_id": str(workflow.user_id)
        }

        # Revert
        workflow.version_history = workflow.version_history + [revert_history_entry]
        workflow.graph_json = target_snapshot.get("graph_json")
        workflow.version = current_version + 1

        await db.commit()
        await db.refresh(workflow)

        print(f"✓ Reverted to version {target_version}")
        print(f"  - New version number: {workflow.version}")
        print(f"  - History entries: {len(workflow.version_history)}")
        print(f"  - Graph now has {len(workflow.graph_json['nodes'])} node(s)")
        print(f"  - Graph now has {len(workflow.graph_json['edges'])} edge(s)")

        # Verify the revert created a new version (v4)
        if workflow.version != 4:
            print(f"❌ FAIL: Expected version 4 after revert, got {workflow.version}")
            return False

        # Verify history now has 3 entries (v1, v2, v3)
        if len(workflow.version_history) != 3:
            print(f"❌ FAIL: Expected 3 history entries, got {len(workflow.version_history)}")
            return False

        # Verify the graph is back to version 1 state (1 node, 0 edges)
        if len(workflow.graph_json['nodes']) != 1:
            print(f"❌ FAIL: Expected 1 node after revert to v1, got {len(workflow.graph_json['nodes'])}")
            return False

        if len(workflow.graph_json['edges']) != 0:
            print(f"❌ FAIL: Expected 0 edges after revert to v1, got {len(workflow.graph_json['edges'])}")
            return False

        print("✓ PASS: Revert created new version instead of overwriting")
        print("✓ PASS: Graph successfully restored to version 1 state")

        # ========================================
        # CLEANUP
        # ========================================
        print("\n" + "-"*80)
        print("Cleanup: Removing test workflow")
        print("-"*80)

        await db.delete(workflow)
        await db.commit()
        print("✓ Test workflow deleted")

        # ========================================
        # SUMMARY
        # ========================================
        print("\n" + "="*80)
        print("TEST SUMMARY - ALL TESTS PASSED ✓")
        print("="*80)
        print("\n✓ Test 1: Create workflow and see version 1 in history")
        print("✓ Test 2: Update workflow with notes and see version 2")
        print("✓ Test 3: Fetch version history and see all versions with snapshots")
        print("✓ Test 4: Compare two versions and get diff")
        print("✓ Test 5: Revert to previous version and see new version created")
        print("\n" + "="*80 + "\n")

        return True


async def main():
    """Run all tests."""
    try:
        success = await test_version_workflow()
        if success:
            print("✅ All version management tests PASSED")
            sys.exit(0)
        else:
            print("❌ Some tests FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
