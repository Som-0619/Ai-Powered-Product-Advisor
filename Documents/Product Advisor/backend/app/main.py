"""FastAPI application entrypoint for Product Advisor."""

import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app import __version__
from app.core.config import settings
from app.core.logging import logger
from app.services.factory import container
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown initialization."""
    logger.info("Starting Product Advisor API service...", extra={"version": __version__, "env": settings.ENVIRONMENT})

    # Initialize Service Container
    container.initialize()

    # Attempt graceful connectivity to local services (non-fatal during Phase 1 startup)
    try:
        if container.db:
            await container.db.connect()
    except Exception as exc:
        logger.warning(f"Initial DB connection deferred: {exc}")

    try:
        if container.search:
            await container.search.connect()
    except Exception as exc:
        logger.warning(f"Initial Search connection deferred: {exc}")

    try:
        if container.cache:
            await container.cache.connect()
    except Exception as exc:
        logger.warning(f"Initial Cache connection deferred: {exc}")

    try:
        if container.storage:
            await container.storage.connect()
    except Exception as exc:
        logger.warning(f"Initial Storage connection deferred: {exc}")

    try:
        if container.model_gateway:
            await container.model_gateway.connect()
            validation = await container.model_gateway.validate_models()
            if not validation.get("valid"):
                logger.warning(
                    f"Configured models check: missing={validation.get('missing')}. "
                    f"To pull: `docker compose exec ollama ollama pull {settings.FAST_MODEL}`"
                )
    except Exception as exc:
        logger.warning(f"Initial ModelGateway check deferred: {exc}")

    logger.info("Product Advisor backend started successfully.")
    yield

    logger.info("Shutting down Product Advisor API service...")
    if container.db:
        await container.db.disconnect()
    if container.search:
        await container.search.disconnect()
    if container.cache:
        await container.cache.disconnect()
    if container.queue:
        await container.queue.disconnect()
    if container.storage and hasattr(container.storage, "disconnect"):
        await container.storage.disconnect()
    logger.info("Cleanup completed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered multimodal product recommendation and product intelligence platform",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next) -> Response:
    """Injects a unique request ID and logs request latency."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{latency_ms}ms"

    # Only log non-health poll endpoints to keep logs clean
    if not request.url.path.endswith(("/health", "/ready")):
        logger.info(
            f"{request.method} {request.url.path} {response.status_code} ({latency_ms}ms)",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            },
        )
    return response


# Mount API v1
app.include_router(api_v1_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health",
        "ready": "/api/v1/ready",
        "environment": settings.ENVIRONMENT,
    }
