import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.schemas.chat import GroundedSource
from backend.app.services.rag_service import rag_service
from backend.app.services.llm_provider import llm_manager
from backend.app.services.ship30_skill import (
    SHIP30_SYSTEM_PROMPT,
    build_ship30_prompt,
)

router = APIRouter(prefix="/api/skills", tags=["Skills"])


class Ship30Request(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic for Ship 30 for 30 essay")
    guest_filter: Optional[str] = Field(None, description="Optional guest name filter (e.g. 'Brian Chesky')")


class Ship30Response(BaseModel):
    topic: str
    essay: str
    sources: List[GroundedSource]
    model_used: str
    word_count: int


@router.post("/ship30", response_model=Ship30Response)
async def generate_ship30_essay(payload: Ship30Request):
    """Generate a high-impact, grounded Ship 30 for 30 essay using official frameworks."""
    # 1. Retrieve grounded quotes
    sources = rag_service.search(
        query=payload.topic,
        top_k=5,
        guest_filter=payload.guest_filter,
    )

    # 2. Build prompt
    prompt = build_ship30_prompt(payload.topic, sources)

    # 3. Generate response
    content, provider_used, _ = await llm_manager.generate_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SHIP30_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4000,
    )

    word_count = len(content.split())

    return Ship30Response(
        topic=payload.topic,
        essay=content,
        sources=sources,
        model_used=provider_used,
        word_count=word_count,
    )


@router.post("/ship30/stream")
async def generate_ship30_essay_stream(payload: Ship30Request):
    """Progressively stream generated Ship 30 essay tokens in real-time via Server-Sent Events (SSE)."""
    sources = rag_service.search(
        query=payload.topic,
        top_k=5,
        guest_filter=payload.guest_filter,
    )
    prompt = build_ship30_prompt(payload.topic, sources)

    async def event_generator():
        # First send sources metadata event
        sources_payload = [s.model_dump() for s in sources]
        yield f"event: sources\ndata: {json.dumps(sources_payload)}\n\n"

        # Stream progressive LLM tokens
        async for token in llm_manager.generate_stream_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SHIP30_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4000,
        ):
            yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

