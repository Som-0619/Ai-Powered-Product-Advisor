"""Abstract base class for Embedding Service.

Defines the contract for vector embedding providers. Allows SearchService
to remain completely decoupled from specific model providers (e.g. Ollama, Bedrock, local).
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingService(ABC):
    """Embedding service abstraction for generating dense vector representations."""

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate a dense vector embedding for a single query string.

        Args:
            text: Query text to embed.

        Returns:
            Normalized vector of floats.
        """
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings for a batch of documents.

        Args:
            texts: List of document strings to embed.

        Returns:
            List of normalized float vectors.
        """
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Return the fixed dimensionality of the generated vectors."""
        pass

    @abstractmethod
    def model_name(self) -> str:
        """Return the canonical identifier of the embedding model."""
        pass
