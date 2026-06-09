"""app/modules/lessons/service.py - Lesson service."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.models import Lesson
from app.core.exceptions import NotFoundException


async def get_lesson_by_id(session: AsyncSession, lesson_id: str) -> Lesson:
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFoundException(resource="Lesson")
    return lesson
