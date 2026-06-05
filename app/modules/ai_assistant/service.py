"""app/modules/ai_assistant/service.py - AI assistant logic."""

from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.core.exceptions import InsufficientCoinsException


async def ask_ai_question(
    session: AsyncSession,
    student_id: str,
    question: str,
) -> tuple[str, int]:
    """
    Ask AI a question and return answer with coin cost.
    Uses Anthropic Claude for responses.
    """
    # Check coins (100 coins per 10 questions)
    from app.modules.users.models import Student
    student = await session.get(Student, student_id)
    if student.coins < settings.AI_COINS_PER_SESSION:
        raise InsufficientCoinsException()
    
    # Deduct coins
    student.coins -= settings.AI_COINS_PER_SESSION
    await session.add(student)
    
    # Get AI response (stub - integrate Anthropic API)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": question}],
        )
        answer = response.content[0].text
    except Exception:
        answer = f"AI response to: {question}"
    
    # Log usage
    from app.modules.ai_assistant.models import AIUsageLog
    log = AIUsageLog(
        student_id=student_id,
        question=question,
        answer=answer,
        coin_cost=settings.AI_COINS_PER_SESSION,
    )
    session.add(log)
    await session.commit()
    
    return answer, settings.AI_COINS_PER_SESSION