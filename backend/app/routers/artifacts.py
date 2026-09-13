"""Artifacts Retrieval Router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.artifact import ArtifactModel
from backend.app.schemas.artifact import ArtifactResponse

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve an artifact by its unique ID."""
    result = await db.execute(
        select(ArtifactModel).where(ArtifactModel.id == artifact_id)
    )
    artifact_obj = result.scalar_one_or_none()
    if not artifact_obj:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")

    return ArtifactResponse(
        id=artifact_obj.id,
        session_id=artifact_obj.session_id,
        title=artifact_obj.title,
        type=artifact_obj.type,
        content=artifact_obj.content,
        created_at=artifact_obj.created_at,
    )


@router.get("/session/{session_id}", response_model=List[ArtifactResponse])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    """List all artifacts created during a given chat session."""
    result = await db.execute(
        select(ArtifactModel)
        .where(ArtifactModel.session_id == session_id)
        .order_by(ArtifactModel.created_at.desc())
    )
    artifacts = result.scalars().all()

    return [
        ArtifactResponse(
            id=a.id,
            session_id=a.session_id,
            title=a.title,
            type=a.type,
            content=a.content,
            created_at=a.created_at,
        )
        for a in artifacts
    ]
