"""Tests for Knowledge Base RAG retrieval precision and citations."""

import pytest
from backend.app.services.rag_service import rag_service


def test_rag_initialization():
    """Verify RAG service indexes transcripts correctly."""
    rag_service.initialize()
    assert rag_service.is_indexed is True
    assert len(rag_service.chunks) > 0
    assert len(rag_service.guest_index) > 0


def test_brian_chesky_retrieval():
    """Verify retrieval returns Brian Chesky episode with timestamped YouTube URL."""
    rag_service.initialize()
    results = rag_service.search("Brian Chesky new playbook founder mode in the details", top_k=3)
    assert len(results) > 0
    top_hit = results[0]
    assert "Brian Chesky" in top_hit.guest or "Brian Chesky" in top_hit.episode_title
    assert len(top_hit.quote) > 20
    assert top_hit.youtube_url is not None
    assert "youtube.com" in top_hit.youtube_url or "youtu.be" in top_hit.youtube_url


def test_guest_filter_search():
    """Verify explicit guest filter strictly confines results."""
    rag_service.initialize()
    results = rag_service.search("product strategy and growth", top_k=3, guest_filter="Brian Chesky")
    assert len(results) > 0
    for r in results:
        assert "brian chesky" in r.guest.lower()


def test_out_of_domain_retrieval():
    """Verify completely out-of-domain queries return empty or low relevance results."""
    rag_service.initialize()
    results = rag_service.search("quantum chromodynamics subatomic dark matter hadron particle collision", top_k=3)
    assert len(results) == 0
