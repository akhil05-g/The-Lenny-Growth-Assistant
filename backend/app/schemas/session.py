"""Pydantic schemas for Session management."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.chat import GroundedSource, ArtifactSummary


class SessionCreate(BaseModel):
    """Payload to start a new chat session."""
    title: Optional[str] = Field("New Conversation", description="Custom session title")
    model_used: Optional[str] = Field(None, description="Initial model selection")


class MessageItem(BaseModel):
    """Message item inside a session view."""
    id: str
    role: str
    content: str
    sources: Optional[List[GroundedSource]] = []
    artifact_id: Optional[str] = None
    created_at: datetime


class SessionResponse(BaseModel):
    """Session summary for sidebar list."""
    id: str
    title: str
    model_used: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class SessionDetailResponse(BaseModel):
    """Detailed session view with full message history and generated artifacts."""
    id: str
    title: str
    model_used: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageItem] = []
    artifacts: List[ArtifactSummary] = []
