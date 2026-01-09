import asyncio
import httpx
import pytest
from uuid import UUID

BASE_URL = "http://localhost:8000/v1"

@pytest.mark.asyncio
async def test_categories_crud():
    async with httpx.AsyncClient() as client:
        # 1. Create
        cat_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "A test category",
            "icon": "test-icon",
            "order": 1
        }
        response = await client.post(f"{BASE_URL}/categories/", json=cat_data)
        assert response.status_code == 200
        category = response.json()
        cat_id = category["id"]
        assert category["name"] == cat_data["name"]

        # 2. Update
        update_data = {
            "name": "Updated Category",
            "slug": "updated-category",
            "order": 2
        }
        response = await client.put(f"{BASE_URL}/categories/{cat_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated Category"

        # 3. List
        response = await client.get(f"{BASE_URL}/categories/")
        assert response.status_code == 200
        assert any(c["id"] == cat_id for c in response.json())

        # 4. Delete
        response = await client.delete(f"{BASE_URL}/categories/{cat_id}")
        assert response.status_code == 200
        
        # Verify deleted
        response = await client.get(f"{BASE_URL}/categories/{update_data['slug']}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_scenarios_crud():
    async with httpx.AsyncClient() as client:
        # 1. Create
        scen_data = {
            "name": "Test Scenario",
            "slug": "test-scenario",
            "icon": "scen-icon"
        }
        response = await client.post(f"{BASE_URL}/scenarios/", json=scen_data)
        assert response.status_code == 200
        scenario = response.json()
        scen_id = scenario["id"]

        # 2. Update
        update_data = {"name": "Updated Scenario"}
        response = await client.put(f"{BASE_URL}/scenarios/{scen_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Scenario"

        # 3. Delete
        response = await client.delete(f"{BASE_URL}/scenarios/{scen_id}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_tools_crud():
    import time
    ts = int(time.time())
    async with httpx.AsyncClient() as client:
        # Setup: Create a category first
        cat_res = await client.post(f"{BASE_URL}/categories/", json={"name": f"Tools Cat {ts}", "slug": f"tools-cat-{ts}"})
        print(f"DEBUG Categories POST status: {cat_res.status_code}")
        print(f"DEBUG Categories POST body: {cat_res.text}")
        cat_id = cat_res.json()["id"]
        
        # Setup: Create a scenario
        scen_res = await client.post(f"{BASE_URL}/scenarios/", json={"name": f"Tools Scen {ts}", "slug": f"tools-scen-{ts}"})
        scen_id = scen_res.json()["id"]

        # 1. Create Tool
        tool_data = {
            "name": f"Test Tool {ts}",
            "slug": f"test-tool-{ts}",
            "description": "A great AI tool",
            "url": "https://example.com",
            "category_id": cat_id,
            "scenario_ids": [scen_id]
        }
        response = await client.post(f"{BASE_URL}/tools/", json=tool_data)
        print(f"DEBUG Tool POST body: {response.text}")
        assert response.status_code == 200
        tool = response.json()
        tool_id = tool["id"]
        assert len(tool["scenarios"]) == 1

        # 2. Update Tool (Change description and remove scenario)
        update_data = {
            "description": "Updated description",
            "scenario_ids": []
        }
        response = await client.put(f"{BASE_URL}/tools/{tool_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["description"] == "Updated description"
        assert len(updated["scenarios"]) == 0

        # 3. Delete
        await client.delete(f"{BASE_URL}/tools/{tool_id}")
        await client.delete(f"{BASE_URL}/categories/{cat_id}")
        await client.delete(f"{BASE_URL}/scenarios/{scen_id}")
