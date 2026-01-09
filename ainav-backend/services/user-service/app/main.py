from fastapi import FastAPI
from .routers import auth, users

app = FastAPI(title="AI Navigator - User Service")

app.include_router(auth.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
