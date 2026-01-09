import pytest
import httpx
import asyncio
from unittest.mock import patch, MagicMock

BASE_URL = "http://localhost:8004"

@pytest.mark.asyncio
async def test_automation_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_trigger_crawl():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/tasks/crawl")
        assert response.status_code == 200
        assert "task_id" in response.json()
        assert response.json()["status"] == "queued"

# This test would require mocking the Celery task execution if we want to wait for it
# Or we can just check the logs after triggering.
