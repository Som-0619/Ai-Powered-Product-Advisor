"""Abstract base class and data models for ModelGateway LLM abstraction."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field


class ModelRole(str, Enum):
    """Specialized model roles."""
    FAST = "fast"
    REASONING = "reasoning"
    VISION = "vision"


T = TypeVar("T")


class ModelCallMetadata(BaseModel):
    """Telemetry and execution metadata for an LLM invocation."""
    request_id: str
    model: str
    role: str
    latency_ms: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    additional_kwargs: Dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel, Generic[T]):
    """Standardized response container returned by ModelGateway operations."""
    content: T
    model: str
    role: str
    request_id: str
    latency_ms: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __str__(self) -> str:
        return str(self.content)


class ModelGateway(ABC):
    """ModelGateway abstraction for LLM interactions.
    
    Decouples agent and application code from specific LLM runtimes (Ollama locally,
    Bedrock/SageMaker on AWS). All agents in the system MUST interact with LLMs exclusively
    through this gateway. Direct imports of Ollama or vendor SDKs from agents are forbidden.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection and validate model availability."""
        pass

    @abstractmethod
    async def validate_models(self) -> Dict[str, Any]:
        """Validate configured models are available in the runtime.
        
        Returns a diagnostic dictionary and raises ModelUnavailableError if mandatory
        models are missing.
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check runtime connectivity, latency, and model status."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[str]:
        """Standard fast LLM generation (e.g. Qwen 4B).
        
        Roles: classification, intent extraction, structured extraction,
        simple summarization, simple review analysis.
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[T]:
        """Structured generation validated against a Pydantic schema using the fast model."""
        pass

    @abstractmethod
    async def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[str]:
        """Deep reasoning generation using the reasoning model (e.g. Qwen 7B/8B).
        
        Roles: technical reasoning, compatibility reasoning, complex comparison,
        evidence synthesis, critic reasoning.
        """
        pass

    @abstractmethod
    async def generate_with_image(
        self,
        prompt: str,
        image_bytes: bytes,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[str]:
        """Multimodal image observation generation using a dedicated vision-capable model."""
        pass
