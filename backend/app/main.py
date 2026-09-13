"""FastAPI Main Application Entrypoint for The Lenny Growth Assistant."""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.services.rag_service import rag_service
from backend.app.routers import (
    health_router,
    sessions_router,
    chat_router,
    models_router,
    artifacts_router,
    skills_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lenny_assistant.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting up The Lenny Growth Assistant...")
    # Initialize Database tables
    await init_db()

    # Asynchronously initialize Knowledge Base so server starts immediately
    asyncio.create_task(asyncio.to_thread(rag_service.initialize))

    yield
    logger.info("Shutting down The Lenny Growth Assistant...")


app = FastAPI(
    title="The Lenny Growth Assistant API",
    description=(
        "Enterprise conversational AI assistant strictly grounded in Lenny's Podcast transcripts. "
        "Supports dynamic model toggling (Ollama local + Cloud), Ship 30 for 30 digital essay creation, "
        "and sandboxed interactive artifact generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Register Routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(models_router)
app.include_router(artifacts_router)
app.include_router(skills_router)

# Mount compiled React frontend if present for single-command unified full-stack serving
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Exclude API endpoints and docs
        if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
            return None
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root():
        """Root endpoint fallback when frontend is not built."""
        return {
            "service": "The Lenny Growth Assistant API",
            "status": "online",
            "docs": "/docs",
            "health": "/api/health",
            "version": "1.0.0",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main.app", host=settings.HOST, port=settings.PORT, reload=True)

