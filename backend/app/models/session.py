"""Session database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base


class SessionModel(Base):
    """Represents an isolated conversation session."""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, default="New Conversation")
    model_used = Column(String, nullable=False, default="ollama:llama3.2")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan", order_by="ArtifactModel.created_at")
