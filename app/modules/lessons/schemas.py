"""app/modules/lessons/schemas.py - Lesson-related schemas."""

from typing import Optional
from pydantic import BaseModel


class TTSPayload(BaseModel):
    text: str
    language: str = "en"