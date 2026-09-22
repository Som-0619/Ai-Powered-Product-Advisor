"""Test FastAPI Search API endpoints: BM25, Vector, Hybrid, hydration, and error handling."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_api_keyword_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/search", params={"q": "AirPods", "mode": "keyword"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "AirPods"
        assert data["search_mode"] == "keyword"
        assert data["total"] > 0
        assert len(data["results"]) > 0
        first = data["results"][0]
        assert "product_id" in first
        assert "score" in first
        assert "product" in first
        assert first["product"]["title"] is not None


@pytest.mark.asyncio
async def test_api_semantic_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/search/semantic", params={"q": "wireless noise cancelling headphones"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["search_mode"] == "vector"
        assert data["total"] > 0
        assert len(data["results"]) > 0


@pytest.mark.asyncio
async def test_api_hybrid_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/search/hybrid", params={"q": "laptop for programming"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["search_mode"] == "hybrid"
        assert data["total"] > 0
        assert len(data["results"]) > 0


@pytest.mark.asyncio
async def test_api_post_search_with_filter():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "query": "Apple",
            "category": "Headphones",
            "mode": "hybrid",
            "limit": 5,
        }
        resp = await ac.post("/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["search_mode"] == "hybrid"
        assert data["total"] > 0
        for item in data["results"]:
            assert item["product"]["category"] == "Headphones"


@pytest.mark.asyncio
async def test_api_empty_query_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/search", params={"q": "   "})
        assert resp.status_code == 400
