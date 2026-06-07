"""app/modules/quizzes/schemas.py - Quiz schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str


class QuizCreate(BaseModel):
    chapter_id: str
    pass_score: int = 60
    xp_reward: int = 100
    coin_reward: int = 25
    questions: List[QuestionCreate] = []


class QuizQuestionRead(BaseModel):
    id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class QuizRead(BaseModel):
    id: str
    chapter_id: str
    pass_score: int
    xp_reward: int
    coin_reward: int
    questions: List[QuizQuestionRead] = []

    class Config:
        from_attributes = True


class QuizAnswer(BaseModel):
    question_id: str
    selected_option: str


class QuizSubmit(BaseModel):
    quiz_id: str
    answers: List[QuizAnswer]


class QuizResultRead(BaseModel):
    id: str
    score: int
    passed: bool
    attempt_number: int
    attempted_at: datetime

    class Config:
        from_attributes = True