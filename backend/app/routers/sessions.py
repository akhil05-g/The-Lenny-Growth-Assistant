"""Session Management Router."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.session import SessionModel
from backend.app.models.message import MessageModel
from backend.app.models.artifact import ArtifactModel
from backend.app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionDetailResponse,
    MessageItem,
)
from backend.app.schemas.chat import ArtifactSummary, GroundedSource
from backend.app.services.llm_provider import llm_manager

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions ordered by last updated timestamp."""
    result = await db.execute(
        select(SessionModel).order_by(SessionModel.updated_at.desc())
    )
    sessions = result.scalars().all()

    response = []
    for s in sessions:
        # Count messages
        msg_count_res = await db.execute(
            select(func.count(MessageModel.id)).where(MessageModel.session_id == s.id)
        )
        msg_count = msg_count_res.scalar() or 0
        response.append(
            SessionResponse(
                id=s.id,
                title=s.title,
                model_used=s.model_used,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=msg_count,
            )
        )
    return response


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate = SessionCreate(),
    db: AsyncSession = Depends(get_db),
):
    """Create a new isolated chat session."""
    session_id = str(uuid.uuid4())
    model_name = payload.model_used or f"{llm_manager.active_provider_name}"

    new_session = SessionModel(
        id=session_id,
        title=payload.title or "New Conversation",
        model_used=model_name,
    )
    db.add(new_session)
    await db.flush()
    await db.refresh(new_session)

    return SessionResponse(
        id=new_session.id,
        title=new_session.title,
        model_used=new_session.model_used,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        message_count=0,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve complete session history including messages and artifacts."""
    result = await db.execute(
        select(SessionModel)
        .options(
            selectinload(SessionModel.messages),
            selectinload(SessionModel.artifacts),
        )
        .where(SessionModel.id == session_id)
    )
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    # Format messages
    messages_out = []
    for m in session_obj.messages:
        sources_list = [GroundedSource(**s) for s in m.sources] if m.sources else []
        messages_out.append(
            MessageItem(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=sources_list,
                artifact_id=m.artifact_id,
                created_at=m.created_at,
            )
        )

    # Format artifacts
    artifacts_out = []
    for a in session_obj.artifacts:
        artifacts_out.append(
            ArtifactSummary(
                id=a.id,
                title=a.title,
                type=a.type,
                content=a.content,
                created_at=a.created_at,
            )
        )

    return SessionDetailResponse(
        id=session_obj.id,
        title=session_obj.title,
        model_used=session_obj.model_used,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=messages_out,
        artifacts=artifacts_out,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all its associated messages and artifacts."""
    result = await db.execute(
        select(SessionModel).where(SessionModel.id == session_id)
    )
    session_obj = result.scalar_one_or_none()
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    await db.delete(session_obj)
    return None
