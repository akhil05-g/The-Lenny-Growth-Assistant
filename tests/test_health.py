"""Tests for health and root endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify service root returns 200 and discovery payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["service"] == "The Lenny Growth Assistant API"
        assert data["status"] == "online"


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify /api/health reports healthy database and RAG status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "database" in data
        assert "knowledge_base" in data
        assert "llm_provider" in data
        assert data["database"] == "healthy"
