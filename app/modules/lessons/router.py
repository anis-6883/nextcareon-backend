"""app/modules/lessons/router.py - Lesson endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.service import get_lesson_tts_audio
from app.db.engine import get_session
from app.core.dependencies import get_current_student

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}/tts")
async def get_tts_audio(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    return await get_lesson_tts_audio(session, lesson_id)
