"""Stage 4 Canonical Reindexing Script.

Performs zero-downtime reindexing of all canonical products from PostgreSQL
into OpenSearch versioned index 'products_v1' and switches alias 'products_current'.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.config import settings
from app.services.product_indexing_service import ProductIndexingService
from app.services.product_catalog_service import ProductCatalogService


async def main():
    print("=" * 60)
    print("STAGE 4 — CANONICAL OPENSEARCH REINDEXING")
    print("=" * 60)

    start = time.perf_counter()
    catalog_service = ProductCatalogService()
    all_products = await catalog_service.get_all_products()
    print(f"Authoritative products in PostgreSQL: {len(all_products)}")

    indexing_service = ProductIndexingService(
        index_name=settings.OPENSEARCH_INDEX,
        alias_name=settings.OPENSEARCH_ALIAS,
    )

    print(f"Target index: {settings.OPENSEARCH_INDEX}")
    print(f"Target alias: {settings.OPENSEARCH_ALIAS}")
    print(f"Embedding dimension: {settings.EMBEDDING_DIMENSION}")

    print("\nStarting full reindex...")
    result = await indexing_service.reindex_all(new_version=settings.OPENSEARCH_INDEX)
    print(f"Reindex result: {result}")

    status = await indexing_service.get_index_status()
    print("\nFinal Index Status:")
    for k, v in status.items():
        print(f"  {k}: {v}")

    elapsed = round(time.perf_counter() - start, 2)
    print(f"\nReindexing completed in {elapsed}s")
    if status.get("synced"):
        print("SUCCESS: OpenSearch index is 100% synchronized with PostgreSQL!")
    else:
        print(
            f"WARNING: Sync mismatch: PG={status.get('postgresql_product_count')}, "
            f"OS={status.get('opensearch_doc_count')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
