"""LLM client with error handling and security measures."""

import asyncio
from functools import lru_cache
from typing import Any, Dict, Optional

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

from app.core.config import get_settings
from app.utils.exceptions import LLMError, RateLimitError

logger = structlog.get_logger(__name__)


class SecureLLMClient:
    """Secure LLM client with rate limiting and error handling."""

    def __init__(self, temperature: float = 0.3):
        self.settings = get_settings()
        self.temperature = temperature
        self._client: Optional[ChatOpenAI] = None
        self._rate_limiter = asyncio.Semaphore(
            self.settings.rate_limit_per_minute
        )

    @property
    def client(self) -> ChatOpenAI:
        """Get or create LLM client."""
        if self._client is None:
            self._client = ChatOpenAI(
                model=self.settings.model_name,
                openai_api_key=self.settings.openrouter_api_key,
                openai_api_base=self.settings.openrouter_base_url,
                temperature=self.temperature,
                timeout=self.settings.request_timeout,
                max_retries=self.settings.max_retries,
            )
        return self._client

    async def invoke(self, messages: list[BaseMessage]) -> str:
        """Invoke LLM with rate limiting and error handling."""
        async with self._rate_limiter:
            try:
                logger.info("invoking_llm", model=self.settings.model_name)
                
                response = await asyncio.to_thread(
                    self.client.invoke,
                    messages
                )
                
                logger.info("llm_response_received", length=len(response.content))
                return response.content
                
            except Exception as e:
                logger.error("llm_invocation_failed", error=str(e))
                
                if "rate limit" in str(e).lower():
                    raise RateLimitError("Rate limit exceeded") from e
                
                raise LLMError(f"LLM invocation failed: {str(e)}") from e

    def validate_input(self, text: str) -> bool:
        """Validate input text for security."""
        if not text or not text.strip():
            return False
            
        if len(text) > 50000:  # Prevent excessive input
            return False
            
        # Add more validation rules as needed
        return True


@lru_cache()
def get_llm_client(temperature: float = 0.3) -> SecureLLMClient:
    """Get cached LLM client instance."""
    return SecureLLMClient(temperature=temperature)