"""Tests for Agent Orchestration, Grounding, Multi-turn memory, and Artifact parsing."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_grounded_chat_with_citations():
    """Verify conversational Q&A attaches citations from Lenny's transcripts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        session_res = await client.post("/api/sessions", json={"title": "Brian Chesky Details Test"})
        session_id = session_res.json()["id"]

        # Send grounded question
        chat_payload = {
            "session_id": session_id,
            "message": "What does Brian Chesky believe about micromanagement and being in the details?",
        }
        chat_res = await client.post("/api/chat", json=chat_payload)
        assert chat_res.status_code == 200
        data = chat_res.json()

        assert data["session_id"] == session_id
        assert data["role"] == "assistant"
        assert len(data["content"]) > 50
        assert len(data["sources"]) > 0

        # Check citation contains Brian Chesky
        top_source = data["sources"][0]
        assert "Brian Chesky" in top_source["guest"] or "Brian Chesky" in top_source["episode_title"]

        # Verify multi-turn memory: check session history now has 2 messages (user + assistant)
        detail_res = await client.get(f"/api/sessions/{session_id}")
        assert detail_res.status_code == 200
        session_detail = detail_res.json()
        assert len(session_detail["messages"]) == 2


@pytest.mark.asyncio
async def test_out_of_domain_refusal():
    """Verify agent politely refuses out-of-domain queries without hallucination."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat_payload = {
            "message": "How do quantum supercomputers solve protein folding in astrophysics?",
        }
        chat_res = await client.post("/api/chat", json=chat_payload)
        assert chat_res.status_code == 200
        data = chat_res.json()

        # Strict anti-hallucination verification
        assert "could not find" in data["content"].lower() or "not find information" in data["content"].lower()
        assert len(data["sources"]) == 0


@pytest.mark.asyncio
async def test_artifact_generation_and_persistence():
    """Verify agent detects artifact requests, renders them cleanly, and persists in database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        session_res = await client.post("/api/sessions", json={"title": "Artifact Generation Test"})
        session_id = session_res.json()["id"]

        chat_payload = {
            "session_id": session_id,
            "message": "Generate an interactive HTML checklist artifact for product execution.",
            "skill": "artifact",
        }
        chat_res = await client.post("/api/chat", json=chat_payload)
        assert chat_res.status_code == 200
        data = chat_res.json()

        # Check artifact presence
        assert data["artifact"] is not None
        artifact = data["artifact"]
        assert "Checklist" in artifact["title"]
        assert artifact["type"] in ["html", "markdown"]
        assert len(artifact["content"]) > 50

        # Check artifact persistence in session details
        detail_res = await client.get(f"/api/sessions/{session_id}")
        session_detail = detail_res.json()
        assert len(session_detail["artifacts"]) == 1
        assert session_detail["artifacts"][0]["id"] == artifact["id"]
