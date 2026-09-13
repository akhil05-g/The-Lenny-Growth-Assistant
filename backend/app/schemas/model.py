"""Pydantic schemas for Model Switching and Provider Telemetry."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Telemetry information for an LLM model/provider option."""
    id: str
    name: str
    provider: str  # "ollama", "claude", "openai", "resilient_local"
    is_available: bool
    is_active: bool
    description: str
    latency_ms: Optional[float] = None


class ModelListResponse(BaseModel):
    """Response containing active provider and list of configured models."""
    active_provider: str
    active_model: str
    models: List[ModelInfo]


class ModelSwitchRequest(BaseModel):
    """Request to switch active LLM provider or model."""
    provider: str = Field(..., description="ollama | claude | openai | resilient_local")
    model_name: Optional[str] = Field(None, description="Model identifier (e.g. llama3.2, claude-3-5-sonnet-20241022)")
