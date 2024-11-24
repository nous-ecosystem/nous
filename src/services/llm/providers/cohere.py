import cohere
from typing import Dict, List, Optional, Any, Union
from ..base import BaseLLMProvider, EmbeddingType


class CohereProvider(BaseLLMProvider):
    """Cohere API provider implementation"""

    DEFAULT_CHAT_MODEL = "command-r-plus-08-2024"
    DEFAULT_EMBED_MODEL = "embed-english-v3.0"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = cohere.AsyncClientV2(api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        response = await self.client.generate(
            prompt=prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
        )
        return response.generations[0].text

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        # Convert messages to Cohere format
        cohere_messages = [
            cohere.ChatMessage(role=msg["role"], content=msg["content"])
            for msg in messages
        ]

        response = await self.client.chat(
            messages=cohere_messages,
            model=model or self.DEFAULT_CHAT_MODEL,
            temperature=temperature,
            documents=documents,
            **kwargs,
        )
        return response.text

    async def embed(
        self,
        inputs: Union[List[str], List[str]],
        input_type: EmbeddingType = EmbeddingType.TEXT,
        model: Optional[str] = None,
        **kwargs,
    ) -> List[List[float]]:
        response = await self.client.embed(
            texts=inputs if input_type == EmbeddingType.TEXT else None,
            images=inputs if input_type == EmbeddingType.IMAGE else None,
            model=model or self.DEFAULT_EMBED_MODEL,
            input_type=input_type.value,
            **kwargs,
        )
        return response.embeddings
