"""
app/core/config.py
Nextcareon — Central configuration loaded from .env via pydantic-settings.
Usage:  from app.core.config import settings
"""

from typing import List
from pydantic import AnyHttpUrl, field_validator
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
    CACHE_TTL_MARKET_DATA: int = 3600
    CACHE_TTL_LEADERBOARD: int = 300
    CACHE_TTL_CAREER_SCORE: int = 900
    CACHE_TTL_QUIZ_SESSION: int = 1800

    # ── JWT ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Anthropic ────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 1024
    AI_COINS_PER_SESSION: int = 100
    AI_QUESTIONS_PER_SESSION: int = 10

    # ── OpenAI (Embeddings) ──────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    # ── RAG ──────────────────────────────────────────────────
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64
    RAG_TOP_K: int = 5

    # ── Storage ──────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-southeast-1"
    AWS_S3_BUCKET: str = ""
    LOCAL_MEDIA_DIR: str = "./media"
    LOCAL_MEDIA_URL: str = "http://localhost:8000/media"

    # ── TTS ──────────────────────────────────────────────────
    TTS_BACKEND: str = "gtts"
    TTS_DEFAULT_LANG: str = "en"
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "southeastasia"

    # ── Gamification ─────────────────────────────────────────
    COIN_LESSON_COMPLETE: int = 10
    COIN_QUIZ_PASS: int = 25
    COIN_ASSIGNMENT_COMPLETE: int = 100
    COIN_PROJECT_COMPLETE: int = 300
    COIN_COURSE_COMPLETE: int = 500
    LEADERBOARD_TOP_N: int = 50

    # ── Career Score Weights ──────────────────────────────────
    SCORE_WEIGHT_COURSE_COMPLETION: int = 15
    SCORE_WEIGHT_QUIZ_PERFORMANCE: int = 15
    SCORE_WEIGHT_PROJECT_QUALITY: int = 30
    SCORE_WEIGHT_PORTFOLIO_STRENGTH: int = 20
    SCORE_WEIGHT_MOCK_INTERVIEW: int = 20

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_AI: str = "20/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"

    # ── Worker ───────────────────────────────────────────────
    WORKER_CONCURRENCY: int = 10
    WORKER_JOB_TIMEOUT: int = 300
    WORKER_RETRY_JOBS: int = 3

    # ── Logging ──────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # ── Admin seed ───────────────────────────────────────────
    FIRST_ADMIN_EMAIL: str = "admin@nextcareon.com"
    FIRST_ADMIN_PASSWORD: str = "change-me-immediately"
    FIRST_ADMIN_NAME: str = "Super Admin"

    # ── Email ────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "Nextcareon"
    SMTP_TLS: bool = True

    # ── Computed helpers ──────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def score_weights(self) -> dict:
        return {
            "course_completion": self.SCORE_WEIGHT_COURSE_COMPLETION,
            "quiz_performance":  self.SCORE_WEIGHT_QUIZ_PERFORMANCE,
            "project_quality":   self.SCORE_WEIGHT_PROJECT_QUALITY,
            "portfolio_strength":self.SCORE_WEIGHT_PORTFOLIO_STRENGTH,
            "mock_interview":    self.SCORE_WEIGHT_MOCK_INTERVIEW,
        }

    @property
    def coin_rewards(self) -> dict:
        return {
            "lesson":     self.COIN_LESSON_COMPLETE,
            "quiz":       self.COIN_QUIZ_PASS,
            "assignment": self.COIN_ASSIGNMENT_COMPLETE,
            "project":    self.COIN_PROJECT_COMPLETE,
            "course":     self.COIN_COURSE_COMPLETE,
        }


settings = Settings()