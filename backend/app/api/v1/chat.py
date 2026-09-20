"""Chat endpoint router providing multi-agent conversational advisor intelligence."""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.orchestrator import orchestrator

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message or query")
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Conversational product intelligence endpoint executing multi-agent evaluation."""
    result = await orchestrator.run(
        user_query=request.message,
    )

    # Formulate conversational reply
    reply_text = ""
    if result.get("status") == "clarification":
        reply_text = result.get("clarification_question") or "Could you clarify what you need?"
    elif result.get("status") == "no_results":
        reply_text = result.get("message") or "I couldn't find matching products for that query."
    else:
        rec_count = len(result.get("recommendations", []))
        top_name = result["recommendations"][0]["product_name"] if rec_count > 0 else "matching items"
        reply_text = f"I evaluated available options across engineering specifications, real reviews, and verified benchmarks. Based on your criteria, my top recommendation is {top_name}."

    return {
        "status": result.get("status", "success"),
        "session_id": request.session_id or result.get("request_id"),
        "request_id": result.get("request_id"),
        "reply": reply_text,
        "recommendations": result.get("recommendations", []),
        "intent": result.get("intent", {}),
        "trace": result.get("trace", []),
        "verification": result.get("verification", {}),
    }


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Server-Sent Events streaming chat endpoint with real-time agent execution progress."""
    async def event_generator():
        async for event in orchestrator.execute_stream(user_query=request.message):
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
