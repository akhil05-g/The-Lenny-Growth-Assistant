"""Pydantic schemas for Chat interactions and Grounded citations."""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class GroundedSource(BaseModel):
    """Represents a grounded transcript reference."""
    episode_title: str
    guest: str
    quote: str
    youtube_url: Optional[str] = None
    timestamp: Optional[str] = None
    relevance_score: float = 0.0


class ArtifactSummary(BaseModel):
    """Inline summary of an associated artifact."""
    id: str
    title: str
    type: Literal["markdown", "html"]
    content: str
    created_at: datetime


class ChatMessageRequest(BaseModel):
    """User prompt request schema."""
    message: str = Field(..., min_length=1, description="User prompt or question")
    session_id: Optional[str] = Field(None, description="Existing session ID, or null to create one")
    model: Optional[str] = Field(None, description="Override active model (e.g. 'ollama:llama3.2', 'claude:claude-3-5-sonnet')")
    skill: Optional[Literal["general", "ship30", "artifact"]] = Field("general", description="Dedicated skill request")


class ChatMessageResponse(BaseModel):
    """Assistant message response schema."""
    id: str
    session_id: str
    role: str = "assistant"
    content: str
    sources: List[GroundedSource] = []
    artifact: Optional[ArtifactSummary] = None
    model_used: str
    created_at: datetime
