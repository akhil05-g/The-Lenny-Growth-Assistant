"""Tests for Ship 30 for 30 Content Engine skill."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_ship30_skill_endpoint():
    """Verify Ship 30 essay generation enforces 4A structure and citations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "topic": "Brian Chesky on being in the details and founder leadership",
            "guest_filter": "Brian Chesky",
        }
        res = await client.post("/api/skills/ship30", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert "essay" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
        assert data["word_count"] > 100

        essay_text = data["essay"]
        # Check core Ship 30 framework elements
        assert "Actionable" in essay_text
        assert "Analytical" in essay_text
        assert "Aspirational" in essay_text
        assert "Anthropological" in essay_text
        assert "Takeaway" in essay_text or "takeaway" in essay_text.lower()
