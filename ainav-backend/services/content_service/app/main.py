from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import categories, tools, scenarios, admin
from shared.config import settings

app = FastAPI(
    title="AI Navigator - Content Service",
    version="1.0.0",
    description="Content management API for AI tools, categories, and scenarios"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routers
app.include_router(categories.router, prefix="/v1")
app.include_router(tools.router, prefix="/v1")
app.include_router(scenarios.router, prefix="/v1")
app.include_router(admin.router, prefix="/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to AI Navigator Content Service"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-service"}

