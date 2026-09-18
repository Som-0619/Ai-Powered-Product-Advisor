"""API v1 master router."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.search import router as search_router
from app.api.v1.recommend import router as recommend_router
from app.api.v1.products import router as products_router
from app.api.v1.runs import router as runs_router
from app.api.v1.ingestion import router as ingestion_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(recommend_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(runs_router)
api_v1_router.include_router(ingestion_router)

