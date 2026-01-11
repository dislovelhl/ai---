"""
AI Navigator - Agent Service

Provides APIs for managing Skills, Agent Workflows, and Executions.
This is the core of the Agentic Creation Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import skills, workflows, executions, chat, analytics, collaboration


app = FastAPI(
    title="AI Navigator - Agent Service",
    description="Agent workflow builder and execution service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router, prefix="/v1/skills", tags=["Skills"])
app.include_router(workflows.router, prefix="/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/v1/executions", tags=["Executions"])
app.include_router(chat.router, prefix="/v1/agents", tags=["Agent Chat"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
app.include_router(collaboration.router, prefix="/v1/collaboration", tags=["Collaboration"])



@app.get("/")
async def root():
    return {
        "service": "agent-service",
        "version": "1.0.0",
        "description": "Agent workflow builder and execution service",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-service"}
