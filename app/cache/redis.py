"""app/cache/redis.py - Redis client for caching."""

from redis.asyncio import Redis
from app.core.config import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> Redis:
    """Get Redis client."""
    return redis_client
