"""Local OpenSearch adapter implementing SearchService.

Supports:
1. BM25 keyword search with technical token preservation (e.g. '3.3V', 'I2C', 'ESP32')
2. Dense vector k-NN search via OpenSearch k-NN plugin (HNSW)
3. Hybrid search combining BM25 and vector scores via Reciprocal Rank Fusion / linear weighting
4. Metadata filtering across products, components, reviews, and documents
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from opensearchpy import OpenSearch, helpers

from app.core.config import settings
from app.core.logging import logger
from app.schemas.search import (
    SearchHit,
    SearchResponse,
    ProductFilters,
    ComponentFilters,
    ReviewFilters,
    DocumentFilters,
)
from app.services.embedding import EmbeddingService
from app.services.search import SearchService
from app.adapters.local.local_embedding import DeterministicLocalEmbeddingService
from app.retrieval.index_manager import INDEX_MAPPINGS


class LocalOpenSearchService(SearchService):
    """Production-grade local OpenSearch adapter."""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self._client: Optional[OpenSearch] = None
        # Decoupled embedding service injected via DI (defaults to deterministic local)
        self._embedding: EmbeddingService = (
            embedding_service or DeterministicLocalEmbeddingService(dimension=384)
        )

    async def connect(self) -> None:
        """Connect to the OpenSearch cluster."""
        if not self._client:
            auth = None
            if settings.OPENSEARCH_USE_SSL and settings.OPENSEARCH_USERNAME:
                auth = (settings.OPENSEARCH_USERNAME, settings.OPENSEARCH_PASSWORD)

            self._client = OpenSearch(
                hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
                http_auth=auth,
                use_ssl=settings.OPENSEARCH_USE_SSL,
                verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
                ssl_show_warn=False,
            )
            logger.info(
                "Connected to OpenSearch cluster",
                extra={"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT},
            )

    async def disconnect(self) -> None:
        """Disconnect from OpenSearch."""
        if self._client:
            await asyncio.to_thread(self._client.close)
            self._client = None
            logger.info("Disconnected from OpenSearch")

    async def health_check(self) -> Dict[str, Any]:
        """Check cluster and k-NN health."""
        start = time.perf_counter()
        try:
            if not self._client:
                await self.connect()
            info = await asyncio.to_thread(self._client.cluster.health)
            latency = round((time.perf_counter() - start) * 1000, 2)
            cluster_status = info.get("status", "unknown")
            return {
                "status": "ok" if cluster_status in ("green", "yellow") else "degraded",
                "latency_ms": latency,
                "details": {
                    "cluster_name": info.get("cluster_name"),
                    "status": cluster_status,
                    "nodes": info.get("number_of_nodes"),
                },
            }
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    async def create_all_indices(self, recreate: bool = False) -> Dict[str, bool]:
        """Create products, components, reviews, and documents indices with technical mappings."""
        if not self._client:
            await self.connect()

        results = {}
        dim = self._embedding.dimension()

        for index_name, mapping_fn in INDEX_MAPPINGS.items():
            exists = await asyncio.to_thread(self._client.indices.exists, index=index_name)
            if exists and recreate:
                await asyncio.to_thread(self._client.indices.delete, index=index_name)
                exists = False

            if not exists:
                body = mapping_fn(dim=dim)
                await asyncio.to_thread(self._client.indices.create, index=index_name, body=body)
                results[index_name] = True
                logger.info(f"Created OpenSearch index '{index_name}' with dimension {dim}")
            else:
                results[index_name] = False

        return results

    def _get_text_for_embedding(self, index_name: str, document: Dict[str, Any]) -> str:
        """Extract composite text representation for generating semantic vectors."""
        if index_name == "products":
            return f"{document.get('title', '')} {document.get('description', '')} {document.get('brand', '')} {document.get('category', '')}"
        elif index_name == "components":
            parts = [
                document.get("title", ""),
                document.get("description", ""),
                document.get("part_number", ""),
                document.get("component_type", ""),
                document.get("package_type", ""),
                document.get("voltage_display", ""),
                document.get("interface", ""),
                str(document.get("extra_specs", "")),
            ]
            return " ".join(filter(None, parts))
        elif index_name == "reviews":
            return f"{document.get('title', '')} {document.get('body', '')} {document.get('use_case', '')}"
        elif index_name == "documents":
            return f"{document.get('title', '')} {document.get('extracted_text', '')[:1000]}"
        return str(document)

    async def index_document(
        self,
        index_name: str,
        doc_id: str,
        document: Dict[str, Any],
        generate_embedding: bool = True,
    ) -> bool:
        """Index a single document with automated vector embedding."""
        if not self._client:
            await self.connect()

        doc_copy = dict(document)
        if generate_embedding and "embedding" not in doc_copy:
            text = self._get_text_for_embedding(index_name, doc_copy)
            doc_copy["embedding"] = await self._embedding.embed_query(text)

        await asyncio.to_thread(
            self._client.index,
            index=index_name,
            id=doc_id,
            body=doc_copy,
            refresh=True,
        )
        return True

    async def bulk_index(
        self,
        index_name: str,
        documents: List[Dict[str, Any]],
        generate_embedding: bool = True,
    ) -> int:
        """Index multiple documents in bulk."""
        if not self._client:
            await self.connect()
        if not documents:
            return 0

        actions = []
        for doc in documents:
            doc_id = str(doc.get("id") or "")
            doc_copy = dict(doc)
            if generate_embedding and "embedding" not in doc_copy:
                text = self._get_text_for_embedding(index_name, doc_copy)
                doc_copy["embedding"] = await self._embedding.embed_query(text)

            action = {
                "_index": index_name,
                "_source": doc_copy,
            }
            if doc_id:
                action["_id"] = doc_id
            actions.append(action)

        success_count, _ = await asyncio.to_thread(
            helpers.bulk,
            self._client,
            actions,
            refresh=True,
        )
        return success_count

    async def delete_document(self, index_name: str, doc_id: str) -> bool:
        if not self._client:
            await self.connect()
        try:
            await asyncio.to_thread(self._client.delete, index=index_name, id=doc_id, refresh=True)
            return True
        except Exception:
            return False

    def _build_filter_clauses(self, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert a filter dictionary into OpenSearch boolean filter clauses."""
        if not filters:
            return []

        clauses = []
        for key, val in filters.items():
            if val is None:
                continue

            if key in ("min_price", "max_price"):
                # Handle price range
                price_range = {}
                if "min_price" in filters and filters["min_price"] is not None:
                    price_range["gte"] = float(filters["min_price"])
                if "max_price" in filters and filters["max_price"] is not None:
                    price_range["lte"] = float(filters["max_price"])
                if price_range and {"range": {"price": price_range}} not in clauses:
                    clauses.append({"range": {"price": price_range}})

            elif key in ("min_voltage", "max_voltage"):
                # Operating voltage range overlap:
                # component.voltage_min <= query.max_voltage AND component.voltage_max >= query.min_voltage
                min_v = filters.get("min_voltage")
                max_v = filters.get("max_voltage")
                if min_v is not None and {"range": {"voltage_max": {"gte": float(min_v)}}} not in clauses:
                    clauses.append({"range": {"voltage_max": {"gte": float(min_v)}}})
                if max_v is not None and {"range": {"voltage_min": {"lte": float(max_v)}}} not in clauses:
                    clauses.append({"range": {"voltage_min": {"lte": float(max_v)}}})

            elif key == "max_current":
                clauses.append({"range": {"current_max": {"lte": float(val)}}})

            elif key == "min_rating":
                clauses.append({"range": {"rating": {"gte": float(val)}}})

            elif key == "max_fraud_score":
                clauses.append({"range": {"fraud_score": {"lte": float(val)}}})

            elif key == "verified_only" and val is True:
                clauses.append({"term": {"is_verified_purchase": True}})

            elif key == "interface":
                # Matches technical interface terms (e.g. I2C, SPI)
                clauses.append({"match": {"interface": str(val)}})

            elif isinstance(val, bool):
                clauses.append({"term": {key: val}})

            elif isinstance(val, (int, float, str)):
                clauses.append({"term": {key: val}})

        return clauses

    def _get_search_fields(self, index_name: str) -> List[str]:
        """Field boost weights for BM25 keyword searches."""
        if index_name == "products":
            return ["title^3", "model_number^4", "model_number.text^3", "sku^3", "brand^2", "description^1", "category^1"]
        elif index_name == "components":
            return ["part_number^5", "part_number.text^4", "title^4", "description^2", "voltage_display^3", "interface^3", "component_type^2", "package_type^2"]
        elif index_name == "reviews":
            return ["title^3", "body^1", "use_case^2", "sentiment^1"]
        elif index_name == "documents":
            return ["title^3", "extracted_text^1", "doc_type^2"]
        return ["*"]

    async def keyword_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """BM25 Keyword search optimized for technical term matching."""
        if not self._client:
            await self.connect()

        start = time.perf_counter()
        fields = self._get_search_fields(index_name)
        filter_clauses = self._build_filter_clauses(filters)

        if query_text and query_text.strip():
            must_clause: List[Dict[str, Any]] = [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": fields,
                        "type": "best_fields",
                        "operator": "or",
                    }
                }
            ]
        else:
            must_clause = [{"match_all": {}}]

        query_body: Dict[str, Any] = {
            "from": offset,
            "size": limit,
            "query": {
                "bool": {
                    "must": must_clause,
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {},
                    "part_number": {},
                    "body": {},
                    "extracted_text": {},
                }
            },
        }

        if filter_clauses:
            query_body["query"]["bool"]["filter"] = filter_clauses

        raw_res = await asyncio.to_thread(
            self._client.search,
            index=index_name,
            body=query_body,
        )

        latency = round((time.perf_counter() - start) * 1000, 2)
        total_hits = raw_res["hits"]["total"]["value"]
        hits = [
            SearchHit(
                id=h["_id"],
                score=round(float(h["_score"] or 0.0), 4),
                index=h["_index"],
                source=h["_source"],
                highlights=h.get("highlight"),
            )
            for h in raw_res["hits"]["hits"]
        ]

        return SearchResponse(
            total=total_hits,
            hits=hits,
            search_mode="keyword",
            latency_ms=latency,
        )

    async def semantic_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Dense vector k-NN semantic search."""
        if not self._client:
            await self.connect()

        start = time.perf_counter()
        filter_clauses = self._build_filter_clauses(filters)

        if query_text and query_text.strip():
            query_vector = await self._embedding.embed_query(query_text)
            knn_clause: Dict[str, Any] = {
                "embedding": {
                    "vector": query_vector,
                    "k": limit + offset,
                }
            }
            if filter_clauses:
                query_body = {
                    "from": offset,
                    "size": limit,
                    "query": {
                        "bool": {
                            "must": [{"knn": knn_clause}],
                            "filter": filter_clauses,
                        }
                    },
                }
            else:
                query_body = {
                    "from": offset,
                    "size": limit,
                    "query": {"knn": knn_clause},
                }
        else:
            query_body = {
                "from": offset,
                "size": limit,
                "query": {
                    "bool": {
                        "must": [{"match_all": {}}],
                        "filter": filter_clauses,
                    }
                },
            }

        raw_res = await asyncio.to_thread(
            self._client.search,
            index=index_name,
            body=query_body,
        )

        latency = round((time.perf_counter() - start) * 1000, 2)
        total_hits = raw_res["hits"]["total"]["value"]
        hits = [
            SearchHit(
                id=h["_id"],
                score=round(float(h["_score"] or 0.0), 4),
                index=h["_index"],
                source=h["_source"],
            )
            for h in raw_res["hits"]["hits"]
        ]

        return SearchResponse(
            total=total_hits,
            hits=hits,
            search_mode="vector",
            latency_ms=latency,
        )

    async def hybrid_search(
        self,
        index_name: str,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Hybrid search combining BM25 keyword and dense vector similarity.

        Uses Reciprocal Rank Fusion (RRF) with alpha weight:
        final_score = alpha * (1 / (60 + bm25_rank)) + (1 - alpha) * (1 / (60 + vector_rank))
        """
        start = time.perf_counter()

        # Execute BM25 and vector queries concurrently
        bm25_res, vector_res = await asyncio.gather(
            self.keyword_search(index_name, query_text, filters=filters, limit=limit * 2),
            self.semantic_search(index_name, query_text, filters=filters, limit=limit * 2),
        )

        rrf_constant = 60.0
        doc_scores: Dict[str, float] = {}
        doc_data: Dict[str, SearchHit] = {}

        # 1. Process BM25 ranks
        for rank, hit in enumerate(bm25_res.hits):
            score = alpha * (1.0 / (rrf_constant + rank + 1))
            doc_scores[hit.id] = doc_scores.get(hit.id, 0.0) + score
            doc_data[hit.id] = hit

        # 2. Process Vector ranks
        for rank, hit in enumerate(vector_res.hits):
            score = (1.0 - alpha) * (1.0 / (rrf_constant + rank + 1))
            doc_scores[hit.id] = doc_scores.get(hit.id, 0.0) + score
            if hit.id not in doc_data:
                doc_data[hit.id] = hit

        # 3. Sort by combined fused score
        sorted_doc_ids = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)
        paginated_ids = sorted_doc_ids[offset : offset + limit]

        fused_hits: List[SearchHit] = []
        for doc_id in paginated_ids:
            hit = doc_data[doc_id]
            fused_hits.append(
                SearchHit(
                    id=hit.id,
                    score=round(doc_scores[doc_id] * 100.0, 4),  # Scale for readability
                    index=hit.index,
                    source=hit.source,
                    highlights=hit.highlights,
                )
            )

        latency = round((time.perf_counter() - start) * 1000, 2)
        return SearchResponse(
            total=len(sorted_doc_ids),
            hits=fused_hits,
            search_mode="hybrid",
            latency_ms=latency,
        )

    # Domain-specific search methods
    async def search_products(
        self,
        query_text: str,
        mode: str = "hybrid",
        filters: Optional[ProductFilters] = None,
        limit: int = 10,
    ) -> SearchResponse:
        f_dict = filters.model_dump(exclude_none=True) if filters else {}
        if mode == "keyword":
            return await self.keyword_search("products", query_text, filters=f_dict, limit=limit)
        elif mode == "vector":
            return await self.semantic_search("products", query_text, filters=f_dict, limit=limit)
        return await self.hybrid_search("products", query_text, filters=f_dict, limit=limit)

    async def search_components(
        self,
        query_text: str,
        mode: str = "hybrid",
        filters: Optional[ComponentFilters] = None,
        limit: int = 10,
    ) -> SearchResponse:
        f_dict = filters.model_dump(exclude_none=True) if filters else {}
        if mode == "keyword":
            return await self.keyword_search("components", query_text, filters=f_dict, limit=limit)
        elif mode == "vector":
            return await self.semantic_search("components", query_text, filters=f_dict, limit=limit)
        return await self.hybrid_search("components", query_text, filters=f_dict, limit=limit)

    async def search_reviews(
        self,
        query_text: str,
        mode: str = "hybrid",
        filters: Optional[ReviewFilters] = None,
        limit: int = 10,
    ) -> SearchResponse:
        f_dict = filters.model_dump(exclude_none=True) if filters else {}
        if mode == "keyword":
            return await self.keyword_search("reviews", query_text, filters=f_dict, limit=limit)
        elif mode == "vector":
            return await self.semantic_search("reviews", query_text, filters=f_dict, limit=limit)
        return await self.hybrid_search("reviews", query_text, filters=f_dict, limit=limit)

    async def search_documents(
        self,
        query_text: str,
        mode: str = "hybrid",
        filters: Optional[DocumentFilters] = None,
        limit: int = 10,
    ) -> SearchResponse:
        f_dict = filters.model_dump(exclude_none=True) if filters else {}
        if mode == "keyword":
            return await self.keyword_search("documents", query_text, filters=f_dict, limit=limit)
        elif mode == "vector":
            return await self.semantic_search("documents", query_text, filters=f_dict, limit=limit)
        return await self.hybrid_search("documents", query_text, filters=f_dict, limit=limit)
