from fastapi import FastAPI
from .routers import search

app = FastAPI(title="AI Navigator - Search Service")

app.include_router(search.router, prefix="/v1/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Navigator Search Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
