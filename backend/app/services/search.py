"""Abstract base class for Search Service across all search modes and domain indexes."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.schemas.search import (
    SearchResponse,
    ProductFilters,
    ComponentFilters,
    ReviewFilters,
    DocumentFilters,
)


class SearchService(ABC):
    """Search service abstraction supporting BM25, k-NN Vector, and Hybrid retrieval."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection to the search cluster."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the search cluster."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify cluster health and index availability."""
        pass

    @abstractmethod
    async def create_all_indices(self, recreate: bool = False) -> Dict[str, bool]:
        """Create all four core indexes (products, components, reviews, documents)."""
        pass

    @abstractmethod
    async def index_document(
        self,
        index_name: str,
        doc_id: str,
        document: Dict[str, Any],
        generate_embedding: bool = True,
    ) -> bool:
        """Index a single document, optionally generating dense vector embedding."""
        pass

    @abstractmethod
    async def bulk_index(
        self,
        index_name: str,
        documents: List[Dict[str, Any]],
        generate_embedding: bool = True,
    ) -> int:
        """Index multiple documents in bulk."""
        pass

    @abstractmethod
    async def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document by ID."""
        pass

    # Core Query Modes
    @abstractmethod
    async def keyword_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Execute BM25 keyword search with technical term matching."""
        pass

    @abstractmethod
    async def semantic_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Execute dense vector k-NN semantic search."""
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Execute hybrid retrieval fusing BM25 keyword scores and vector similarity."""
        pass

    # Stage 4 Canonical Product Search Methods
    @abstractmethod
    async def search_keyword(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Search products using BM25 keyword matching."""
        pass

    @abstractmethod
    async def search_vector(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Search products using dense vector k-NN semantic similarity."""
        pass

    @abstractmethod
    async def search_hybrid(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        keyword_weight: Optional[float] = None,
        vector_weight: Optional[float] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Search products combining BM25 and vector scores via normalized fusion."""
        pass

    @abstractmethod
    async def get_product_candidates(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: str = "hybrid",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve candidate product IDs and search scores/metadata from OpenSearch."""
        pass

