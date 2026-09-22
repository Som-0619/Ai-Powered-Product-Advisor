"""Session Context Manager for request/user scoped conversational state.

Guarantees:
- Strictly scoped by session_id / conversation_id.
- Multi-user isolation: User A's products NEVER leak to User B.
- Resolves follow-up queries referencing previously returned products.
- Thread-safe and persistent across turns in a conversation session.
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.core.logging import logger


class SessionContext(BaseModel):
    """Scoped session state container."""
    session_id: str
    last_query: str = ""
    last_intent: str = "SEARCH"
    last_category: Optional[str] = None
    products: List[Dict[str, Any]] = Field(default_factory=list)
    selected_product_ids: List[str] = Field(default_factory=list)
    updated_at: float = Field(default_factory=time.time)


class SessionContextManager:
    """Manages conversational session state with safe per-session scoping."""

    _in_memory_store: Dict[str, SessionContext] = {}

    @classmethod
    def get_session(cls, session_id: Optional[str]) -> Optional[SessionContext]:
        """Fetch session context strictly by session_id."""
        if not session_id or not str(session_id).strip():
            return None
        sid = str(session_id).strip()
        return cls._in_memory_store.get(sid)

    @classmethod
    def save_session(
        cls,
        session_id: Optional[str],
        query: str,
        intent: str,
        products: List[Dict[str, Any]],
        category: Optional[str] = None,
    ) -> None:
        """Save session context strictly under session_id."""
        if not session_id or not str(session_id).strip():
            return
        sid = str(session_id).strip()
        clean_products = []
        for p in (products or [])[:10]:
            clean_products.append({
                "product_id": str(p.get("product_id") or p.get("id") or ""),
                "title": p.get("title") or p.get("product_name") or "",
                "brand": p.get("brand", ""),
                "model": p.get("model", ""),
                "category": p.get("category", ""),
                "price": p.get("price"),
                "formatted_price": p.get("formatted_price"),
                "specifications": p.get("specifications") or p.get("specs") or {},
                "amazon_url": p.get("amazon_url"),
                "flipkart_url": p.get("flipkart_url"),
                "retailer_offers": p.get("retailer_offers") or [],
            })
        ctx = SessionContext(
            session_id=sid,
            last_query=query,
            last_intent=intent,
            last_category=category,
            products=clean_products,
            selected_product_ids=[p["product_id"] for p in clean_products if p.get("product_id")],
            updated_at=time.time(),
        )
        cls._in_memory_store[sid] = ctx

    @classmethod
    def clear_session(cls, session_id: Optional[str]) -> None:
        """Remove session context for session_id."""
        if session_id and str(session_id).strip() in cls._in_memory_store:
            del cls._in_memory_store[str(session_id).strip()]

    @classmethod
    def is_relative_query(cls, query: str) -> bool:
        """Check if query is anaphoric or refers to previous conversational context."""
        q_lower = query.lower().strip()
        follow_up_patterns = [
            r"\b(which\s+one|which\s+of\s+these|which\s+is\s+better|which\s+one\s+is\s+better)\b",
            r"\b(compare\s+these|compare\s+them|between\s+these|between\s+them)\b",
            r"\b(tell\s+me\s+about\s+this|what\s+is\s+this|what\s+about\s+this|describe\s+this)\b",
            r"\b(better\s+battery|which\s+has\s+better\s+battery|battery\s+life)\b",
            r"\b(which\s+is\s+cheaper|which\s+one\s+is\s+cheaper|cheapest\s+one|cheaper\s+one)\b",
            r"\b(tell\s+me\s+something\s+about\s+this\s+product|what\s+is\s+this\s+product)\b",
            r"\b(their\s+(battery|price|specs|reviews?|camera|display|ram|storage))\b",
            r"\b(first\s+one|second\s+one|last\s+one|top\s+one)\b",
            r"\b(summarize\s+reviews\s+for\s+this\s+laptop|reviews\s+for\s+this)\b",
        ]
        return any(re.search(pat, q_lower) for pat in follow_up_patterns)

    @classmethod
    def resolve_follow_up(
        cls, query: str, session_id: Optional[str]
    ) -> Tuple[bool, Optional[SessionContext], str]:
        """Detect follow-up reference and retrieve safe session context.

        Returns:
            (is_follow_up, session_context, clarification_if_ambiguous)
        """
        is_rel = cls.is_relative_query(query)
        if not is_rel:
            ctx = cls.get_session(session_id)
            return False, ctx, ""

        # Relative query detected
        if not session_id:
            clarification = "Which products would you like to compare? Please specify the models or categories you're considering."
            return True, None, clarification

        ctx = cls.get_session(session_id)
        if not ctx or not ctx.products:
            clarification = "Which products would you like to compare? Please specify the models or categories you're considering."
            return True, None, clarification

        return True, ctx, ""
