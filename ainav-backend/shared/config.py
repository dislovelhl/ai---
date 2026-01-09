import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://ainav:ainavpassword@localhost:5433/ainav_db"
    
    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # --- Meilisearch ---
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_KEY: str = "masterKey"
    
    # --- DeepSeek API (for LLM enrichment) ---
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    
    # --- Product Hunt API ---
    PRODUCTHUNT_TOKEN: Optional[str] = None
    
    # --- GitHub API ---
    GITHUB_TOKEN: Optional[str] = None
    
    # --- Application Settings ---
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # --- Pagination ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # --- Auth ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-dev-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    def get_utc_now(self):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
