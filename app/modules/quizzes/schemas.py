"""app/modules/quizzes/schemas.py - Quiz schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class QuizQuestionRead(BaseModel):
    id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class QuizRead(BaseModel):
    id: str
    pass_score: int
    questions: List[QuizQuestionRead]


class QuizAnswer(BaseModel):
    question_id: str
    selected_option: str


class QuizSubmit(BaseModel):
    answers: List[QuizAnswer]


class QuizResultRead(BaseModel):
    score: int
    passed: bool
    attempted_at: datetime