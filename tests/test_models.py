"""Tests for Model configuration and dynamic switching."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_list_models():
    """Verify models endpoint returns active provider and available options."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/models")
        assert res.status_code == 200
        data = res.json()

        assert "active_provider" in data
        assert "models" in data
        assert len(data["models"]) >= 4  # ollama, claude, openai, resilient_local


@pytest.mark.asyncio
async def test_switch_models():
    """Verify dynamic switching between providers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Switch to resilient_local
        switch_res = await client.post(
            "/api/models/switch",
            json={"provider": "resilient_local"},
        )
        assert switch_res.status_code == 200
        data = switch_res.json()
        assert data["active_provider"] == "resilient_local"

        # Switch to ollama
        switch_back = await client.post(
            "/api/models/switch",
            json={"provider": "ollama", "model_name": "llama3.2:latest"},
        )
        assert switch_back.status_code == 200
        data_back = switch_back.json()
        assert data_back["active_provider"] == "ollama"
