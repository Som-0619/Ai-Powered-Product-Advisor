"""Local Ollama Embedding adapter implementing EmbeddingService."""

from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.services.embedding import EmbeddingService


class LocalOllamaEmbeddingService(EmbeddingService):
    """Ollama embedding provider for local model execution."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        dimension: int = 768,
    ):
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._model = model or settings.EMBEDDING_MODEL
        self._dimension = dimension
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

    async def embed_query(self, text: str) -> List[float]:
        try:
            payload = {"model": self._model, "prompt": text}
            res = await self._client.post("/api/embeddings", json=payload)
            res.raise_for_status()
            return res.json().get("embedding", [])
        except Exception as exc:
            logger.warning(
                f"Ollama embedding query failed for model '{self._model}': {exc}"
            )
            # Return empty or fallback vector if Ollama is unreachable/model not pulled
            return [0.0] * self._dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            emb = await self.embed_query(text)
            embeddings.append(emb)
        return embeddings

    def dimension(self) -> int:
        return self._dimension

    def model_name(self) -> str:
        return self._model
