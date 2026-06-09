"""app/core/config.py
Nextcareon — Central configuration loaded from .env via pydantic-settings.
Usage:  from app.core.config import settings
"""

from enum import Enum
from pydantic import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Optional


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


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
    APP_ENV: Environment = Environment.DEVELOPMENT
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

    # ── Score Weights ─────────────────────────────────────────
    score_weights: Dict[str, int] = {
        "course_completion": 15,
        "quiz_performance": 15,
        "project_quality": 30,
        "portfolio_strength": 20,
        "mock_interview": 20,
    }

    # ── Worker Settings ──────────────────────────────────────
    WORKER_CONCURRENCY: int = 10
    WORKER_JOB_TIMEOUT: int = 300

    # ── OpenAI Chat Settings ─────────────────────────────────
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    OPENAI_CHAT_MAX_TOKENS: int = 1024

    # ── OpenAI Embeddings ────────────────────────────────────
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    # ── Rate Limiting ────────────────────────────────────────
    GLOBAL_RATE_LIMIT_STR: str = "100 per minute"
    AI_RATE_LIMIT_STR: str = "20 per minute"
    AUTH_RATE_LIMIT_STR: str = "10 per minute"

    # ── Sentry ───────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None

    @classmethod
    def __pydantic_validate__(cls, data: dict, config: ValidationInfo):
        env = data.get("APP_ENV", "development")
        if env == "production":
            required = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY", "JWT_SECRET_KEY", "OPENAI_API_KEY"]
            missing = [k for k in required if not data.get(k)]
            if missing:
                raise ValueError(f"Production environment requires: {', '.join(missing)}")
        return super().__pydantic_validate__(data, config)


settings = Settings()
