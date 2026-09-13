"""Artifact database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class ArtifactModel(Base):
    """Represents a generated rendered artifact (Markdown or HTML/CSS document)."""
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False, default="Untitled Artifact")
    type = Column(String, nullable=False, default="markdown")  # "markdown" or "html"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("SessionModel", back_populates="artifacts")
