import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.redis_client import get_sync_pool, ping_redis
from app.db.session import engine
from app.api.v1 import router as api_router

logger = logging.getLogger(__name__)



# Lifespan — runs on startup and shutdown

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    logger.info("Starting %s v%s [%s]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)

    # Verify DB connection
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("PostgreSQL connected.")
    except Exception as exc:
        logger.error("PostgreSQL connection failed: %s", exc)
        raise

    # Verify Redis connection
    if ping_redis():
        logger.info("Redis connected.")
    else:
        logger.error("Redis connection failed — check REDIS_URL in .env")
        raise RuntimeError("Redis unavailable")

    # In development, auto-create tables (skip in production — use Alembic)
    if settings.ENVIRONMENT == "development":
        from app.db.init_db import create_db_and_tables
        create_db_and_tables()

    yield  # Application runs here

    
    logger.info("Shutting down %s...", settings.APP_NAME)
    engine.dispose()
    pool = get_sync_pool()
    pool.disconnect()
    logger.info("Connections closed.")



# App instance

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-driven career development platform for Bangladeshi students.",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes

app.include_router(api_router.api_router)


# Health check — always public, no auth

@app.get("/health", tags=["system"])
def health_check():
    """
    Returns DB and Redis connectivity status.
    Used by load balancers and the GitHub Actions CI health gate.
    """
    db_ok = False
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    redis_ok = ping_redis()

    status = "healthy" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "postgresql": "up" if db_ok else "down",
            "redis": "up" if redis_ok else "down",
        },
    }


@app.get("/", tags=["system"], include_in_schema=False)
def root():
    return {"message": f"Welcome to {settings.APP_NAME} API", "docs": "/docs"}
