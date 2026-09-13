"""Artifact Parsing, Validation, and Zero-Trust Security Sanitization."""

import re
import html
import logging
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.artifact import ArtifactModel
from backend.app.schemas.chat import ArtifactSummary

logger = logging.getLogger("lenny_assistant.artifact_service")

# Flexible regex to detect :::artifact title="..." type="..." ... ::: blocks (with or without closing :::)
ARTIFACT_REGEX = re.compile(
    r":::artifact\s+title=[\"'](.*?)[\"'](?:\s+type=[\"'](markdown|html)[\"'])?\s*\n?([\s\S]*?)(?:\n?:::|$)",
    re.IGNORECASE,
)

# Secondary XML tag style <artifact title="..." type="...">...</artifact>
TAG_ARTIFACT_REGEX = re.compile(
    r"<artifact\s+title=[\"'](.*?)[\"'](?:\s+type=[\"'](markdown|html)[\"'])?>([\s\S]*?)(?:<\/artifact>|$)",
    re.IGNORECASE,
)

# Raw HTML fence detection if user asked for an artifact
HTML_FENCE_REGEX = re.compile(
    r"```html\s*\n(<!DOCTYPE[\s\S]*?|<html>[\s\S]*?|<div[\s\S]*?)\n```",
    re.IGNORECASE,
)


class ArtifactService:
    """Handles parsing, sanitizing, and persisting generated artifacts."""

    @staticmethod
    def sanitize_html(content: str) -> str:
        """Sanitize raw HTML to prevent injection and script escalation."""
        # Strip malicious script handlers like onclick, onload, onerror, onmouseover
        sanitized = re.sub(r"\s+on\w+\s*=\s*([\"'][^\"']*[\"']|[^\s>]+)", "", content, flags=re.IGNORECASE)
        # Strip dangerous URL schemes
        sanitized = re.sub(r"(href|src)\s*=\s*[\"']\s*(javascript|data|vbscript):[^\"']*[\"']", r'\1="#"', sanitized, flags=re.IGNORECASE)
        return sanitized

    @classmethod
    def extract_artifact(cls, text: str) -> Tuple[str, Optional[dict]]:
        """Extract artifact from model response text, returning clean display text and artifact dict."""
        if not text:
            return text, None

        # Try :::artifact pattern
        match = ARTIFACT_REGEX.search(text)
        if match and match.group(1):
            title = match.group(1).strip()
            art_type = (match.group(2) or "html").lower()
            raw_content = match.group(3).strip()

            if raw_content:
                content = cls.sanitize_html(raw_content) if art_type == "html" else raw_content
                cleaned_text = ARTIFACT_REGEX.sub("", text).strip()
                if not cleaned_text:
                    cleaned_text = f"Here is the interactive {title} generated from Lenny's podcast frameworks:"
                return cleaned_text, {"title": title, "type": art_type, "content": content}

        # Try tag pattern
        match_tag = TAG_ARTIFACT_REGEX.search(text)
        if match_tag and match_tag.group(1):
            title = match_tag.group(1).strip()
            art_type = (match_tag.group(2) or "html").lower()
            raw_content = match_tag.group(3).strip()

            if raw_content:
                content = cls.sanitize_html(raw_content) if art_type == "html" else raw_content
                cleaned_text = TAG_ARTIFACT_REGEX.sub("", text).strip()
                if not cleaned_text:
                    cleaned_text = f"Here is the interactive {title} generated from Lenny's podcast frameworks:"
                return cleaned_text, {"title": title, "type": art_type, "content": content}

        # Try raw HTML fence
        match_fence = HTML_FENCE_REGEX.search(text)
        if match_fence:
            raw_content = match_fence.group(1).strip()
            content = cls.sanitize_html(raw_content)
            cleaned_text = HTML_FENCE_REGEX.sub("", text).strip()
            if not cleaned_text:
                cleaned_text = "Here is the interactive HTML artifact generated from Lenny's podcast frameworks:"
            return cleaned_text, {"title": "Interactive Operational Artifact", "type": "html", "content": content}

        return text, None

    @classmethod
    async def create_and_persist_artifact(
        cls,
        session_id: str,
        artifact_data: dict,
        db: AsyncSession,
    ) -> ArtifactSummary:
        """Persist an artifact to the database and return its summary schema."""
        artifact_record = ArtifactModel(
            session_id=session_id,
            title=artifact_data["title"],
            type=artifact_data["type"],
            content=artifact_data["content"],
        )
        db.add(artifact_record)
        await db.commit()
        await db.refresh(artifact_record)

        return ArtifactSummary(
            id=artifact_record.id,
            title=artifact_record.title,
            type=artifact_record.type,
            content=artifact_record.content,
            created_at=artifact_record.created_at,
        )


artifact_service = ArtifactService()
