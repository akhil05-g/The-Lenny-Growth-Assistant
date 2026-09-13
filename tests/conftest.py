"""Pytest configuration and fixtures."""

import pytest
from backend.app.database import init_db
from backend.app.services.rag_service import rag_service
from backend.app.services.llm_provider import llm_manager


@pytest.fixture(autouse=True)
async def setup_test_environment():
    """Ensure database tables exist and resilient provider is active for test suite."""
    await init_db()
    llm_manager.set_active_provider("resilient_local")
    rag_service.initialize()
    yield
