"""Agent telemetry models: AgentRun, AgentStep, ModelCall."""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class AgentRun(Base, UUIDMixin, TimestampMixin):
    """End-to-end execution record of an agent workflow session."""
    __tablename__ = "agent_runs"

    request_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40), default="running", nullable=False, index=True
    )  # "running", "completed", "failed", "requires_clarification"
    total_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    result_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    steps: Mapped[List["AgentStep"]] = relationship("AgentStep", back_populates="run", cascade="all, delete-orphan")


class AgentStep(Base, UUIDMixin, TimestampMixin):
    """Granular execution step within an agent run."""
    __tablename__ = "agent_steps"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_name: Mapped[str] = mapped_column(
        String(80), nullable=False, index=True
    )  # "query_understanding", "retrieval", "review", "parts", "compatibility", "vision", "ranking", "evidence"
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="completed", nullable=False
    )  # "completed", "failed", "retried"
    input_payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    output_payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="steps")
    model_calls: Mapped[List["ModelCall"]] = relationship("ModelCall", back_populates="step", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_agent_steps_run_order", "run_id", "step_order"),
    )


class ModelCall(Base, UUIDMixin, TimestampMixin):
    """Detailed audit entry for each LLM or Vision model invocation."""
    __tablename__ = "model_calls"

    step_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_steps.id", ondelete="CASCADE"), nullable=True, index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. "qwen2.5:3b", "qwen2.5:7b", "llava:7b"
    model_type: Mapped[str] = mapped_column(
        String(40), default="fast", nullable=False
    )  # "fast", "reasoning", "vision", "embedding"
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    step: Mapped[Optional["AgentStep"]] = relationship("AgentStep", back_populates="model_calls")
