"""Health and readiness schemas with healthy, degraded, and not_ready distinction."""

from typing import Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    name: str
    status: Literal["healthy", "degraded", "not_ready"] = Field(
        ..., description="'healthy', 'degraded', or 'not_ready'"
    )
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "not_ready"] = "healthy"
    version: str
    timestamp: str
    environment: str


class ReadyResponse(BaseModel):
    status: Literal["healthy", "degraded", "not_ready"] = Field(
        ..., description="'healthy', 'degraded', or 'not_ready'"
    )
    version: str
    timestamp: str
    environment: str
    services: Dict[str, ServiceStatus]
