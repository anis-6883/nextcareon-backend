"""app/modules/gamification/leaderboard.py - Leaderboard functionality."""

from typing import Optional
from redis.asyncio import Redis
from app.core.config import settings


LEADERBOARD_KEY = "leaderboard:top_students"


async def get_leaderboard(redis: Redis, limit: int = 50) -> list[tuple]:
    """Get top N students by XP."""
    return await redis.zrevrange(LEADERBOARD_KEY, 0, limit - 1, withscores=True)


async def update_student_xp(redis: Redis, student_id: str, xp: int) -> None:
    """Update student XP in leaderboard."""
    await redis.zincrby(LEADERBOARD_KEY, xp, student_id)


async def get_student_rank(redis: Redis, student_id: str) -> Optional[int]:
    """Get student's rank in leaderboard."""
    rank = await redis.zrevrank(LEADERBOARD_KEY, student_id)
    return rank + 1 if rank is not None else None
