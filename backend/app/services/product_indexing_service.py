"""Product Indexing Service.

Synchronizes canonical PostgreSQL products into OpenSearch versioned indices
with deterministic search text, dense semantic embeddings, and atomic alias switching.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Sequence, Union
from opensearchpy import OpenSearch, helpers

from app.core.config import settings
from app.core.logging import logger
from app.models.catalog import Product
from app.services.product_catalog_service import ProductCatalogService
from app.services.embedding import EmbeddingService
from app.adapters.local.local_embedding import DeterministicLocalEmbeddingService
from app.retrieval.index_manager import (
    DEFAULT_PRODUCT_ALIAS,
    DEFAULT_PRODUCT_INDEX,
    DEFAULT_VECTOR_DIM,
    create_versioned_product_index,
    get_alias_indices,
    switch_alias,
)


def build_search_text(product: Product) -> str:
    """Deterministically generate rich searchable text combining product metadata and specifications.

    Combines: brand, model, title, variant, category, subcategory, model_number,
    key specifications, and description.
    Deterministic: no LLM generation.
    """
    parts: List[str] = []

    if product.brand:
        parts.append(product.brand.strip())
    if product.model:
        parts.append(product.model.strip())
    if product.title and product.title not in parts:
        parts.append(product.title.strip())
    if product.variant:
        parts.append(product.variant.strip())
    if product.category:
        parts.append(product.category.strip())
    if product.subcategory:
        parts.append(product.subcategory.strip())
    if product.model_number and product.model_number not in parts:
        parts.append(product.model_number.strip())

    # Add variant titles if available
    if product.variants:
        for v in product.variants:
            v_name = getattr(v, "variant_name", None) or getattr(v, "title", None)
            if v_name and v_name not in parts:
                parts.append(v_name.strip())

    # Extract specifications
    specs = product.specifications or {}
    if isinstance(specs, dict):
        priority_keys = [
            "cpu",
            "processor",
            "gpu",
            "graphics",
            "ram",
            "memory",
            "storage",
            "ssd",
            "display",
            "screen",
            "resolution",
            "camera",
            "battery",
            "sensor",
            "interface",
            "connectivity",
            "wireless",
            "bluetooth",
            "wifi",
            "chipset",
            "architecture",
            "voltage",
            "current",
            "power",
        ]
        # First priority spec keys
        for key in priority_keys:
            val = specs.get(key)
            if val:
                parts.append(f"{val}".strip())
        # Then remaining specs
        for key, val in sorted(specs.items()):
            if key not in priority_keys and val:
                if isinstance(val, (str, int, float)):
                    parts.append(f"{val}".strip())
                elif isinstance(val, list):
                    parts.extend(str(item).strip() for item in val if item)

    if product.description:
        parts.append(product.description.strip())

    # Deterministic normalization: remove redundant whitespace
    full_text = " ".join(parts)
    return " ".join(full_text.split())


def build_opensearch_document(
    product: Product,
    embedding: List[float],
) -> Dict[str, Any]:
    """Convert a canonical PostgreSQL Product entity into a normalized OpenSearch document.

    Canonical document structure:
    - product_id: UUID string matching OpenSearch _id
    - brand, model, variant, category, subcategory, description
    - specifications: structured spec dict
    - search_text: deterministic text representation
    - image_reference: metadata reference only (no binary image)
    - source_metadata: provenance reference
    - embedding: dense vector matching EMBEDDING_DIMENSION
    """
    pid_str = str(product.id)
    search_text = build_search_text(product)

    # Primary image reference metadata (NO binary storage)
    image_ref: Dict[str, Any] = {}
    if product.images:
        primary_img = next(
            (img for img in product.images if img.is_primary), product.images[0]
        )
        image_ref = {
            "image_id": str(primary_img.id),
            "storage_key": primary_img.storage_key or primary_img.image_url,
            "url": primary_img.image_url,
            "image_type": primary_img.image_type,
            "is_primary": bool(primary_img.is_primary),
        }

    # Provenance source metadata
    source_meta: Dict[str, Any] = {}
    if product.sources:
        first_src = product.sources[0]
        source_meta = {
            "source_type": first_src.source_type,
            "source_url": first_src.source_url,
            "trust_score": float(first_src.trust_score or 1.0),
        }

    # Lowest price from offers if available
    price = None
    currency = "INR"
    if product.retailer_offers:
        valid_prices = [
            o.price
            for o in product.retailer_offers
            if o.price is not None and o.price > 0
        ]
        if valid_prices:
            price = float(min(valid_prices))
            currency = product.retailer_offers[0].currency or "INR"

    variant_str = product.variant or ""
    if not variant_str and product.variants:
        first_v = product.variants[0]
        variant_str = (
            getattr(first_v, "variant_name", None)
            or getattr(first_v, "title", None)
            or ""
        )

    return {
        "product_id": pid_str,
        "id": pid_str,  # Backward compatibility
        "brand": product.brand or "",
        "model": product.model or "",
        "variant": variant_str,
        "title": product.title or f"{product.brand or ''} {product.model or ''}".strip(),
        "slug": product.slug or "",
        "category": product.category or "",
        "subcategory": product.subcategory or "",
        "description": product.description or "",
        "search_text": search_text,
        "specifications": product.specifications or {},
        "specs": product.specifications or {},  # Backward compatibility
        "image_reference": image_ref,
        "source_metadata": source_meta,
        "model_number": product.model_number or "",
        "sku": product.sku or "",
        "price": price,
        "currency": currency,
        "is_component": bool(product.is_component),
        "embedding": embedding,
    }


class ProductIndexingService:
    """Orchestrates indexing of canonical PostgreSQL products into OpenSearch.

    Guarantees:
    1. PostgreSQL is the authoritative source of truth.
    2. OpenSearch document ID strictly equals canonical product_id.
    3. Idempotent indexing: upserting identical product does not duplicate documents.
    4. Versioned index creation and zero-downtime alias switching.
    5. Strict embedding dimension validation.
    """

    def __init__(
        self,
        client: Optional[OpenSearch] = None,
        catalog_service: Optional[ProductCatalogService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        index_name: Optional[str] = None,
        alias_name: Optional[str] = None,
    ):
        self._client = client
        self._catalog = catalog_service or ProductCatalogService()
        self._embedding = embedding_service or DeterministicLocalEmbeddingService(
            dimension=settings.EMBEDDING_DIMENSION
        )
        self._index_name = index_name or settings.OPENSEARCH_INDEX
        self._alias_name = alias_name or settings.OPENSEARCH_ALIAS

    def _get_client(self) -> OpenSearch:
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
        return self._client

    async def ensure_index(self, index_name: Optional[str] = None) -> bool:
        """Ensure versioned index exists with explicit mappings and alias points to it."""
        client = self._get_client()
        target_index = index_name or self._index_name
        dim = self._embedding.dimension()

        # Check dimension matches configuration
        if dim != settings.EMBEDDING_DIMENSION:
            raise ValueError(
                f"Embedding dimension mismatch: service dimension {dim} != configured {settings.EMBEDDING_DIMENSION}"
            )

        created = await asyncio.to_thread(
            create_versioned_product_index, client, target_index, dim
        )
        if created:
            logger.info(f"Created versioned product index '{target_index}' (dim={dim})")

        # If alias does not exist or points nowhere, point to target_index
        alias_indices = await asyncio.to_thread(get_alias_indices, client, self._alias_name)
        if not alias_indices:
            await asyncio.to_thread(switch_alias, client, self._alias_name, target_index)
            logger.info(f"Pointed alias '{self._alias_name}' to '{target_index}'")

        return created

    async def index_product(
        self,
        product_id: Union[uuid.UUID, str],
        target_index: Optional[str] = None,
    ) -> bool:
        """Index a single product by UUID into OpenSearch. Idempotent by product_id."""
        client = self._get_client()
        await self.ensure_index(target_index)

        product = await self._catalog.get_product(product_id)
        if not product:
            logger.warning(f"Product {product_id} not found in PostgreSQL catalog; skipping indexing")
            return False

        search_text = build_search_text(product)
        embedding = await self._embedding.embed_text(search_text)
        self._embedding.validate_vector(embedding)

        doc = build_opensearch_document(product, embedding)
        idx = target_index or self._alias_name

        await asyncio.to_thread(
            client.index,
            index=idx,
            id=str(product.id),
            body=doc,
            refresh=True,
        )
        logger.info(
            f"Indexed product {product.id} ({product.brand} {product.model}) into {idx}",
            extra={"product_id": str(product.id), "index": idx},
        )
        return True

    async def index_products(
        self,
        product_ids: Sequence[Union[uuid.UUID, str]],
        target_index: Optional[str] = None,
        batch_size: int = 100,
    ) -> int:
        """Bulk index multiple products by IDs."""
        client = self._get_client()
        await self.ensure_index(target_index)

        products = await self._catalog.get_products_by_ids(product_ids)
        if not products:
            return 0

        idx = target_index or self._alias_name
        total_indexed = 0

        for i in range(0, len(products), batch_size):
            chunk = products[i : i + batch_size]
            search_texts = [build_search_text(p) for p in chunk]
            embeddings = await self._embedding.embed_documents(search_texts)

            actions = []
            for p, emb in zip(chunk, embeddings):
                self._embedding.validate_vector(emb)
                doc = build_opensearch_document(p, emb)
                actions.append({
                    "_index": idx,
                    "_id": str(p.id),
                    "_source": doc,
                })

            success_count, _ = await asyncio.to_thread(
                helpers.bulk,
                client,
                actions,
                refresh=True,
            )
            total_indexed += success_count

        logger.info(f"Bulk indexed {total_indexed}/{len(products)} products into {idx}")
        return total_indexed

    async def index_all_products(
        self,
        target_index: Optional[str] = None,
        batch_size: int = 100,
    ) -> int:
        """Index all canonical products from PostgreSQL into the target index."""
        client = self._get_client()
        await self.ensure_index(target_index)

        all_products = await self._catalog.get_all_products()
        if not all_products:
            logger.warning("No products found in PostgreSQL catalog to index")
            return 0

        idx = target_index or self._alias_name
        total_indexed = 0

        for i in range(0, len(all_products), batch_size):
            chunk = all_products[i : i + batch_size]
            search_texts = [build_search_text(p) for p in chunk]
            embeddings = await self._embedding.embed_documents(search_texts)

            actions = []
            for p, emb in zip(chunk, embeddings):
                self._embedding.validate_vector(emb)
                doc = build_opensearch_document(p, emb)
                actions.append({
                    "_index": idx,
                    "_id": str(p.id),
                    "_source": doc,
                })

            success_count, _ = await asyncio.to_thread(
                helpers.bulk,
                client,
                actions,
                refresh=True,
            )
            total_indexed += success_count

        logger.info(f"Indexed all {total_indexed} products from PostgreSQL into {idx}")
        return total_indexed

    async def update_product(
        self,
        product_id: Union[uuid.UUID, str],
        target_index: Optional[str] = None,
    ) -> bool:
        """Update an existing indexed product (upsert semantics)."""
        return await self.index_product(product_id, target_index=target_index)

    async def delete_product(
        self,
        product_id: Union[uuid.UUID, str],
        target_index: Optional[str] = None,
    ) -> bool:
        """Remove a product from OpenSearch. Does NOT delete from PostgreSQL."""
        client = self._get_client()
        pid_str = str(product_id)
        idx = target_index or self._alias_name

        try:
            res = await asyncio.to_thread(
                client.delete,
                index=idx,
                id=pid_str,
                ignore=[404],
                refresh=True,
            )
            logger.info(f"Deleted product {pid_str} from OpenSearch {idx}: {res.get('result')}")
            return True
        except Exception as exc:
            logger.error(f"Failed to delete product {pid_str} from OpenSearch: {exc}")
            return False

    async def reindex_all(self, new_version: Optional[str] = None) -> Dict[str, Any]:
        """Zero-downtime full reindex into a new versioned index and atomic alias switch.

        Flow:
        1. Query PostgreSQL total product count
        2. Create new versioned index (e.g. products_v2)
        3. Index all products into new versioned index
        4. Validate document count matches PostgreSQL
        5. Atomically switch alias 'products_current' to new index
        6. Retain old index
        """
        client = self._get_client()
        all_products = await self._catalog.get_all_products()
        expected_count = len(all_products)

        # Determine new versioned index name
        if not new_version:
            current_indices = await asyncio.to_thread(get_alias_indices, client, self._alias_name)
            if current_indices:
                latest = current_indices[0]
                if "_v" in latest:
                    prefix, v_str = latest.rsplit("_v", 1)
                    try:
                        next_v = int(v_str) + 1
                        new_version = f"{prefix}_v{next_v}"
                    except ValueError:
                        new_version = f"{latest}_new"
                else:
                    new_version = f"{latest}_v2"
            else:
                new_version = self._index_name

        dim = self._embedding.dimension()
        logger.info(f"Starting full reindex into '{new_version}' (expected: {expected_count} products)")

        # Create new index
        await asyncio.to_thread(create_versioned_product_index, client, new_version, dim)

        # Index all products into new versioned index
        indexed_count = await self.index_all_products(target_index=new_version)

        # Refresh and count documents in new index
        await asyncio.to_thread(client.indices.refresh, index=new_version)
        count_res = await asyncio.to_thread(client.count, index=new_version)
        actual_count = count_res.get("count", 0)

        # Validation check
        if actual_count < expected_count:
            error_msg = (
                f"Reindexing validation failed: expected {expected_count} documents in '{new_version}', "
                f"but found only {actual_count}. Alias '{self._alias_name}' was NOT switched."
            )
            logger.error(error_msg)
            return {
                "status": "failed",
                "reason": error_msg,
                "expected": expected_count,
                "actual": actual_count,
                "index": new_version,
            }

        # Atomically switch alias to the validated new index
        await asyncio.to_thread(switch_alias, client, self._alias_name, new_version)
        logger.info(
            f"Successfully switched alias '{self._alias_name}' to '{new_version}' with {actual_count} documents"
        )

        return {
            "status": "success",
            "alias": self._alias_name,
            "active_index": new_version,
            "document_count": actual_count,
            "expected_count": expected_count,
        }

    async def get_index_status(self) -> Dict[str, Any]:
        """Return diagnostic status of product search indices and PostgreSQL alignment."""
        client = self._get_client()
        alias_indices = await asyncio.to_thread(get_alias_indices, client, self._alias_name)
        active_index = alias_indices[0] if alias_indices else None

        doc_count = 0
        if active_index:
            try:
                count_res = await asyncio.to_thread(client.count, index=active_index)
                doc_count = count_res.get("count", 0)
            except Exception:
                pass

        all_products = await self._catalog.get_all_products()
        pg_count = len(all_products)

        health = "unknown"
        try:
            h_info = await asyncio.to_thread(client.cluster.health)
            health = h_info.get("status", "unknown")
        except Exception:
            pass

        return {
            "alias": self._alias_name,
            "active_index": active_index,
            "alias_indices": alias_indices,
            "opensearch_doc_count": doc_count,
            "postgresql_product_count": pg_count,
            "synced": (doc_count == pg_count and pg_count > 0),
            "cluster_health": health,
            "embedding_model": self._embedding.model_name(),
            "embedding_dimension": self._embedding.dimension(),
        }
