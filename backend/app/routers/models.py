"""Model Switcher and Telemetry Router."""

from fastapi import APIRouter, HTTPException, status
from typing import List

from backend.app.schemas.model import (
    ModelListResponse,
    ModelSwitchRequest,
    ModelInfo,
)
from backend.app.services.llm_provider import llm_manager

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get("", response_model=ModelListResponse)
async def list_models():
    """List available LLM providers, active selection, and health telemetry."""
    telemetry = await llm_manager.get_available_models_telemetry()
    models_out = [ModelInfo(**t) for t in telemetry]

    active_provider = llm_manager.active_provider_name
    active_inst = llm_manager.get_active_provider()
    active_model_name = getattr(active_inst, "model_name", active_provider)

    return ModelListResponse(
        active_provider=active_provider,
        active_model=active_model_name,
        models=models_out,
    )


@router.post("/switch", response_model=ModelListResponse)
async def switch_model(payload: ModelSwitchRequest):
    """Switch active LLM model or provider."""
    try:
        llm_manager.set_active_provider(payload.provider, payload.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return await list_models()
