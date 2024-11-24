from groq import Groq
from typing import Dict, List, Optional, Any, Union
from ..base import BaseLLMProvider, EmbeddingType


class GroqProvider(BaseLLMProvider):
    """Groq API provider implementation"""

    DEFAULT_CHAT_MODEL = "llama3-70b-8192"  # Using a default stable model

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = Groq(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.DEFAULT_CHAT_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model or self.DEFAULT_CHAT_MODEL,
            temperature=temperature,
            **kwargs,
        )
        return response.choices[0].message.content

    async def embed(
        self,
        inputs: Union[List[str], List[str]],
        input_type: EmbeddingType = EmbeddingType.TEXT,
        model: Optional[str] = None,
        **kwargs,
    ) -> List[List[float]]:
        raise NotImplementedError("Groq does not currently support embeddings")
