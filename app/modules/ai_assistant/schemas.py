"""app/modules/ai_assistant/schemas.py - Pydantic schemas for AI assistant."""

from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request schema for AI chat."""
    message: str
    conversation_id: Optional[str] = None
    lesson_id: Optional[str] = None
    course_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for AI chat."""
    answer: str


class ExplainQuizRequest(BaseModel):
    """Request schema for quiz explanation."""
    question_text: str
    selected_option: str
    correct_option: str
    lesson_id: Optional[str] = None


class ProjectSuggestionsRequest(BaseModel):
    """Request schema for project suggestions."""
    course_id: str