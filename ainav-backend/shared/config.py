import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://ainav:ainavpassword@localhost:5433/ainav_db"
    
    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # Redis connection pool settings for rate limiting
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_SOCKET_TIMEOUT: int = 5  # seconds
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5  # seconds

    # --- Rate Limiting Configuration ---
    # Execution limits per user tier (24-hour window)
    RATE_LIMIT_FREE_TIER: int = 50  # Free tier: 50 executions per day
    RATE_LIMIT_PRO_TIER: int = 500  # Pro tier: 500 executions per day
    RATE_LIMIT_ENTERPRISE_TIER: int = 9999999  # Enterprise tier: effectively unlimited
    RATE_LIMIT_WINDOW_SECONDS: int = 86400  # 24 hours in seconds

    @property
    def RATE_LIMIT_CONFIG(self) -> dict[str, int]:
        """
        Rate limit configuration dictionary per user tier.

        Returns a dictionary mapping tier names to their execution limits.
        This allows easy access from rate limiting logic while maintaining
        the ability to override via environment variables.
        """
        return {
            "free": self.RATE_LIMIT_FREE_TIER,
            "pro": self.RATE_LIMIT_PRO_TIER,
            "enterprise": self.RATE_LIMIT_ENTERPRISE_TIER
        }

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

    # --- OAuth2 Settings ---
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    # Note: This is the backend callback URL where GitHub redirects after authorization
    GITHUB_REDIRECT_URI: str = "http://localhost:8003/v1/oauth/github/callback"

    # WeChat OAuth (for Chinese users)
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    # Note: This is the backend callback URL where WeChat redirects after authorization
    WECHAT_REDIRECT_URI: str = "http://localhost:8003/v1/oauth/wechat/callback"

    # Frontend URL for redirects
    FRONTEND_URL: str = "http://localhost:3000"

    # --- Application Settings ---
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # --- Pagination ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # --- Auth ---
    # SECRET_KEY: Must be set via environment variable in production
    # The default is only for development/testing and will trigger a warning
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-only-secret-key-replace-in-production-with-32-chars-minimum"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour for access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh tokens

    def validate_security_settings(self) -> None:
        """Validate security-critical settings at startup."""
        if self.ENVIRONMENT == "production":
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production. "
                    "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            if "dev-only" in self.SECRET_KEY or "secret" in self.SECRET_KEY.lower():
                raise ValueError(
                    "SECRET_KEY appears to be a default/weak key. "
                    "Set a strong, unique SECRET_KEY in production."
                )

    # --- Email Settings ---
    SMTP_HOST: str = "smtp.qq.com"  # Default to QQ Mail for Chinese users
    SMTP_PORT: int = 465
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "AI导航"
    SMTP_USE_SSL: bool = True
    SMTP_USE_TLS: bool = False
    
    def get_utc_now(self):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
