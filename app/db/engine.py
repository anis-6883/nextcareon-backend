"""app/db/engine.py - Async database engine setup."""

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """Dependency for FastAPI to get async database session."""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables (for development)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables (for development/testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)