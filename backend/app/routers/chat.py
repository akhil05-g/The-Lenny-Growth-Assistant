"""Chat Router for conversational turns."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from backend.app.services.agent_service import agent_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_200_OK)
async def chat_interaction(
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process user query with strict RAG grounding, skill routing, and artifact parsing."""
    try:
        session_id = payload.session_id or str(uuid.uuid4())
        response = await agent_service.process_user_turn(
            session_id=session_id,
            user_message=payload.message,
            db=db,
            skill=payload.skill,
            model_override=payload.model,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}",
        )


@router.post("/stream")
async def chat_interaction_stream(
    payload: ChatMessageRequest,
):
    """Stream user query tokens, citations, and artifacts in real-time via Server-Sent Events."""
    try:
        session_id = payload.session_id or str(uuid.uuid4())
        return StreamingResponse(
            agent_service.process_user_turn_stream(
                session_id=session_id,
                user_message=payload.message,
                skill=payload.skill,
                model_override=payload.model,
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat stream initiation failed: {str(e)}",
        )

