"""Message database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class MessageModel(Base):
    """Represents a conversational message within a session."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True, default=list)  # Grounded source references
    artifact_id = Column(String, ForeignKey("artifacts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("SessionModel", back_populates="messages")
    artifact = relationship("ArtifactModel", foreign_keys=[artifact_id])
