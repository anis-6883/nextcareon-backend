"""app/modules/ai_assistant/service.py - AI assistant logic."""

import time
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.core.exceptions import InsufficientCoinsException
from app.db.engine import engine

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None

from app.modules.ai_assistant.models import (
    AiConversation,
    AiMessage,
    AiUsageLog,
    LessonChunks,
)
from app.modules.gamification.service import get_balance, withdraw_coins
from app.modules.ai_assistant.rag import retrieve_relevant_chunks


COIN_COST_PER_QUESTION = 10
AI_QUESTIONS_PER_COIN = 10


async def check_rate_limit(student_id: str) -> bool:
    """Check if student is within rate limit (10 requests per 60 seconds)."""
    from app.cache.redis import redis_client
    key = f"rate_limit:{student_id}"
    current = await redis_client.get(key)
    if current is None:
        await redis_client.setex(key, 60, 1)
        return True
    if int(current) >= 10:
        return False
    await redis_client.incr(key)
    return True


async def create_or_get_conversation(
    session: AsyncSession,
    student_id: str,
    course_id: Optional[str] = None,
) -> AiConversation:
    """Create or retrieve existing conversation."""
    conv = (await session.execute(
        select(AiConversation).where(
            AiConversation.student_id == student_id,
            AiConversation.course_id == course_id,
        )
    )).first()
    
    if not conv:
        conv = AiConversation(student_id=student_id, course_id=course_id)
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
    
    return conv


async def chat_with_ai(
    session: AsyncSession,
    student_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    lesson_id: Optional[str] = None,
    course_id: Optional[str] = None,
) -> str:
    """Chat with AI assistant using RAG."""
    if not await check_rate_limit(student_id):
        raise Exception("Rate limit exceeded. Please wait before asking more questions.")
    
    balance = await get_balance(session, student_id)
    if balance < COIN_COST_PER_QUESTION:
        raise InsufficientCoinsException()
    
    conv = await create_or_get_conversation(session, student_id, course_id)
    
    user_message = AiMessage(conversation_id=conv.id, role="user", content=message, tokens_used=0)
    session.add(user_message)
    await session.commit()
    await session.refresh(user_message)
    
    history = (await session.execute(
        select(AiMessage)
        .where(AiMessage.conversation_id == conv.id)
        .order_by(AiMessage.created_at.desc())
        .limit(6)
    )).all()
    history = list(reversed(history))
    
    context_chunks = await retrieve_relevant_chunks(message, lesson_id, course_id, top_k=4)
    context_text = "\n".join([c.content_text for c in context_chunks]) if context_chunks else ""
    
    if not HAS_OPENAI:
        return f"AI response (stub): {message}"
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    system_prompt = f"""<context>{context_text}</context>
<instructions>You are Nextcareon's dedicated technical assistant. Explain code queries carefully. Stick strictly to the course documentation provided within the context tags. If information cannot be found, politely state your bounds.</instructions>"""
    
    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": message})
    
    start_time = time.time()
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        max_tokens=settings.OPENAI_CHAT_MAX_TOKENS,
        temperature=0.1,
        messages=messages,
    )
    response_time = int((time.time() - start_time) * 1000)
    
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    await withdraw_coins(
        session, student_id, COIN_COST_PER_QUESTION,
        "AI_GATE_PURCHASE", "AI assistant question"
    )
    
    assistant_message = AiMessage(
        conversation_id=conv.id,
        role="assistant",
        content=answer,
        tokens_used=tokens,
    )
    session.add(assistant_message)
    await session.commit()
    
    log = AiUsageLog(
        student_id=student_id,
        endpoint_accessed="/chat",
        total_tokens=tokens,
        response_time_ms=response_time,
    )
    session.add(log)
    await session.commit()
    
    return answer


async def explain_quiz_answer(
    session: AsyncSession,
    student_id: str,
    question_text: str,
    selected_option: str,
    correct_option: str,
    lesson_id: Optional[str] = None,
) -> str:
    """Explain quiz answer using RAG."""
    if not await check_rate_limit(student_id):
        raise Exception("Rate limit exceeded.")
    
    balance = await get_balance(session, student_id)
    if balance < COIN_COST_PER_QUESTION:
        raise InsufficientCoinsException()
    
    context_chunks = await retrieve_relevant_chunks(question_text, lesson_id, top_k=4)
    context_text = "\n".join([c.content_text for c in context_chunks]) if context_chunks else ""
    
    if not HAS_OPENAI:
        return f"Explanation: The correct answer is {correct_option}."
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""<context>{context_text}</context>
<instructions>Explain why the correct answer is {correct_option}, and explain the logical gap in choosing {selected_option}.</instructions>"""
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": question_text},
    ]
    
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        max_tokens=500,
        temperature=0.1,
        messages=messages,
    )
    
    await withdraw_coins(session, student_id, COIN_COST_PER_QUESTION, "AI_GATE_PURCHASE", "Quiz explanation")
    
    return response.choices[0].message.content


async def generate_project_suggestions(
    session: AsyncSession,
    student_id: str,
    course_id: str,
) -> str:
    """Generate project suggestions for a course."""
    if not await check_rate_limit(student_id):
        raise Exception("Rate limit exceeded.")
    
    balance = await get_balance(session, student_id)
    if balance < COIN_COST_PER_QUESTION:
        raise InsufficientCoinsException()
    
    if not HAS_OPENAI:
        return "Project suggestions (stub)"
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = """Based on the course curriculum, generate 3 practical portfolio project ideas. Each should have: Name, Core Architecture, and Real-world Deployment Challenges."""
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Course ID: {course_id}"},
    ]
    
    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        max_tokens=1000,
        temperature=0.2,
        messages=messages,
    )
    
    await withdraw_coins(session, student_id, COIN_COST_PER_QUESTION, "AI_GATE_PURCHASE", "Project suggestions")
    
    return response.choices[0].message.content
