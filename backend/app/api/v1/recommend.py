"""Recommendation endpoint router connecting real multi-agent supervisor execution."""

import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.orchestrator import orchestrator

router = APIRouter(tags=["recommend"])


class RecommendRequest(BaseModel):
    query: str = Field(..., description="Natural language search or product query")
    constraints: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@router.post("/recommend")
async def recommend_endpoint(request: RecommendRequest):
    """Deterministic recommendation & verification endpoint executing the full multi-agent pipeline."""
    result = await orchestrator.run(
        user_query=request.query,
        request_id=request.request_id,
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
