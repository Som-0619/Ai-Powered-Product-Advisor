"""Chat endpoint router providing multi-agent conversational advisor intelligence.

Connects to the LangGraph SupervisorAgent and specialist agents via clean tool layers.
Returns structured Section 32 output while preserving streaming and backward compatibility.
"""

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.agents.supervisor import SupervisorAgent
from app.services.orchestrator import orchestrator

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="User search query (Section 32)")
    message: Optional[str] = Field(default=None, description="User message (backward compatibility)")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation identifier")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """Conversational product intelligence endpoint executing multi-agent evaluation."""
    req_start_ts = datetime.now(timezone.utc).isoformat()
    t_api_start = time.perf_counter()
    logger.info(f"[DEV_TRACE] request_start: {req_start_ts}", extra={"request_start": req_start_ts})

    user_query = (request.query or request.message or "").strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="A query or message must be provided.")

    req_id = request.conversation_id or request.session_id
    supervisor = SupervisorAgent()
    result = await supervisor.run(user_query=user_query, request_id=req_id)

    api_latency_ms = round((time.perf_counter() - t_api_start) * 1000, 2)
    logger.info(
        f"[DEV_TRACE] FastAPI latency: {api_latency_ms}ms, total request latency: {api_latency_ms}ms, final product count: {len(result.get('products', []))}",
        extra={
            "fastapi_latency_ms": api_latency_ms,
            "total_request_latency_ms": api_latency_ms,
            "final_product_count": len(result.get("products", [])),
            "request_id": req_id,
        },
    )

    # Format products for frontend backward-compatibility
    frontend_recs = []
    for p in result.get("products", []):
        frontend_recs.append({
            "product_id": p.get("product_id"),
            "product_name": p.get("title") or f"{p.get('brand', '')} {p.get('model', '')}".strip(),
            "brand": p.get("brand", ""),
            "model": p.get("model", ""),
            "category": p.get("category", ""),
            "price": p.get("price"),
            "final_score": p.get("final_score", 0.0),
            "score": p.get("final_score", 0.0),
            "image_url": p.get("primary_image_url"),
            "specifications": p.get("specifications", {}),
            "eligible": p.get("eligible", True),
        })

    # Section 32 structured response with backward-compatibility fields
    return {
        "answer": result.get("answer", ""),
        "products": result.get("products", []),
        "evidence": result.get("evidence", []),
        "reviews": result.get("reviews", []),
        "compatibility": result.get("compatibility", []),
        "visual_findings": result.get("visual_findings", []),
        "retailer_offers": result.get("retailer_offers", []),
        "warnings": result.get("warnings", []),
        "confidence": result.get("confidence", 1.0),
        # Backward compatibility for existing UI
        "reply": result.get("answer", ""),
        "recommendations": frontend_recs,
        "status": result.get("status", "success"),
        "session_id": request.session_id or request.conversation_id or result.get("request_id"),
        "request_id": result.get("request_id"),
        "trace": result.get("trace", []),
        "verification": result.get("verification", {}),
    }


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Server-Sent Events streaming chat endpoint with real-time agent execution progress."""
    user_query = (request.query or request.message or "").strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="A query or message must be provided.")

    async def event_generator():
        async for event in orchestrator.execute_stream(user_query=user_query):
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
