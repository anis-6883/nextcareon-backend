"""app/modules/quizzes/router.py - Quiz endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.quizzes.service import (
    create_quiz, get_quiz_by_id, submit_quiz, get_student_quiz_attempts
)
from app.modules.quizzes.schemas import QuizCreate, QuizRead, QuizSubmit, QuizResultRead
from app.db.engine import get_session
from app.core.dependencies import get_current_student, get_current_admin
from typing import List

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/{chapter_id}", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
async def create_new_quiz(
    chapter_id: str,
    quiz: QuizCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    return await create_quiz(session, chapter_id, **quiz.model_dump())


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(
    quiz_id: str,
    session: AsyncSession = Depends(get_session),
):
    return await get_quiz_by_id(session, quiz_id)


@router.post("/submit", response_model=QuizResultRead)
async def submit_quiz_endpoint(
    submission: QuizSubmit,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    return await submit_quiz(session, student.id, submission.quiz_id, submission.answers)


@router.get("/attempts/{quiz_id}", response_model=List[QuizResultRead])
async def get_quiz_attempts(
    quiz_id: str,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    return await get_student_quiz_attempts(session, student.id, quiz_id)