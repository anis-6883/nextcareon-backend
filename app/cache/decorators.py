"""app/cache/decorators.py - Redis caching decorators."""

import json
from functools import wraps
from typing import Any, Callable, Optional
from redis.asyncio import Redis
from app.cache.redis import get_redis
from app.cache.keys import (
    CAREER_PATHS_LIST, CAREER_PATH_DETAIL,
    CAREER_PATH_MARKET_DATA, JOB_OPENINGS,
    COMPANIES, ALUMNI_SHOWCASE
)


def cache_result(ttl_seconds: int = 3600):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis: Redis = await get_redis()
            cache_key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            
            if result is not None:
                await redis.setex(cache_key, ttl_seconds, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator


async def invalidate_all_career_cache() -> None:
    redis: Redis = await get_redis()
    patterns = [
        "cache:career_paths*",
        "cache:career_path*",
        "cache:job_openings*",
        "cache:companies*",
        "cache:alumni_showcase*",
        "cache:salary_ranges*"
    ]
    for pattern in patterns:
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)


async def invalidate_career_explorer_cache(path_id: Optional[str] = None) -> None:
    redis: Redis = await get_redis()
    
    await redis.delete(CAREER_PATHS_LIST)
    
    if path_id:
        key = CAREER_PATH_DETAIL.format(path_id=path_id)
        await redis.delete(key)
        key = CAREER_PATH_MARKET_DATA.format(path_id=path_id)
        await redis.delete(key)
    
    await redis.delete(JOB_OPENINGS)
    await redis.delete(COMPANIES)
    await redis.delete(ALUMNI_SHOWCASE)
