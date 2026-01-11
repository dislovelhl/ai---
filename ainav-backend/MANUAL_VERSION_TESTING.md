# Manual Testing Guide - Workflow Version Management

This guide provides step-by-step instructions to manually test all version-related endpoints.

## Prerequisites

1. Ensure the agent service is running on port 8005:
   ```bash
   cd services/agent_service
   uvicorn app.main:app --port 8005 --reload
   ```

2. Ensure database is accessible at `localhost:5433`

3. Have `curl` and `jq` installed for formatted JSON output

## Test Workflow

### Setup: Create a Test User (if needed)

```bash
# Check if users exist
curl -s http://localhost:8003/v1/users | jq '.'
```

---

## TEST 1: Create Workflow and Verify Version 1

### Create a new workflow

```bash
curl -X POST http://localhost:8005/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Version Test Workflow",
    "name_zh": "版本测试工作流",
    "slug": "version-test-workflow",
    "description": "Testing version control functionality",
    "description_zh": "测试版本控制功能",
    "graph_json": {
      "nodes": [
        {
          "id": "node-1",
          "type": "llm",
          "data": {
            "label": "LLM Node",
            "model": "gpt-4"
          },
          "position": {"x": 100, "y": 100}
        }
      ],
      "edges": []
    },
    "trigger_type": "manual",
    "is_public": false
  }' | jq '.'
```

**Expected Result:**
- Status: 201 Created
- Response contains workflow with `version: 1`
- `version_history` should be empty array `[]`

**Save the workflow ID from the response for subsequent tests:**
```bash
export WORKFLOW_ID="<paste-workflow-id-here>"
```

### Verify version history is empty

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions" | jq '.'
```

**Expected Result:**
```json
{
  "workflow_id": "<workflow-id>",
  "current_version": 1,
  "history": []
}
```

✅ **TEST 1 PASS CRITERIA:**
- Workflow created successfully
- Initial version is 1
- Version history is empty (no previous versions yet)

---

## TEST 2: Update Workflow with Version Notes and See Version 2

### Update the workflow with version notes

```bash
curl -X PUT "http://localhost:8005/v1/workflows/${WORKFLOW_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_json": {
      "nodes": [
        {
          "id": "node-1",
          "type": "llm",
          "data": {
            "label": "LLM Node",
            "model": "gpt-4"
          },
          "position": {"x": 100, "y": 100}
        },
        {
          "id": "node-2",
          "type": "api",
          "data": {
            "label": "API Call Node",
            "endpoint": "/api/test"
          },
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
    },
    "version_notes": "Added API call node and connected it to LLM node"
  }' | jq '.'
```

**Expected Result:**
- Status: 200 OK
- Response shows `version: 2`
- `version_history` array contains 1 entry for version 1
- Current `graph_json` has 2 nodes and 1 edge

✅ **TEST 2 PASS CRITERIA:**
- Version incremented to 2
- Version notes saved in history entry
- Version 1 snapshot preserved in history

---

## TEST 3: Fetch Version History and See All Versions with Snapshots

### Get complete version history

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions" | jq '.'
```

**Expected Result:**
```json
{
  "workflow_id": "<workflow-id>",
  "current_version": 2,
  "history": [
    {
      "version": 1,
      "timestamp": "2026-01-11T...",
      "notes": "Added API call node and connected it to LLM node",
      "graph_json": {
        "nodes": [
          {
            "id": "node-1",
            "type": "llm",
            "data": {"label": "LLM Node", "model": "gpt-4"},
            "position": {"x": 100, "y": 100}
          }
        ],
        "edges": []
      },
      "user_id": "<user-id>"
    }
  ]
}
```

### Verify the history entry contains complete graph snapshot

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions" | \
  jq '.history[0].graph_json.nodes | length'
```

**Expected Output:** `1` (version 1 had 1 node)

✅ **TEST 3 PASS CRITERIA:**
- History contains version 1 entry
- Version 1 snapshot includes complete `graph_json`
- Version 1 snapshot has 1 node and 0 edges (original state)
- Timestamp, notes, and user_id are present

---

## TEST 4: Make Another Update to Enable Comparison

### Update to version 3

```bash
curl -X PUT "http://localhost:8005/v1/workflows/${WORKFLOW_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_json": {
      "nodes": [
        {
          "id": "node-1",
          "type": "llm",
          "data": {
            "label": "LLM Node",
            "model": "gpt-4-turbo"
          },
          "position": {"x": 100, "y": 100}
        },
        {
          "id": "node-2",
          "type": "api",
          "data": {
            "label": "API Call Node",
            "endpoint": "/api/test"
          },
          "position": {"x": 300, "y": 100}
        },
        {
          "id": "node-3",
          "type": "output",
          "data": {
            "label": "Output Node"
          },
          "position": {"x": 500, "y": 100}
        }
      ],
      "edges": [
        {
          "id": "edge-1",
          "source": "node-1",
          "target": "node-2"
        },
        {
          "id": "edge-2",
          "source": "node-2",
          "target": "node-3"
        }
      ]
    },
    "version_notes": "Added output node and updated LLM model to gpt-4-turbo"
  }' | jq '.version'
```

**Expected Output:** `3`

---

## TEST 5: Compare Two Versions and Get Diff

### Compare version 1 and version 2

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions/compare?v1=1&v2=2" | jq '.'
```

**Expected Result:**
```json
{
  "workflow_id": "<workflow-id>",
  "version1": {
    "version": 1,
    "timestamp": "...",
    "notes": "Added API call node and connected it to LLM node",
    "graph_json": {
      "nodes": [...],  // 1 node
      "edges": []      // 0 edges
    },
    "user_id": "..."
  },
  "version2": {
    "version": 2,
    "timestamp": "...",
    "notes": "Added output node and updated LLM model to gpt-4-turbo",
    "graph_json": {
      "nodes": [...],  // 2 nodes
      "edges": [...]   // 1 edge
    },
    "user_id": "..."
  },
  "nodes_added": [
    {
      "node_id": "node-2",
      "change_type": "added",
      "new_data": {...}
    }
  ],
  "nodes_removed": [],
  "nodes_modified": [],
  "edges_added": [
    {
      "edge_id": "edge-1",
      "change_type": "added",
      "new_data": {...}
    }
  ],
  "edges_removed": [],
  "edges_modified": []
}
```

### Verify the differences

```bash
# Count nodes added
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions/compare?v1=1&v2=2" | \
  jq '.nodes_added | length'
```

**Expected Output:** `1` (node-2 was added)

```bash
# Count edges added
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions/compare?v1=1&v2=2" | \
  jq '.edges_added | length'
```

**Expected Output:** `1` (edge-1 was added)

✅ **TEST 5 PASS CRITERIA:**
- Comparison returns both version snapshots
- Correctly identifies 1 node added (node-2)
- Correctly identifies 1 edge added (edge-1)
- No nodes or edges removed
- No nodes modified

---

## TEST 6: Revert to Previous Version and See New Version Created

### Revert to version 1

```bash
curl -X POST "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/revert" \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": 1
  }' | jq '.'
```

**Expected Result:**
- Status: 200 OK
- Response shows `version: 4` (new version created, not overwriting)
- Current `graph_json` matches version 1 (1 node, 0 edges)
- `version_history` now contains 3 entries (v1, v2, v3)

### Verify revert created new version

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}" | jq '.version'
```

**Expected Output:** `4`

### Verify graph was restored to version 1 state

```bash
# Count nodes in current graph
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}" | \
  jq '.graph_json.nodes | length'
```

**Expected Output:** `1` (back to version 1 state)

```bash
# Count edges in current graph
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}" | \
  jq '.graph_json.edges | length'
```

**Expected Output:** `0` (back to version 1 state)

### Verify version history contains all previous versions

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions" | \
  jq '.history | length'
```

**Expected Output:** `3` (v1, v2, v3 are all preserved)

✅ **TEST 6 PASS CRITERIA:**
- Revert created version 4 (not overwriting v3)
- Current graph matches version 1 state (1 node, 0 edges)
- All previous versions (v1, v2, v3) preserved in history
- Version 3 was saved to history before revert

---

## TEST 7: Error Cases

### Test reverting to non-existent version

```bash
curl -X POST "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/revert" \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": 999
  }'
```

**Expected Result:**
- Status: 404 Not Found
- Error message: "Version 999 not found in workflow history"

### Test comparing non-existent versions

```bash
curl -s "http://localhost:8005/v1/workflows/${WORKFLOW_ID}/versions/compare?v1=1&v2=999"
```

**Expected Result:**
- Status: 404 Not Found
- Error message about version not found

### Test with invalid workflow ID

```bash
curl -s "http://localhost:8005/v1/workflows/00000000-0000-0000-0000-000000000000/versions"
```

**Expected Result:**
- Status: 404 Not Found
- Error message: "Workflow not found"

✅ **TEST 7 PASS CRITERIA:**
- All error cases return appropriate 404 status codes
- Error messages are descriptive

---

## Cleanup

### Delete the test workflow

```bash
curl -X DELETE "http://localhost:8005/v1/workflows/${WORKFLOW_ID}"
```

**Expected Result:**
- Status: 204 No Content

---

## Summary of Acceptance Criteria

| # | Criteria | Endpoint | Status |
|---|----------|----------|--------|
| 1 | Can create workflow and see version 1 in history | POST /workflows, GET /workflows/{id}/versions | ✅ |
| 2 | Can update workflow with notes and see version 2 | PUT /workflows/{id} | ✅ |
| 3 | Can fetch version history and see all versions with snapshots | GET /workflows/{id}/versions | ✅ |
| 4 | Can compare two versions and get diff | GET /workflows/{id}/versions/compare | ✅ |
| 5 | Can revert to previous version and see new version created | POST /workflows/{id}/revert | ✅ |

## Additional Notes

- All version operations create new versions rather than overwriting
- Version history preserves complete graph snapshots for full restoration
- Version notes are optional but recommended for tracking changes
- Comparison endpoint provides detailed node and edge diffs
- Revert operation is non-destructive (creates new version)
