"""app/modules/courses/service.py - Course business logic."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.models import Course, Chapter, Lesson
from app.core.exceptions import NotFoundException


async def get_course_by_slug(session: AsyncSession, slug: str) -> Optional[Course]:
    """Get course by slug."""
    result = await session.exec(select(Course).where(Course.slug == slug))
    return result.first()


async def get_course_by_id(session: AsyncSession, course_id: str) -> Course:
    """Get course by ID or raise 404."""
    course = await session.get(Course, course_id)
    if not course:
        raise NotFoundException(resource="Course")
    return course


async def get_courses(session: AsyncSession, skip: int = 0, limit: int = 20):
    """Get paginated list of courses."""
    result = await session.exec(select(Course).offset(skip).limit(limit))
    return result.all()


async def create_course(
    session: AsyncSession,
    title: str,
    slug: str,
    description: str = "",
    difficulty: str = "beginner",
    estimated_hours: int = 0,
) -> Course:
    """Create a new course."""
    course = Course(
        title=title,
        slug=slug,
        description=description,
        difficulty=difficulty,
        estimated_hours=estimated_hours,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def get_chapters_by_course(
    session: AsyncSession, course_id: str, skip: int = 0, limit: int = 100
):
    """Get all chapters for a course."""
    result = await session.exec(
        select(Chapter)
        .where(Chapter.course_id == course_id)
        .order_by(Chapter.order_index)
        .offset(skip)
        .limit(limit)
    )
    return result.all()


async def get_lessons_by_chapter(
    session: AsyncSession, chapter_id: str, skip: int = 0, limit: int = 100
):
    """Get all lessons for a chapter."""
    result = await session.exec(
        select(Lesson)
        .where(Lesson.chapter_id == chapter_id)
        .order_by(Lesson.order_index)
        .offset(skip)
        .limit(limit)
    )
    return result.all()


async def enroll_student_in_course(
    session: AsyncSession,
    student_id: str,
    course_id: str,
):
    """Enroll student in course (creates StudentCourseProgress)."""
    from app.modules.career_score.models import StudentCourseProgress
    enrollment = StudentCourseProgress(
        student_id=student_id,
        course_id=course_id,
    )
    session.add(enrollment)
    await session.commit()
    return enrollment