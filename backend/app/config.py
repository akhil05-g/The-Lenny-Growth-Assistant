"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EPISODES_DIR = DATA_DIR / "episodes"
INDEX_DIR = DATA_DIR / "index"


class Settings(BaseSettings):
    """System-wide configuration settings with validation."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Persistence settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./lenny_assistant.db"

    # LLM Settings
    # Switch by setting ACTIVE_PROVIDER=anthropic (or ollama/openai/resilient_local) in .env
    ACTIVE_PROVIDER: Literal["ollama", "anthropic", "claude", "openai", "resilient_local"] = "ollama"

    # Ollama Local Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"

    # Cloud Provider Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"  # claude-sonnet-4-6 per assignment spec

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    # Knowledge Base settings
    TRANSCRIPTS_DATA_DIR: str = str(EPISODES_DIR)
    INDEX_DATA_DIR: str = str(INDEX_DIR)
    TOP_K_RETRIEVAL: int = 5
    MAX_CONTEXT_TOKENS: int = 3500

    # Observability
    LOG_LEVEL: str = "INFO"
    ENABLE_QUERY_TELEMETRY: bool = True


settings = Settings()
