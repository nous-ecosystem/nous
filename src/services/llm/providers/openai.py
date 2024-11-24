from typing import Dict, List, Optional, Any, Union
import aiohttp
from ..base import BaseLLMProvider, EmbeddingType


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation"""

    BASE_URL = "https://api.openai.com/v1"
    DEFAULT_CHAT_MODEL = "gpt-4-turbo-preview"
    DEFAULT_EMBED_MODEL = "text-embedding-3-small"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.session = None

    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    async def _make_request(self, endpoint: str, payload: dict) -> dict:
        await self._ensure_session()
        async with self.session.post(
            f"{self.BASE_URL}/{endpoint}", json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenAI API error: {error_text}")
            return await response.json()

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        messages = [{"role": "user", "content": prompt}]
        payload = {"model": self.DEFAULT_CHAT_MODEL, "messages": messages, **kwargs}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature

        response = await self._make_request("chat/completions", payload)
        return response["choices"][0]["message"]["content"]

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        payload = {
            "model": model or self.DEFAULT_CHAT_MODEL,
            "messages": messages,
            **kwargs,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        response = await self._make_request("chat/completions", payload)
        return response["choices"][0]["message"]["content"]

    async def embed(
        self,
        inputs: Union[List[str], List[str]],
        input_type: EmbeddingType = EmbeddingType.TEXT,
        model: Optional[str] = None,
        **kwargs,
    ) -> List[List[float]]:
        if input_type == EmbeddingType.IMAGE:
            raise ValueError("OpenAI does not support image embeddings")

        payload = {
            "model": model or self.DEFAULT_EMBED_MODEL,
            "input": inputs,
            **kwargs,
        }

        response = await self._make_request("embeddings", payload)
        return [item["embedding"] for item in response["data"]]

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None
