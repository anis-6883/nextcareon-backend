"""app/background/tasks/embed_lesson.py - Lesson embedding jobs."""

from app.core.config import settings


async def embed_lesson_content(lesson_text: str) -> list[float]:
    """
    Generate embeddings for lesson content using OpenAI.
    Used for RAG-based AI assistant.
    """
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=lesson_text,
        )
        return response.data[0].embedding
    except Exception:
        return [0.0] * settings.OPENAI_EMBEDDING_DIMENSIONS
