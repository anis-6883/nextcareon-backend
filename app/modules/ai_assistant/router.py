"""app/modules/ai_assistant/router.py - AI assistant API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.core.dependencies import get_current_student
from app.modules.ai_assistant.service import (
    chat_with_ai,
    explain_quiz_answer,
    generate_project_suggestions,
)
from app.modules.ai_assistant.schemas import (
    ChatRequest,
    ChatResponse,
    ExplainQuizRequest,
    ProjectSuggestionsRequest,
)

router = APIRouter(prefix="/ai", tags=["ai-assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Chat with AI assistant."""
    try:
        answer = await chat_with_ai(
            session=session,
            student_id=str(student.id),
            message=request.message,
            conversation_id=request.conversation_id,
            lesson_id=request.lesson_id,
            course_id=request.course_id,
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/explain-quiz")
async def explain_quiz_endpoint(
    request: ExplainQuizRequest,
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Explain quiz answer using RAG."""
    try:
        explanation = await explain_quiz_answer(
            session=session,
            student_id=str(student.id),
            question_text=request.question_text,
            selected_option=request.selected_option,
            correct_option=request.correct_option,
            lesson_id=request.lesson_id,
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/generate-projects")
async def generate_projects_endpoint(
    request: ProjectSuggestionsRequest,
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Generate project suggestions for a course."""
    try:
        suggestions = await generate_project_suggestions(
            session=session,
            student_id=str(student.id),
            course_id=request.course_id,
        )
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))