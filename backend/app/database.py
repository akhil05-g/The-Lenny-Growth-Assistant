"""Database persistence engine with transparent failover."""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.config import settings

logger = logging.getLogger("lenny_assistant.database")

Base = declarative_base()

# Configure engine with fallback
db_url = settings.DATABASE_URL

# Fallback mechanism if postgres fails or SQLite default
FALLBACK_SQLITE_URL = "sqlite+aiosqlite:///./lenny_assistant.db"

try:
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )
except Exception as e:
    logger.warning(
        f"Failed to initialize engine for {db_url}: {e}. Falling back to SQLite."
    )
    engine = create_async_engine(
        FALLBACK_SQLITE_URL,
        echo=False,
        future=True,
    )

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    global engine, async_session_factory
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized successfully at {engine.url}")
    except Exception as e:
        logger.warning(f"Error connecting to primary DB ({e}). Falling back to local SQLite.")
        engine = create_async_engine(FALLBACK_SQLITE_URL, echo=False, future=True)
        async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully on local SQLite fallback.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining async database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
