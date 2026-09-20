import asyncio
import time
from typing import Any, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger
from app.services.database import DatabaseService


class LocalPostgresService(DatabaseService):
    def __init__(self, db_url: str = None):
        self._db_url = db_url or settings.async_database_url
        self._engine: AsyncEngine = None
        self._session_factory: async_sessionmaker[AsyncSession] = None
        self._loop = None

    async def connect(self) -> None:
        current_loop = asyncio.get_running_loop()
        if self._engine and self._loop != current_loop:
            self._engine = None
            self._session_factory = None

        if not self._engine:
            self._loop = current_loop
            self._engine = create_async_engine(
                self._db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
            self._session_factory = async_sessionmaker(
                self._engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            logger.info("Connected to PostgreSQL engine", extra={"url": self._db_url.split("@")[-1]})


    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            logger.info("Disconnected from PostgreSQL engine")

    async def health_check(self) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            if not self._engine:
                await self.connect()
            async with self._engine.connect() as conn:
                result = await conn.execute(text("SELECT 1;"))
                scalar = result.scalar()
                latency = round((time.perf_counter() - start) * 1000, 2)
                if scalar == 1:
                    return {
                        "status": "ok",
                        "latency_ms": latency,
                        "details": {"connected": True, "database": settings.POSTGRES_DB},
                    }
                return {"status": "degraded", "latency_ms": latency, "error": "Unexpected scalar"}
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def session(self):
        """Async context manager yielding an active AsyncSession."""
        current_loop = asyncio.get_running_loop()
        if self._engine and self._loop != current_loop:
            self._engine = None
            self._session_factory = None

        if not self._session_factory:
            await self.connect()
        async with self._session_factory() as s:
            yield s


