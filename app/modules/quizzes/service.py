"""app/modules/quizzes/service.py - Quiz business logic."""

import time
from datetime import datetime
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.models import Quiz, Question, QuizAttempt
from app.core.exceptions import NotFoundException
from app.cache.redis import redis_client


async def get_quiz_by_id(session: AsyncSession, quiz_id: str) -> Quiz:
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        raise NotFoundException(resource="Quiz")
    return quiz


async def create_quiz(
    session: AsyncSession,
    chapter_id: str,
    **kwargs
) -> Quiz:
    existing = await session.execute(
        select(Quiz).where(Quiz.chapter_id == chapter_id)
    )
    if existing.first():
        raise ValueError("Quiz already exists for this chapter")
    
    questions_data = kwargs.pop("questions", [])
    
    quiz = Quiz(chapter_id=chapter_id, **kwargs)
    session.add(quiz)
    await session.commit()
    await session.refresh(quiz)
    
    for q in questions_data:
        question = Question(quiz_id=quiz.id, **q)
        session.add(question)
    await session.commit()
    
    return quiz


async def submit_quiz(
    session: AsyncSession,
    student_id: str,
    quiz_id: str,
    answers: List[dict]
) -> QuizAttempt:
    cache_key = f"quiz_cooldown:{student_id}:{quiz_id}"
    last_attempt = await redis_client.get(cache_key)
    
    quiz = await get_quiz_by_id(session, quiz_id)
    
    questions_dict = {}
    for q in await session.execute(select(Question).where(Question.quiz_id == quiz_id)):
        questions_dict[q.id] = q
    
    correct_count = 0
    for answer in answers:
        q_id = answer.get("question_id")
        selected = answer.get("selected_option")
        if q_id in questions_dict:
            if questions_dict[q_id].correct_option == selected:
                correct_count += 1
    
    score = int((correct_count / len(questions_dict)) * 100) if questions_dict else 0
    passed = score >= quiz.pass_score
    
    attempt_number = 1
    existing_attempts = await session.execute(
        select(QuizAttempt).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.quiz_id == quiz_id
        )
    )
    if existing_attempts.first():
        attempt_number = len(existing_attempts.all()) + 1
    
    attempt = QuizAttempt(
        student_id=student_id,
        quiz_id=quiz_id,
        score=score,
        passed=passed,
        attempt_number=attempt_number,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    
    await redis_client.setex(cache_key, 300, str(int(time.time())))
    
    return attempt


async def get_student_quiz_attempts(
    session: AsyncSession,
    student_id: str,
    quiz_id: str
) -> List[QuizAttempt]:
    result = await session.execute(
        select(QuizAttempt)
        .where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.quiz_id == quiz_id
        )
        .order_by(QuizAttempt.attempted_at)
    )
    return result.all()
