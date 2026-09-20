"""Integration and unit tests for OpenSearch SearchService retrieval.

Validates:
1. Exact technical term matching:
   - 'ESP32'
   - '3.3V'
   - 'I2C'
   - 'RTX 4060'
   - '16GB RAM'
2. Semantic vector queries (natural language / descriptive search)
3. Hybrid search combining BM25 keyword and dense vector k-NN similarity
4. Metadata filtering:
   - category & subcategory
   - brand
   - price ranges (min_price, max_price)
   - component_type
   - voltage ranges (operating voltage overlap)
   - interface (I2C, SPI)
5. Domain-specific search methods:
   - search_products()
   - search_components()
   - search_reviews()
   - search_documents()
6. Normalized SearchResponse and SearchHit structures
"""

import pytest
import pytest_asyncio

from app.services.search import SearchService
from app.services.factory import get_search_service
from app.schemas.search import (
    SearchResponse,
    ProductFilters,
    ComponentFilters,
    ReviewFilters,
    DocumentFilters,
)


@pytest_asyncio.fixture(loop_scope="function")
async def search_service() -> SearchService:
    service = get_search_service()
    await service.connect()
    return service


@pytest.mark.asyncio
async def test_search_service_health(search_service: SearchService):
    """Verify OpenSearch cluster health check."""
    health = await search_service.health_check()
    assert health["status"] in ("ok", "degraded")
    assert health["latency_ms"] >= 0
    assert "status" in health["details"]


@pytest.mark.asyncio
async def test_exact_technical_term_esp32(search_service: SearchService):
    """Test exact technical term query 'ESP32' matches MCU module across products and components."""
    # 1. Product keyword search
    res = await search_service.search_products("ESP32", mode="keyword", limit=5)
    assert res.total >= 1
    hit_titles = [h.source.get("title", "") for h in res.hits]
    assert any("ESP32" in t for t in hit_titles)

    # 2. Component search
    comp_res = await search_service.search_components("ESP32", mode="keyword", limit=5)
    assert comp_res.total >= 1
    part_numbers = [h.source.get("part_number", "") for h in comp_res.hits]
    assert any("ESP32" in p for p in part_numbers)


@pytest.mark.asyncio
async def test_exact_technical_term_voltage_3v3(search_service: SearchService):
    """Test exact technical term query '3.3V' and voltage filtering."""
    # 1. Keyword search for '3.3V'
    res = await search_service.search_components("3.3V", mode="keyword", limit=5)
    assert res.total >= 1

    # 2. Metadata filtering on voltage range overlap (3.3V operating voltage)
    filters = ComponentFilters(min_voltage=3.3, max_voltage=3.3)
    filtered_res = await search_service.search_components("", mode="keyword", filters=filters, limit=5)
    assert filtered_res.total >= 2
    matched_parts = [h.source.get("part_number", "") for h in filtered_res.hits]
    # ESP32 operates 3.0-3.6V, BME280 operates 1.71-3.6V, TPS7A02 operates 1.4-6.0V
    assert "ESP32-WROOM-32E-N4" in matched_parts
    assert "BME280" in matched_parts


@pytest.mark.asyncio
async def test_exact_technical_term_interface_i2c(search_service: SearchService):
    """Test exact technical term query 'I2C' communication interface."""
    # 1. Keyword search on components
    res = await search_service.search_components("I2C", mode="keyword", limit=5)
    assert res.total >= 1
    interfaces = [h.source.get("interface", "") for h in res.hits]
    assert any("I2C" in iface for iface in interfaces)

    # 2. Interface filter
    filters = ComponentFilters(interface="I2C")
    filtered_res = await search_service.search_components("", mode="keyword", filters=filters, limit=5)
    assert filtered_res.total >= 1
    for h in filtered_res.hits:
        assert "I2C" in h.source.get("interface", "")


@pytest.mark.asyncio
async def test_exact_technical_term_rtx_4060(search_service: SearchService):
    """Test exact technical term query 'RTX 4060' targets RTX 4060 GPU specifically."""
    res = await search_service.search_products("RTX 4060", mode="keyword", limit=5)
    assert res.total >= 1
    assert any("4060" in h.source.get("title", "") for h in res.hits)
    assert any(h.source.get("brand") == "ASUS" for h in res.hits)



@pytest.mark.asyncio
async def test_exact_technical_term_16gb_ram(search_service: SearchService):
    """Test exact technical term query '16GB RAM' matches laptop specification variant."""
    res = await search_service.search_products("16GB RAM", mode="keyword", limit=5)
    assert res.total >= 1
    hit_titles_and_desc = [f"{h.source.get('title')} {h.source.get('description')}" for h in res.hits]
    assert any("16GB" in text for text in hit_titles_and_desc)


@pytest.mark.asyncio
async def test_semantic_vector_search(search_service: SearchService):
    """Test dense vector k-NN semantic search with descriptive natural language queries."""
    # Semantic query for sensor module
    res = await search_service.search_components(
        "weather station environmental humidity and temperature detector",
        mode="vector",
        limit=3,
    )
    assert res.total >= 1
    assert res.search_mode == "vector"
    top_part = res.hits[0].source.get("part_number", "")
    assert top_part == "BME280"

    # Semantic query for enterprise laptop
    prod_res = await search_service.search_products(
        "ultra-lightweight enterprise laptop with OLED display",
        mode="vector",
        limit=3,
    )
    assert prod_res.total >= 1
    assert "ThinkPad" in prod_res.hits[0].source.get("title", "")


@pytest.mark.asyncio
async def test_hybrid_search_fusion(search_service: SearchService):
    """Test hybrid search fusing BM25 keyword score and dense vector k-NN similarity."""
    hybrid_res = await search_service.search_products(
        "Lenovo ThinkPad OLED display",
        mode="hybrid",
        limit=5,
    )
    assert hybrid_res.search_mode == "hybrid"
    assert hybrid_res.total >= 1
    top_hit = hybrid_res.hits[0]
    assert "ThinkPad" in top_hit.source.get("title", "")
    assert top_hit.score > 0.0


@pytest.mark.asyncio
async def test_metadata_filters(search_service: SearchService):
    """Test multi-field metadata filtering across categories, brands, prices, and fraud scores."""
    # 1. Filter products by category and brand
    p_filters = ProductFilters(category="laptops-ultrabooks", brand="Lenovo")
    res_p = await search_service.search_products("", mode="keyword", filters=p_filters, limit=5)
    assert res_p.total == 1
    assert res_p.hits[0].source.get("brand") == "Lenovo"

    # 2. Filter products by price range
    price_filters = ProductFilters(min_price=200.0, max_price=500.0)
    res_price = await search_service.search_products("", mode="keyword", filters=price_filters, limit=5)
    assert res_price.total >= 1
    for h in res_price.hits:
        p = h.source.get("price")
        if p is not None:
            assert 200.0 <= p <= 500.0

    # 3. Filter reviews by fraud score and rating
    r_filters = ReviewFilters(min_rating=4.5, max_fraud_score=0.5)
    res_r = await search_service.search_reviews("", mode="keyword", filters=r_filters, limit=5)
    assert res_r.total >= 1
    for h in res_r.hits:
        assert h.source.get("rating") >= 4.5
        assert h.source.get("fraud_score") <= 0.5
        assert "BEST LAPTOP EVER CLICK HERE TO BUY" not in h.source.get("title", "")

    # 4. Filter documents by doc_type
    d_filters = DocumentFilters(doc_type="datasheet")
    res_d = await search_service.search_documents("", mode="keyword", filters=d_filters, limit=5)
    assert res_d.total >= 2
    for h in res_d.hits:
        assert h.source.get("doc_type") == "datasheet"
