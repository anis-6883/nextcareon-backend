"""app/modules/courses/router.py - Course endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.service import get_courses, get_course_by_id, create_course
from app.modules.courses.schemas import CourseCreate, CourseRead
from app.db.engine import get_session

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseRead])
async def list_courses(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """List all courses."""
    courses = await get_courses(session, skip=skip, limit=limit)
    return [CourseRead.model_validate(c) for c in courses]


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get course by ID."""
    course = await get_course_by_id(session, course_id)
    return CourseRead.model_validate(course)