"""app/modules/ai_assistant/embeddings.py - Embedding utilities for RAG."""

import json
from typing import List
from app.core.config import settings

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None


class EmbeddingService:
    """Service for generating embeddings using OpenAI."""
    
    def __init__(self):
        if HAS_OPENAI:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI."""
        if not HAS_OPENAI:
            return [0.0] * settings.OPENAI_EMBEDDING_DIMENSIONS
        response = self.client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    
    async def create_embedding_json(self, text: str) -> str:
        """Create embedding and return as JSON string."""
        embedding = await self.create_embedding(text)
        return json.dumps(embedding)
    
    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            emb = await self.create_embedding(text)
            embeddings.append(emb)
        return embeddings


embedding_service = EmbeddingService()
