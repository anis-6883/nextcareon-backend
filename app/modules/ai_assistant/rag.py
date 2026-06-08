"""app/modules/ai_assistant/rag.py - RAG retrieval engine."""

import json
from typing import List, Optional
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import engine
from app.modules.ai_assistant.models import LessonChunks
from app.modules.ai_assistant.embeddings import embedding_service


async def retrieve_relevant_chunks(
    query_text: str,
    lesson_id: Optional[str] = None,
    course_id: Optional[str] = None,
    top_k: int = 4,
) -> List[LessonChunks]:
    """Retrieve relevant lesson chunks using vector similarity."""
    query_embedding = await embedding_service.create_embedding(query_text)
    query_vec = json.dumps(query_embedding)
    
    async with AsyncSession(engine) as session:
        if lesson_id:
            results = await session.execute(
                text("""
                    SELECT * FROM lesson_chunks 
                    WHERE lesson_id = :lesson_id 
                    ORDER BY embedding <=> :query_vec::vector 
                    LIMIT :top_k
                """),
                {"lesson_id": lesson_id, "query_vec": query_vec, "top_k": top_k}
            )
        elif course_id:
            from app.modules.courses.models import Lesson
            results = await session.execute(
                text("""
                    SELECT lc.* FROM lesson_chunks lc
                    JOIN lessons l ON lc.lesson_id = l.id
                    WHERE l.course_id = :course_id
                    ORDER BY lc.embedding <=> :query_vec::vector
                    LIMIT :top_k
                """),
                {"course_id": course_id, "query_vec": query_vec, "top_k": top_k}
            )
        else:
            results = await session.execute(
                text("""
                    SELECT * FROM lesson_chunks 
                    ORDER BY embedding <=> :query_vec::vector 
                    LIMIT :top_k
                """),
                {"query_vec": query_vec, "top_k": top_k}
            )
        
        return [LessonChunks(**row._mapping) for row in results]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks