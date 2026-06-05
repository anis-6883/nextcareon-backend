"""app/modules/quizzes/router.py - Quiz endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.quizzes.schemas import QuizRead, QuizSubmit, QuizResultRead
from app.modules.quizzes.grader import grade_quiz_attempt
from app.db.engine import get_session
from app.core.dependencies import get_current_student

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(quiz_id: str, session: AsyncSession = Depends(get_session)):
    """Get quiz with questions (without correct answers)."""
    from app.modules.quizzes.models import Quiz
    from app.modules.quizzes.schemas import QuizQuestionRead
    
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Quiz")
    
    questions = [
        QuizQuestionRead(
            id=q.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
        )
        for q in quiz.questions
    ]
    
    return QuizRead(
        id=quiz.id,
        pass_score=quiz.pass_score,
        questions=questions,
    )


@router.post("/{quiz_id}/submit", response_model=QuizResultRead)
async def submit_quiz(
    quiz_id: str,
    data: QuizSubmit,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    """Submit quiz answers and get result."""
    answers = {a.question_id: a.selected_option for a in data.answers}
    result = await grade_quiz_attempt(session, str(student.id), quiz_id, answers)
    return QuizResultRead(
        score=result.score,
        passed=result.passed,
        attempted_at=result.attempted_at,
    )