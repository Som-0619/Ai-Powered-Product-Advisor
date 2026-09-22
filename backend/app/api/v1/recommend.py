import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.services.orchestrator import orchestrator

router = APIRouter(tags=["recommend"])


class RecommendRequest(BaseModel):
    query: str = Field(..., description="Natural language search or product query")
    constraints: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@router.post("/recommend")
async def recommend_endpoint(request: RecommendRequest):
    """Deterministic recommendation & verification endpoint executing the full multi-agent pipeline."""
    req_start_ts = datetime.now(timezone.utc).isoformat()
    t_api_start = time.perf_counter()
    logger.info(f"[DEV_TRACE] request_start: {req_start_ts}", extra={"request_start": req_start_ts})

    result = await orchestrator.run(
        user_query=request.query,
        request_id=request.request_id,
    )
    api_latency_ms = round((time.perf_counter() - t_api_start) * 1000, 2)
    final_count = len(result.get("recommendations", [])) if isinstance(result, dict) else 0
    logger.info(
        f"[DEV_TRACE] FastAPI latency: {api_latency_ms}ms, total request latency: {api_latency_ms}ms, final product count: {final_count}",
        extra={
            "fastapi_latency_ms": api_latency_ms,
            "total_request_latency_ms": api_latency_ms,
            "final_product_count": final_count,
            "request_id": request.request_id,
        },
    )
    return result


@router.post("/recommend/stream")
async def recommend_stream_post(request: RecommendRequest):
    """Server-Sent Events (SSE) streaming endpoint for real-time agent execution progress."""
    async def event_generator():
        async for event in orchestrator.execute_stream(user_query=request.query, request_id=request.request_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/recommend/stream")
async def recommend_stream_get(query: str = Query(..., description="User query"), request_id: Optional[str] = None):
    """Server-Sent Events (SSE) streaming endpoint via GET for browser EventSource support."""
    async def event_generator():
        async for event in orchestrator.execute_stream(user_query=query, request_id=request_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
