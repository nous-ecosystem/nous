from typing import AsyncGenerator
import json
import aiohttp
from ..base import LLMProvider, LLMConfig


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.options = config.options or {}
        self.base_url = "https://api.openai.com/v1"
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        return self.session

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI API"""
        session = await self._ensure_session()
        options = {**self.options, **kwargs}

        async with session.post(
            "/chat/completions",
            json={
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                **options,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream text using OpenAI API"""
        session = await self._ensure_session()
        options = {**self.options, **kwargs, "stream": True}

        async with session.post(
            "/chat/completions",
            json={
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                **options,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as response:
            response.raise_for_status()
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = line[6:]  # Remove "data: " prefix
                    if data:
                        content = json.loads(data)["choices"][0]["delta"].get("content")
                        if content:
                            yield content

    async def __del__(self):
        """Cleanup the session"""
        if self.session and not self.session.closed:
            await self.session.close()
