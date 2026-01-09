import asyncio
import sys
import os

# Add /app to sys.path to ensure imports work correctly
sys.path.append("/app")

from services.automation_service.app.workers.tasks import _sync_to_meilisearch_pipeline

async def main():
    print("Starting manual sync...")
    result = await _sync_to_meilisearch_pipeline()
    print(f"Sync result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
