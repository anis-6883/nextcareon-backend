"""app/background/tasks/achievement_check.py - Achievement check jobs."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import async_session
from app.modules.gamification.models import Achievement, StudentAchievement
from app.modules.users.models import Student


async def check_achievements_job(student_id: str) -> list[str]:
    """
    Background job to check and award achievements.
    Returns list of earned achievement IDs.
    """
    async with async_session() as session:
        student = await session.get(Student, student_id)
        achievements = await session.exec(select(Achievement))
        earned = []
        
        for achievement in achievements:
            # Check achievement criteria
            # Example: quiz_pass_count >= achievement.required_value
            if achievement.name == "First Quiz Completed":
                quiz_count = len(student.quiz_results) if student.quiz_results else 0
                if quiz_count >= achievement.required_value:
                    earned.append(achievement.id)
        
        # Award earned achievements
        for aid in earned:
            sa = StudentAchievement(
                student_id=student_id,
                achievement_id=aid,
            )
            session.add(sa)
        
        await session.commit()
        return earned