"""scripts/embed_all.py - Embed all lessons for RAG."""

import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import async_session
from app.modules.courses.models import Lesson
from app.background.tasks.embed_lesson import embed_lesson_content


async def embed_all_lessons() -> None:
    """Generate embeddings for all lessons."""
    async with async_session() as session:
        lessons = await session.execute(select(Lesson))
        lessons = lessons.all()
        
        for lesson in lessons:
            if lesson.content_text:
                embedding = await embed_lesson_content(lesson.content_text)
                # Store embedding in lesson.tts_audio_url or separate field
                # For pgvector: lesson.embedding = embedding
                print(f"Embedded lesson {lesson.id}")


if __name__ == "__main__":
    asyncio.run(embed_all_lessons())
