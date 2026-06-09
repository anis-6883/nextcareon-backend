"""app/modules/gamification/background.py - Background achievement checker."""

import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.gamification.models import (
    Achievement,
    UserAchievement,
    UserBalance,
    MetricType,
)
from app.cache.redis import redis_client
from app.db.engine import engine


async def check_achievements_for_student(student_id: str):
    """Background task to check and unlock achievements for a student."""
    async with AsyncSession(engine) as session:
        achievements = (await session.execute(select(Achievement))).all()
        user_achievements = (await session.execute(
            select(UserAchievement).where(UserAchievement.student_id == student_id)
        )).all()
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        
        for achievement in achievements:
            if achievement.id in unlocked_ids:
                continue
            
            threshold_met = False
            
            if achievement.metric_type == MetricType.COINS_EARNED:
                balance = (await session.execute(
                    select(UserBalance).where(UserBalance.student_id == student_id)
                )).first()
                threshold_met = balance and balance.current_balance >= achievement.target_threshold
            
            if threshold_met:
                user_achievement = UserAchievement(
                    student_id=student_id,
                    achievement_id=achievement.id,
                )
                session.add(user_achievement)
        
        await session.commit()


async def batch_check_achievements():
    """Batch check achievements for all students with recent activity."""
    async with AsyncSession(engine) as session:
        students = (await session.execute(select(UserBalance))).all()
        for student in students:
            await check_achievements_for_student(str(student.student_id))
