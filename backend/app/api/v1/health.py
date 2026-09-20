"""Health and readiness endpoints distinguishing healthy, degraded, and not_ready."""

import asyncio
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends
from app import __version__
from app.core.config import settings
from app.schemas.health import HealthResponse, ReadyResponse, ServiceStatus
from app.services.factory import (
    get_db_service,
    get_search_service,
    get_cache_service,
    get_storage_service,
    get_model_gateway,
    DatabaseService,
    SearchService,
    CacheService,
    StorageService,
    ModelGateway,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness probe: returns 200 and 'healthy' if FastAPI process is operational."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(
    db: DatabaseService = Depends(get_db_service),
    search: SearchService = Depends(get_search_service),
    cache: CacheService = Depends(get_cache_service),
    storage: StorageService = Depends(get_storage_service),
    llm: ModelGateway = Depends(get_model_gateway),
) -> ReadyResponse:
    """Readiness probe: checks dependencies and reports 'healthy', 'degraded', or 'not_ready'."""
    db_task = db.health_check()
    search_task = search.health_check()
    cache_task = cache.health_check()
    storage_task = storage.health_check()
    llm_task = llm.health_check()

    db_res, search_res, cache_res, storage_res, llm_res = await asyncio.gather(
        db_task, search_task, cache_task, storage_task, llm_task, return_exceptions=True
    )

    def _normalize(name: str, res) -> ServiceStatus:
        if isinstance(res, Exception):
            return ServiceStatus(name=name, status="not_ready", error=str(res))
        raw_status = res.get("status", "not_ready")
        if raw_status in ("ok", "healthy"):
            norm_status: Literal["healthy", "degraded", "not_ready"] = "healthy"
        elif raw_status == "degraded":
            norm_status = "degraded"
        else:
            norm_status = "not_ready"

        return ServiceStatus(
            name=name,
            status=norm_status,
            latency_ms=res.get("latency_ms"),
            details=res.get("details"),
            error=res.get("error"),
        )

    services = {
        "postgres": _normalize("postgres", db_res),
        "opensearch": _normalize("opensearch", search_res),
        "redis": _normalize("redis", cache_res),
        "minio": _normalize("minio", storage_res),
        "ollama": _normalize("ollama", llm_res),
    }

    # Classification logic:
    # 1. If critical data store (postgres, opensearch, redis) is down -> not_ready
    critical = ["postgres", "opensearch", "redis"]
    is_critical_down = any(services[k].status == "not_ready" for k in critical)

    if is_critical_down:
        overall_status: Literal["healthy", "degraded", "not_ready"] = "not_ready"
    elif any(s.status in ("degraded", "not_ready") for s in services.values()):
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return ReadyResponse(
        status=overall_status,
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        services=services,
    )
