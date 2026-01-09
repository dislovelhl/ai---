from fastapi import FastAPI
from .workers.tasks import crawl_and_enrich_daily, sync_to_meilisearch, sync_github_stats, enrich_single_tool

app = FastAPI(title="AI Navigator - Automation Service")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Navigator Automation Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/tasks/crawl")
async def trigger_crawl():
    """Manually trigger the daily crawl task."""
    task = crawl_and_enrich_daily.delay()
    return {"task_id": task.id, "status": "queued"}

@app.post("/tasks/sync-search")
async def trigger_search_sync():
    """Manually trigger the Meilisearch sync task."""
    task = sync_to_meilisearch.delay()
    return {"task_id": task.id, "status": "queued"}

@app.post("/tasks/sync-github")
async def trigger_github_sync():
    """Manually trigger the GitHub stats sync task."""
    task = sync_github_stats.delay()
    return {"task_id": task.id, "status": "queued"}

@app.post("/tasks/enrich/{tool_id}")
async def trigger_enrichment(tool_id: str):
    """Manually trigger enrichment for a specific tool."""
    task = enrich_single_tool.delay(tool_id)
    return {"task_id": task.id, "status": "queued"}
