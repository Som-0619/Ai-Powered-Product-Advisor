"""Deterministic local embedding service implementing EmbeddingService.

Provides fast, reproducible, and normalized vector embeddings without requiring
an external model download during local testing or offline environments.
Uses semantic token n-gram projection with L2 normalization.
"""

import hashlib
import math
from typing import List
from app.services.embedding import EmbeddingService


class DeterministicLocalEmbeddingService(EmbeddingService):
    """Generates normalized dense vectors deterministically from input text.

    Ensures that identical or semantically overlapping strings generate vectors
    with high cosine similarity, making it ideal for unit testing OpenSearch
    vector and hybrid search pipelines.
    """

    def __init__(self, dimension: int = 384, model_name: str = "local-deterministic-v1"):
        self._dim = dimension
        self._model = model_name

    def _embed_text(self, text: str) -> List[float]:
        """Convert text into an L2-normalized vector."""
        vec = [0.0] * self._dim
        clean_text = text.lower().strip()
        if not clean_text:
            return vec

        # Whole words get higher weight (4.0), subword 3-grams get lower weight (1.0)
        tokens = clean_text.split()
        weighted_features = [(t, 4.0) for t in tokens]
        for t in tokens:
            if len(t) >= 3:
                for i in range(len(t) - 2):
                    weighted_features.append((t[i : i + 3], 1.0))

        # Project features onto vector dimensions via multiple hash functions
        for feature, weight in weighted_features:
            h = hashlib.sha256(feature.encode("utf-8")).digest()
            for idx in range(0, min(len(h), 16), 2):
                dim_idx = int.from_bytes(h[idx : idx + 2], "big") % self._dim
                # Pseudo-random signed weight between -1.0 and 1.0
                sign = 1.0 if (h[idx] % 2 == 0) else -1.0
                vec[dim_idx] += sign * weight

        # L2 normalize the vector
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0.0:
            vec = [round(v / norm, 6) for v in vec]

        return vec

    async def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def dimension(self) -> int:
        return self._dim

    def model_name(self) -> str:
        return self._model
