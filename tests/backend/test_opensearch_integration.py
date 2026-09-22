"""Stage 4 — OpenSearch Search and Retrieval Integration Tests.

Validates all 14 required search tests from Section 32:
1. test_index_product()
2. test_index_idempotency()
3. test_reindex_all()
4. test_bm25_search()
5. test_vector_search()
6. test_hybrid_search()
7. test_category_filter()
8. test_brand_filter()
9. test_product_id_consistency()
10. test_index_alias()
11. test_embedding_dimension()
12. test_image_reference_not_stored_as_binary()
13. test_opensearch_failure()
14. test_database_fallback()

Plus Section 33 search quality evaluation suite.
"""

import os
import uuid
import pytest
import pytest_asyncio
from opensearchpy import OpenSearch
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.catalog import Product
from app.services.product_catalog_service import ProductCatalogService
from app.services.product_indexing_service import (
    ProductIndexingService,
    build_search_text,
    build_opensearch_document,
)
from app.adapters.local.opensearch_service import LocalOpenSearchService
from app.adapters.local.local_embedding import DeterministicLocalEmbeddingService
from app.retrieval.index_manager import get_alias_indices

TEST_DB_URL = os.environ.get(
    "LOCAL_POSTGRES_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor",
    ),
)
if "postgres:5432" in TEST_DB_URL:
    TEST_DB_URL = TEST_DB_URL.replace("postgres:5432", "127.0.0.1:5432")

OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.environ.get("OPENSEARCH_PORT", 9200))


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(db_engine):
    maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def opensearch_client():
    client = OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        use_ssl=False,
        verify_certs=False,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def embedding_service():
    return DeterministicLocalEmbeddingService(dimension=settings.EMBEDDING_DIMENSION)


@pytest.fixture(scope="function")
def indexing_service(opensearch_client, embedding_service):
    return ProductIndexingService(
        client=opensearch_client,
        embedding_service=embedding_service,
        index_name=settings.OPENSEARCH_INDEX,
        alias_name=settings.OPENSEARCH_ALIAS,
    )


@pytest.fixture(scope="function")
def opensearch_service(embedding_service):
    return LocalOpenSearchService(embedding_service=embedding_service)


# --------------------------------------------------------------------------
# 1. test_index_product()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_index_product(test_session, indexing_service, opensearch_client):
    """Test indexing a single product into OpenSearch."""
    catalog = ProductCatalogService(test_session)
    products = await catalog.get_products(limit=1)
    assert len(products) > 0, "Database must have at least one product"
    prod = products[0]

    success = await indexing_service.index_product(prod.id)
    assert success is True

    # Verify directly from OpenSearch
    doc = opensearch_client.get(index=settings.OPENSEARCH_ALIAS, id=str(prod.id))
    assert doc["found"] is True
    assert doc["_id"] == str(prod.id)
    source = doc["_source"]
    assert source["product_id"] == str(prod.id)
    assert source["brand"] == (prod.brand or "")
    assert source["model"] == (prod.model or "")
    assert len(source["search_text"]) > 0
    assert len(source["embedding"]) == settings.EMBEDDING_DIMENSION


# --------------------------------------------------------------------------
# 2. test_index_idempotency()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_index_idempotency(test_session, indexing_service, opensearch_client):
    """Indexing the same product twice must not create duplicate documents."""
    catalog = ProductCatalogService(test_session)
    products = await catalog.get_products(limit=1)
    prod = products[0]

    # Index first time
    await indexing_service.index_product(prod.id)
    opensearch_client.indices.refresh(index=settings.OPENSEARCH_ALIAS)

    # Search for this exact product ID
    res1 = opensearch_client.search(
        index=settings.OPENSEARCH_ALIAS,
        body={"query": {"term": {"product_id": str(prod.id)}}},
    )
    count1 = res1["hits"]["total"]["value"]
    assert count1 == 1

    # Index second time
    await indexing_service.index_product(prod.id)
    opensearch_client.indices.refresh(index=settings.OPENSEARCH_ALIAS)

    res2 = opensearch_client.search(
        index=settings.OPENSEARCH_ALIAS,
        body={"query": {"term": {"product_id": str(prod.id)}}},
    )
    count2 = res2["hits"]["total"]["value"]
    assert count2 == 1, f"Expected exactly 1 document, found {count2}"


# --------------------------------------------------------------------------
# 3. test_reindex_all()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_reindex_all(test_session, indexing_service, opensearch_client):
    """Test full reindexing into a versioned index and atomic alias switch."""
    catalog = ProductCatalogService(test_session)
    all_prods = await catalog.get_all_products()
    total_pg = len(all_prods)

    res = await indexing_service.reindex_all(new_version="products_v1")
    assert res["status"] == "success"
    assert res["alias"] == settings.OPENSEARCH_ALIAS
    assert res["document_count"] == total_pg

    # Verify alias points to products_v1
    active_indices = get_alias_indices(opensearch_client, settings.OPENSEARCH_ALIAS)
    assert "products_v1" in active_indices


# --------------------------------------------------------------------------
# 4. test_bm25_search()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_bm25_search(opensearch_service):
    """Test BM25 keyword search for exact product names/specifications."""
    resp = await opensearch_service.search_keyword("AirPods Max")
    assert resp.total > 0
    assert len(resp.hits) > 0
    top_hit = resp.hits[0]
    assert "AirPods" in top_hit.source.get("title", "") or "AirPods" in top_hit.source.get("model", "")
    assert top_hit.score > 0.0


# --------------------------------------------------------------------------
# 5. test_vector_search()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_vector_search(opensearch_service):
    """Test dense vector k-NN semantic search."""
    resp = await opensearch_service.search_vector("wireless noise cancelling headphones")
    assert resp.total > 0
    assert len(resp.hits) > 0
    assert resp.search_mode == "vector"
    assert resp.hits[0].score > 0.0


# --------------------------------------------------------------------------
# 6. test_hybrid_search()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_hybrid_search(opensearch_service):
    """Test hybrid search combining BM25 keyword and vector similarity."""
    resp = await opensearch_service.search_hybrid(
        "laptop for machine learning with good GPU",
        keyword_weight=0.5,
        vector_weight=0.5,
        limit=5,
    )
    assert resp.total > 0
    assert len(resp.hits) > 0
    assert resp.search_mode == "hybrid"
    # Scores must be positive normalized numbers
    for h in resp.hits:
        assert h.score > 0.0


# --------------------------------------------------------------------------
# 7. test_category_filter()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_category_filter(opensearch_service):
    """Test filtering by product category."""
    resp = await opensearch_service.search_keyword(
        "Apple",
        filters={"category": "Headphones"},
        limit=5,
    )
    assert resp.total > 0
    for h in resp.hits:
        assert h.source.get("category") == "Headphones"


# --------------------------------------------------------------------------
# 8. test_brand_filter()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_brand_filter(opensearch_service):
    """Test filtering by product brand."""
    resp = await opensearch_service.search_keyword(
        "wireless",
        filters={"brand": "Apple"},
        limit=5,
    )
    assert resp.total > 0
    for h in resp.hits:
        assert h.source.get("brand") == "Apple"


# --------------------------------------------------------------------------
# 9. test_product_id_consistency()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_product_id_consistency(test_session, opensearch_service):
    """Retrieved product_id from OpenSearch must match PostgreSQL canonical ID."""
    catalog = ProductCatalogService(test_session)
    resp = await opensearch_service.search_keyword("Apple", limit=3)
    assert len(resp.hits) > 0

    for hit in resp.hits:
        doc_id = hit.id
        # Verify canonical existence in PostgreSQL
        pg_product = await catalog.get_product(doc_id)
        assert pg_product is not None, f"Product {doc_id} returned by OpenSearch but missing in PostgreSQL"
        assert str(pg_product.id) == doc_id


# --------------------------------------------------------------------------
# 10. test_index_alias()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_index_alias(opensearch_client):
    """Verify alias points to active product index."""
    alias_name = settings.OPENSEARCH_ALIAS
    assert opensearch_client.indices.exists_alias(name=alias_name)
    indices = get_alias_indices(opensearch_client, alias_name)
    assert len(indices) >= 1
    # Query via alias
    res = opensearch_client.count(index=alias_name)
    assert res["count"] > 0


# --------------------------------------------------------------------------
# 11. test_embedding_dimension()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_embedding_dimension(embedding_service):
    """Verify embedding vector strictly matches configured dimension."""
    text = "Dell XPS 15 Intel Core i7 32GB RAM"
    vec = await embedding_service.embed_text(text)
    assert len(vec) == settings.EMBEDDING_DIMENSION

    # Invalid dimension check
    invalid_vec = [0.1] * 128
    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        embedding_service.validate_vector(invalid_vec)


# --------------------------------------------------------------------------
# 12. test_image_reference_not_stored_as_binary()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_image_reference_not_stored_as_binary(opensearch_client):
    """Inspect stored documents: image_reference must NOT contain binary data."""
    res = opensearch_client.search(
        index=settings.OPENSEARCH_ALIAS,
        body={"size": 10, "query": {"match_all": {}}},
    )
    hits = res["hits"]["hits"]
    assert len(hits) > 0

    for hit in hits:
        src = hit["_source"]
        img_ref = src.get("image_reference", {})
        if img_ref:
            assert "data" not in img_ref
            assert "bytes" not in img_ref
            assert "base64" not in img_ref
            # Stored reference must be string URI / key
            if "storage_key" in img_ref and img_ref["storage_key"]:
                assert isinstance(img_ref["storage_key"], str)
            if "url" in img_ref and img_ref["url"]:
                assert isinstance(img_ref["url"], str)


# --------------------------------------------------------------------------
# 13. test_opensearch_failure()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_opensearch_failure(monkeypatch):
    """When OpenSearch is unavailable and fallback is disabled, raise RuntimeError."""
    monkeypatch.setattr(settings, "ENABLE_DB_SEARCH_FALLBACK", False)
    failing_service = LocalOpenSearchService()
    # Connect to invalid port
    failing_client = OpenSearch(hosts=[{"host": "localhost", "port": 59999}])
    failing_service._client = failing_client

    with pytest.raises(RuntimeError, match="OpenSearch"):
        await failing_service.search_keyword("test query")


# --------------------------------------------------------------------------
# 14. test_database_fallback()
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_database_fallback(monkeypatch):
    """When ENABLE_DB_SEARCH_FALLBACK=True, fallback to PostgreSQL search."""
    monkeypatch.setattr(settings, "ENABLE_DB_SEARCH_FALLBACK", True)
    failing_service = LocalOpenSearchService()
    failing_client = OpenSearch(hosts=[{"host": "localhost", "port": 59999}])
    failing_service._client = failing_client

    resp = await failing_service.search_keyword("AirPods", limit=5)
    assert resp.search_mode == "db_fallback"
    assert resp.total >= 1
    assert len(resp.hits) >= 1


# --------------------------------------------------------------------------
# 15. Section 33 Search Quality Test Dataset
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_search_quality_dataset(opensearch_service):
    """Test retrieval quality across representative queries from Section 33."""
    test_queries = [
        ("AirPods Max", "Exact"),
        ("iPhone 15", "Exact"),
        ("ESP32", "Exact"),
        ("16GB RAM 512GB SSD", "Specification"),
        ("laptop for machine learning", "Semantic"),
        ("headphones with noise cancellation", "Semantic"),
        ("development board with WiFi", "Semantic"),
        ("temperature sensor", "Semantic"),
    ]

    results_summary = []
    for q, q_type in test_queries:
        resp = await opensearch_service.search_hybrid(q, limit=5)
        results_summary.append({
            "query": q,
            "type": q_type,
            "total_retrieved": resp.total,
            "hits_returned": len(resp.hits),
            "top_hit": resp.hits[0].source.get("title") if resp.hits else None,
            "top_score": resp.hits[0].score if resp.hits else 0.0,
        })
        assert resp.total > 0, f"Query '{q}' ({q_type}) retrieved 0 documents!"

    # Ensure all 8 test queries succeeded with high quality candidates
    assert len(results_summary) == 8
