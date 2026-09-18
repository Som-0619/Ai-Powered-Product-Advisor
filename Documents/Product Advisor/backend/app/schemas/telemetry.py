"""Schemas for AgentRun, AgentStep, and ModelCall."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ModelCallBase(BaseModel):
    model_name: str
    model_type: str = "fast"
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class ModelCallCreate(ModelCallBase):
    step_id: Optional[uuid.UUID] = None


class ModelCallRead(ModelCallBase):
    id: uuid.UUID
    step_id: Optional[uuid.UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AgentStepBase(BaseModel):
    agent_name: str
    step_order: int
    status: str = "completed"
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0


class AgentStepCreate(AgentStepBase):
    run_id: uuid.UUID


class AgentStepRead(AgentStepBase):
    id: uuid.UUID
    run_id: uuid.UUID
    created_at: datetime
    model_calls: List[ModelCallRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class AgentRunBase(BaseModel):
    request_id: str
    user_query: str
    status: str = "running"
    total_latency_ms: Optional[float] = None
    result_json: Dict[str, Any] = Field(default_factory=dict)


class AgentRunCreate(AgentRunBase):
    pass


class AgentRunRead(AgentRunBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    steps: List[AgentStepRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
