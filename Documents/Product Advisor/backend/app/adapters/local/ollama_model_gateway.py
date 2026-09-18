"""Local Ollama ModelGateway adapter implementing ModelGateway using LangChain.

This adapter provides the LLM abstraction over local Ollama runtime for Product Advisor.
It enforces timeouts, bounded retries, structured outputs, telemetry, model metadata,
request IDs, and strict model availability verification.
"""

import asyncio
import base64
import json
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

import httpx
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ModelUnavailableError
from app.services.model_gateway import (
    ModelGateway,
    ModelResponse,
    ModelRole,
    ModelCallMetadata,
)

T = TypeVar("T")


class LocalOllamaModelGateway(ModelGateway):
    """Production LangChain-backed ModelGateway for local Ollama runtime."""

    def __init__(self):
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
        self._client_loop: Optional[asyncio.AbstractEventLoop] = None
        self._llm_cache: Dict[Tuple[str, float, float, int, int], ChatOllama] = {}

    def _get_client(self) -> httpx.AsyncClient:
        """Get or recreate an AsyncClient bound to the current running event loop."""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is None or self._client.is_closed or self._client_loop is not current_loop:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)
            self._client_loop = current_loop
        return self._client

    async def connect(self) -> None:
        """Initialize connection and check Ollama runtime connectivity."""
        logger.info("Initializing Ollama ModelGateway", extra={"base_url": self._base_url})
        try:
            client = self._get_client()
            res = await client.get("/api/tags")
            if res.status_code == 200:
                models = [m.get("name", "") for m in res.json().get("models", [])]
                logger.info("Ollama runtime connected", extra={"available_models": models})
            else:
                logger.warning(f"Ollama returned status code {res.status_code} during connect")
        except Exception as exc:
            logger.error(f"Failed to connect to Ollama runtime at {self._base_url}: {exc}")

    async def get_available_models(self) -> List[str]:
        """Fetch list of model tags currently available in the local Ollama instance."""
        try:
            client = self._get_client()
            res = await client.get("/api/tags")
            if res.status_code == 200:
                data = res.json()
                return [m.get("name", "") for m in data.get("models", [])]
            return []
        except Exception as exc:
            logger.warning(f"Failed to query Ollama tags: {exc}")
            return []


    def _is_model_available(self, target_model: str, available_models: List[str]) -> bool:
        """Check if target_model is present in available_models (allowing flexible tag matching)."""
        target_clean = target_model.strip()
        for avail in available_models:
            avail_clean = avail.strip()
            if target_clean == avail_clean:
                return True
            # Match e.g. "qwen:4b" with "qwen:4b" or "qwen:4b-latest"
            if target_clean in avail_clean or avail_clean.startswith(f"{target_clean}:"):
                return True
            # Match base tag without ":latest"
            if ":" not in target_clean and avail_clean.startswith(f"{target_clean}:"):
                return True
        return False

    async def validate_models(self) -> Dict[str, Any]:
        """Verify configured models exist in Ollama. Reports exact missing models and commands."""
        available = await self.get_available_models()
        roles_to_check = [
            (ModelRole.FAST.value, settings.FAST_MODEL),
            (ModelRole.REASONING.value, settings.REASONING_MODEL),
            (ModelRole.VISION.value, settings.VISION_MODEL),
        ]

        missing = []
        for role, model in roles_to_check:
            if not self._is_model_available(model, available):
                missing.append({
                    "role": role,
                    "model": model,
                    "remediation": f"ollama pull {model}",
                })

        is_valid = len(missing) == 0
        report = {
            "valid": is_valid,
            "available_models": available,
            "configured_models": {
                "fast": settings.FAST_MODEL,
                "reasoning": settings.REASONING_MODEL,
                "vision": settings.VISION_MODEL,
            },
            "missing_models": missing,
        }

        if not is_valid:
            logger.warning(
                "Configured models are missing in Ollama runtime",
                extra={"missing": missing, "available": available},
            )
        else:
            logger.info("All configured models are available in Ollama runtime", extra={"available": available})

        return report

    async def health_check(self) -> Dict[str, Any]:
        """Check runtime connectivity, latency, and configured model status."""
        start = time.perf_counter()
        try:
            client = self._get_client()
            res = await client.get("/api/tags")
            latency = round((time.perf_counter() - start) * 1000, 2)
            if res.status_code == 200:
                models = [m.get("name") for m in res.json().get("models", [])]
                is_fast = self._is_model_available(settings.FAST_MODEL, models)
                is_reas = self._is_model_available(settings.REASONING_MODEL, models)
                is_vis = self._is_model_available(settings.VISION_MODEL, models)

                status = "ok" if is_fast else "degraded"
                return {
                    "status": status,
                    "latency_ms": latency,
                    "details": {
                        "runtime": "ollama",
                        "available_models": models,
                        "configured_fast_model": settings.FAST_MODEL,
                        "configured_reasoning_model": settings.REASONING_MODEL,
                        "configured_vision_model": settings.VISION_MODEL,
                        "models_status": {
                            "fast_model": "available" if is_fast else "missing",
                            "reasoning_model": "available" if is_reas else "missing",
                            "vision_model": "available" if is_vis else "missing",
                        },
                    },
                }
            return {
                "status": "degraded",
                "latency_ms": latency,
                "error": f"Ollama returned HTTP {res.status_code}",
            }
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    def _get_chat_model(
        self,
        model_name: str,
        temperature: float = 0.1,
        timeout: Optional[float] = None,
        num_ctx: int = 2048,
    ) -> ChatOllama:
        """Retrieve or construct a cached LangChain ChatOllama instance bound to active loop."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        loop_id = id(loop) if loop else 0

        timeout_val = timeout if timeout is not None else settings.LLM_TIMEOUT_SECONDS
        cache_key = (model_name, round(temperature, 2), timeout_val, num_ctx, loop_id)
        if cache_key not in self._llm_cache:
            self._llm_cache[cache_key] = ChatOllama(
                base_url=self._base_url,
                model=model_name,
                temperature=temperature,
                timeout=timeout_val,
                num_ctx=num_ctx,
                num_predict=384,
            )
        return self._llm_cache[cache_key]


    async def _assert_model_available(self, model_name: str, role: str) -> None:
        """Verify model tag exists in Ollama before invocation, raising ModelUnavailableError if not."""
        available = await self.get_available_models()
        if not self._is_model_available(model_name, available):
            msg = (
                f"Model '{model_name}' configured for role '{role}' is not available in local Ollama runtime. "
                f"Available models: {available}. "
                f"Please pull the model using: `ollama pull {model_name}`."
            )
            logger.error(msg, extra={"role": role, "requested_model": model_name, "available_models": available})
            raise ModelUnavailableError(msg)

    def _extract_token_usage(self, raw_response: Any) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Extract prompt, completion, and total tokens from LangChain AIMessage."""
        usage = getattr(raw_response, "usage_metadata", None)
        if usage:
            prompt_tokens = usage.get("input_tokens")
            completion_tokens = usage.get("output_tokens")
            total_tokens = usage.get("total_tokens")
            return prompt_tokens, completion_tokens, total_tokens

        resp_meta = getattr(raw_response, "response_metadata", {})
        prompt_tokens = resp_meta.get("prompt_eval_count")
        completion_tokens = resp_meta.get("eval_count")
        total_tokens = None
        if prompt_tokens is not None or completion_tokens is not None:
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)
        return prompt_tokens, completion_tokens, total_tokens

    async def _invoke_with_retry(
        self,
        invoker_fn,
        operation_name: str,
        request_id: str,
        max_retries: int,
    ) -> Any:
        """Execute async LLM operation with bounded retries and exponential backoff."""
        attempt = 0
        last_error = None

        while attempt <= max_retries:
            try:
                return await invoker_fn()
            except ModelUnavailableError:
                # Do not retry if model is explicitly missing
                raise
            except Exception as exc:
                err_str = str(exc)
                if "not found" in err_str.lower() and "model" in err_str.lower():
                    # Ollama model not found 404
                    raise ModelUnavailableError(f"Ollama reported model not found: {err_str}") from exc

                last_error = exc
                if attempt < max_retries:
                    backoff = min(1.0 * (2 ** attempt), 8.0)
                    logger.warning(
                        f"LLM call {operation_name} failed (attempt {attempt + 1}/{max_retries + 1}). Retrying in {backoff:.1f}s. Error: {exc}",
                        extra={"request_id": request_id, "attempt": attempt + 1, "operation": operation_name},
                    )
                    await asyncio.sleep(backoff)
                    attempt += 1
                else:
                    logger.error(
                        f"LLM call {operation_name} exhausted all {max_retries + 1} attempts. Final error: {exc}",
                        extra={"request_id": request_id, "operation": operation_name},
                    )
                    raise exc

        raise last_error or RuntimeError(f"Unknown error during {operation_name}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[str]:
        """Standard fast LLM generation (Qwen 4B).
        
        Roles: classification, intent extraction, structured extraction,
        simple summarization, simple review analysis.
        """
        req_id = request_id or str(uuid.uuid4())
        model_name = settings.FAST_MODEL
        role = ModelRole.FAST.value

        await self._assert_model_available(model_name, role)
        llm = self._get_chat_model(model_name=model_name, temperature=temperature, timeout=timeout)

        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        start_time = time.perf_counter()

        async def _call():
            return await llm.ainvoke(messages)

        raw_res = await self._invoke_with_retry(
            _call,
            operation_name=f"generate:{model_name}",
            request_id=req_id,
            max_retries=max_retries,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        prompt_tokens, completion_tokens, total_tokens = self._extract_token_usage(raw_res)

        content = raw_res.content if isinstance(raw_res.content, str) else str(raw_res.content)

        logger.info(
            "Fast generation completed",
            extra={
                "request_id": req_id,
                "model": model_name,
                "role": role,
                "latency_ms": latency_ms,
                "tokens": total_tokens,
            },
        )

        return ModelResponse(
            content=content,
            model=model_name,
            role=role,
            request_id=req_id,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            metadata={"system_prompt_present": bool(system_prompt)},
        )

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
        req_id = request_id or str(uuid.uuid4())
        model_name = settings.FAST_MODEL
        role = ModelRole.FAST.value

        await self._assert_model_available(model_name, role)
        llm = self._get_chat_model(model_name=model_name, temperature=temperature, timeout=timeout)

        # Use LangChain structured output with include_raw=True for telemetry
        structured_llm = llm.with_structured_output(schema, include_raw=True)

        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        start_time = time.perf_counter()

        async def _call():
            res_dict = await structured_llm.ainvoke(messages)
            # If parsing failed directly, attempt JSON extraction fallback
            if res_dict.get("parsed") is not None:
                return res_dict
            
            raw_msg = res_dict.get("raw")
            raw_content = getattr(raw_msg, "content", "") if raw_msg else ""
            parsed_obj = self._fallback_parse_json(raw_content, schema)
            if parsed_obj is not None:
                res_dict["parsed"] = parsed_obj
                return res_dict
            
            raise ValueError(
                f"Failed to parse structured output for {schema.__name__}. Error: {res_dict.get('parsing_error')}"
            )

        res_dict = await self._invoke_with_retry(
            _call,
            operation_name=f"generate_structured:{schema.__name__}",
            request_id=req_id,
            max_retries=max_retries,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raw_msg = res_dict.get("raw")
        prompt_tokens, completion_tokens, total_tokens = self._extract_token_usage(raw_msg)
        parsed_result = res_dict["parsed"]

        logger.info(
            "Structured generation completed",
            extra={
                "request_id": req_id,
                "model": model_name,
                "role": role,
                "schema": schema.__name__,
                "latency_ms": latency_ms,
                "tokens": total_tokens,
            },
        )

        return ModelResponse(
            content=parsed_result,
            model=model_name,
            role=role,
            request_id=req_id,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            metadata={"schema": schema.__name__},
        )

    def _fallback_parse_json(self, text: str, schema: Type[T]) -> Optional[T]:
        """Extract and validate JSON block from markdown code fences or loose JSON string."""
        try:
            # 1. Check for markdown code blocks ```json ... ```
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                payload = json.loads(match.group(1))
                return schema.model_validate(payload)
            # 2. Check for outermost curly braces
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                payload = json.loads(match.group(1))
                return schema.model_validate(payload)
        except Exception:
            return None
        return None

    async def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        request_id: Optional[str] = None,
    ) -> ModelResponse[str]:
        """Deep reasoning generation using the reasoning model (Qwen 8B / 7B).
        
        Roles: technical reasoning, compatibility reasoning, complex comparison,
        evidence synthesis, critic reasoning.
        """
        req_id = request_id or str(uuid.uuid4())
        model_name = settings.REASONING_MODEL
        role = ModelRole.REASONING.value

        await self._assert_model_available(model_name, role)
        llm = self._get_chat_model(model_name=model_name, temperature=temperature, timeout=timeout)

        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        start_time = time.perf_counter()

        async def _call():
            return await llm.ainvoke(messages)

        raw_res = await self._invoke_with_retry(
            _call,
            operation_name=f"generate_reasoning:{model_name}",
            request_id=req_id,
            max_retries=max_retries,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        prompt_tokens, completion_tokens, total_tokens = self._extract_token_usage(raw_res)

        content = raw_res.content if isinstance(raw_res.content, str) else str(raw_res.content)

        logger.info(
            "Reasoning generation completed",
            extra={
                "request_id": req_id,
                "model": model_name,
                "role": role,
                "latency_ms": latency_ms,
                "tokens": total_tokens,
            },
        )

        return ModelResponse(
            content=content,
            model=model_name,
            role=role,
            request_id=req_id,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            metadata={"role": "reasoning"},
        )

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
        req_id = request_id or str(uuid.uuid4())
        model_name = settings.VISION_MODEL
        role = ModelRole.VISION.value

        await self._assert_model_available(model_name, role)
        llm = self._get_chat_model(model_name=model_name, temperature=temperature, timeout=timeout)

        # Base64 encode image
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        
        # Build multimodal HumanMessage payload
        content_items = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64_img}"},
        ]

        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=content_items))

        start_time = time.perf_counter()

        async def _call():
            return await llm.ainvoke(messages)

        raw_res = await self._invoke_with_retry(
            _call,
            operation_name=f"generate_with_image:{model_name}",
            request_id=req_id,
            max_retries=max_retries,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        prompt_tokens, completion_tokens, total_tokens = self._extract_token_usage(raw_res)

        content = raw_res.content if isinstance(raw_res.content, str) else str(raw_res.content)

        logger.info(
            "Vision generation completed",
            extra={
                "request_id": req_id,
                "model": model_name,
                "role": role,
                "latency_ms": latency_ms,
                "tokens": total_tokens,
            },
        )

        return ModelResponse(
            content=content,
            model=model_name,
            role=role,
            request_id=req_id,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            metadata={"image_size_bytes": len(image_bytes)},
        )
