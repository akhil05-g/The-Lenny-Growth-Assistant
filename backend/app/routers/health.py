"""Health and Observability Check Router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.services.rag_service import rag_service
from backend.app.services.llm_provider import llm_manager

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=Dict[str, Any])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check verifying DB, Knowledge Base, and LLM Provider."""
    # Check DB
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Knowledge Base
    kb_status = {
        "is_indexed": rag_service.is_indexed,
        "total_chunks": len(rag_service.chunks),
        "total_guests": len(rag_service.guest_index),
        "total_topics": len(rag_service.topic_map),
    }

    # Check Active LLM
    active_provider = llm_manager.active_provider_name
    provider_inst = llm_manager.get_active_provider()
    is_avail, latency, msg = await provider_inst.check_health()

    llm_telemetry = {
        "active_provider": active_provider,
        "is_available": is_avail,
        "latency_ms": round(latency, 2),
        "status_message": msg,
    }

    overall_status = "healthy" if (db_status == "healthy" and kb_status["is_indexed"]) else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "knowledge_base": kb_status,
        "llm_provider": llm_telemetry,
    }
