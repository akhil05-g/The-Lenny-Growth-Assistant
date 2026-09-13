"""Pydantic schemas for Artifact representations."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ArtifactResponse(BaseModel):
    """Schema for retrieved rendered artifact."""
    id: str
    session_id: str
    title: str
    type: Literal["markdown", "html"]
    content: str
    created_at: datetime


class ArtifactCreate(BaseModel):
    """Schema for manual or programmatic artifact creation."""
    session_id: str
    title: str = Field(..., min_length=1)
    type: Literal["markdown", "html"] = "markdown"
    content: str = Field(..., min_length=1)
