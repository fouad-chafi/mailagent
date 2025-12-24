"""
LM Studio service for local LLM inference.
Handles communication with the local LM Studio API.
"""

import asyncio
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


class LLMConnectionError(LLMServiceError):
    pass


class LLMTimeoutError(LLMServiceError):
    pass


class LLMService:
    def __init__(self):
        self.base_url = settings.LM_STUDIO_URL
        self.model = settings.LM_STUDIO_MODEL
        self.timeout = settings.LM_STUDIO_TIMEOUT
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def verify_connection(self) -> dict:
        try:
            client = await self._get_client()
            response = await client.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10,
                },
            )
            response.raise_for_status()
            return {"status": "ok", "model": self.model}
        except httpx.ConnectError as e:
            raise LLMConnectionError(
                "Cannot connect to LM Studio. Please ensure LM Studio is running on "
                f"{self.base_url.replace('/v1/chat/completions', '')}"
            ) from e
        except Exception as e:
            raise LLMServiceError(f"Failed to verify LM Studio connection: {e}") from e

    async def call_llm(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        if max_tokens is None:
            max_tokens = settings.LM_STUDIO_MAX_TOKENS_RESPONSE

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        for attempt in range(3):
            try:
                client = await self._get_client()
                logger.debug(f"Sending request to LM Studio (attempt {attempt + 1})")
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.TimeoutException as e:
                if attempt == 2:
                    raise LLMTimeoutError(
                        f"LM Studio request timed out after {self.timeout} seconds"
                    ) from e
                await asyncio.sleep(2 ** (attempt + 1))
            except httpx.HTTPStatusError as e:
                logger.error(f"LM Studio returned error: {e.response.status_code} - {e.response.text}")
                raise LLMServiceError(f"LM Studio returned error: {e.response.status_code}") from e
            except httpx.ConnectError as e:
                if attempt == 2:
                    raise LLMConnectionError(
                        "Cannot connect to LM Studio. Ensure it is running and accessible."
                    ) from e
                await asyncio.sleep(2 ** (attempt + 1))
            except (KeyError, IndexError) as e:
                raise LLMServiceError(f"Unexpected response format from LM Studio: {e}") from e
            except Exception as e:
                if attempt == 2:
                    raise LLMServiceError(f"Unexpected error calling LM Studio: {e}") from e
                await asyncio.sleep(2 ** (attempt + 1))

        raise LLMServiceError("Failed to complete request after 3 attempts")

    async def call_llm_json(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant. Respond with valid JSON only.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict:
        response = await self.call_llm(prompt, system_prompt, temperature, max_tokens)

        import json

        response_clean = response.strip()
        if response_clean.startswith("```json"):
            response_clean = response_clean[7:]
        if response_clean.startswith("```"):
            response_clean = response_clean[3:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        response_clean = response_clean.strip()

        try:
            return json.loads(response_clean)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_clean}")
            raise LLMServiceError(f"LLM returned invalid JSON: {e}") from e

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4

    def truncate_for_context(self, text: str, max_tokens: int = 100000) -> str:
        estimated = self.estimate_tokens(text)
        if estimated <= max_tokens:
            return text
        max_chars = max_tokens * 4
        return text[:max_chars] + "... [truncated]"


llm_service = LLMService()
