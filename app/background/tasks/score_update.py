"""app/background/tasks/score_update.py - Async score update jobs."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import async_session
from app.modules.career_score.models import StudentCourseProgress
from app.modules.career_score.calculator import calculate_career_readiness_score


async def update_course_progress_job(student_id: str, course_id: str) -> None:
    """
    Background job to recalculate student course progress.
    Called when lesson/quiz is completed.
    """
    async with async_session() as session:
        result = await session.execute(
            select(StudentCourseProgress)
            .where(
                StudentCourseProgress.student_id == student_id,
                StudentCourseProgress.course_id == course_id,
            )
        )
        progress = result.first()
        if progress:
            # Recalculate based on completed chapters
            # This would be expanded to count completed chapters
            await session.commit()
