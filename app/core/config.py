from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    APP_NAME: str = "Career_AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | production | testing

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/career_ai"
    DB_ECHO: bool = False          # Set True in dev to log SQL queries
    DB_POOL_SIZE: int = 10         # Base connection pool size
    DB_MAX_OVERFLOW: int = 20      # Extra connections allowed beyond pool_size

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # ------------------------------------------------------------------
    # JWT / Auth
    # ------------------------------------------------------------------
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # OpenAI / AI
    # ------------------------------------------------------------------
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",   # Next.js dev
        "http://127.0.0.1:3000",
    ]

    # ------------------------------------------------------------------
    # Gamification constants
    # ------------------------------------------------------------------
    # XP required to reach each level (index = level number)
    XP_LEVEL_THRESHOLDS: list[int] = [
        0,      # level 1
        500,    # level 2
        1500,   # level 3
        3000,   # level 4
        5500,   # level 5
        9000,   # level 6
        14000,  # level 7
        21000,  # level 8
        30000,  # level 9
        42000,  # level 10
    ]
    STREAK_BONUS_DAYS: list[int] = [7, 30, 100]
    STREAK_BONUS_COINS: list[int] = [50, 200, 1000]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()