"""app/core/config.py
Nextcareon — Central configuration loaded from .env via pydantic-settings.
Usage:  from app.core.config import settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    APP_NAME: str = "Nextcareon"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_PREFIX: str = "/api/v1"

    # ── PostgreSQL ───────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # ── Admin seed ───────────────────────────────────────────
    FIRST_ADMIN_EMAIL: str = "admin@nextcareon.com"
    FIRST_ADMIN_PASSWORD: str = "change-me-immediately"
    FIRST_ADMIN_NAME: str = "Super Admin"


settings = Settings()