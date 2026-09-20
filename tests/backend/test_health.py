"""Unit and integration tests for FastAPI health endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Product Advisor"
        assert "version" in data
        assert data["health"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_health_liveness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert data["environment"] == "local"


@pytest.mark.asyncio
async def test_health_readiness_structure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded", "not_ready")
        assert "services" in data
        for s in ("postgres", "opensearch", "redis", "minio", "ollama"):
            assert s in data["services"]
            assert data["services"][s]["status"] in ("healthy", "degraded", "not_ready")


@pytest.mark.asyncio
async def test_request_id_middleware():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health", headers={"X-Request-ID": "custom-uuid-1234"})
        assert response.status_code == 200
        assert response.headers.get("x-request-id") == "custom-uuid-1234"
        assert "x-response-time" in response.headers
