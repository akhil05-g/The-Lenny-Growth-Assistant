"""Tests for Session CRUD and persistence operations."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_session_lifecycle():
    """Verify complete session CRUD operations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Session
        create_res = await client.post("/api/sessions", json={"title": "Test PM Strategy Session"})
        assert create_res.status_code == 201
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test PM Strategy Session"

        # 2. List Sessions
        list_res = await client.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 3. Get Session Details
        detail_res = await client.get(f"/api/sessions/{session_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["id"] == session_id
        assert isinstance(detail_data["messages"], list)
        assert isinstance(detail_data["artifacts"], list)

        # 4. Delete Session
        del_res = await client.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 204

        # 5. Verify deletion
        not_found_res = await client.get(f"/api/sessions/{session_id}")
        assert not_found_res.status_code == 404
