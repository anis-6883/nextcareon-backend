"""app/modules/quizzes/grader.py - Quiz auto-grading logic."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.quizzes.models import Quiz, QuizQuestion, StudentQuizResult
from app.modules.users.service import update_student_xp
from app.core.exceptions import NotFoundException, BadRequestException


async def grade_quiz_attempt(
    session: AsyncSession,
    student_id: str,
    quiz_id: str,
    answers: dict[str, str],  # question_id -> selected_option
) -> StudentQuizResult:
    """
    Grade a quiz attempt.
    
    Returns the student's quiz result with score and pass status.
    """
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        raise NotFoundException(resource="Quiz")
    
    # Get all questions for the quiz
    questions = await session.execute(
        select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
    )
    questions = questions.all()
    
    # Calculate score
    correct = 0
    total = len(questions)
    
    for q in questions:
        selected = answers.get(q.id, "")
        if selected.upper() == q.correct_option.upper():
            correct += 1
    
    score = int((correct / total) * 100) if total > 0 else 0
    passed = score >= quiz.pass_score
    
    # Create result
    result = StudentQuizResult(
        student_id=student_id,
        quiz_id=quiz_id,
        score=score,
        passed=passed,
    )
    session.add(result)
    
    # Award coins if passed
    if passed:
        await update_student_xp(session, student_id, quiz.xp_reward, quiz.coin_reward)
    
    await session.commit()
    await session.refresh(result)
    return result


async def get_quiz_result(
    session: AsyncSession, student_id: str, quiz_id: str
) -> Optional[StudentQuizResult]:
    """Get student's quiz result."""
    result = await session.execute(
        select(StudentQuizResult)
        .where(
            StudentQuizResult.student_id == student_id,
            StudentQuizResult.quiz_id == quiz_id,
        )
    )
    return result.first()
