from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class EmbeddingType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.extra_config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Generate text based on prompt"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        """Chat completion endpoint"""
        pass

    @abstractmethod
    async def embed(
        self,
        inputs: Union[List[str], List[str]],
        input_type: EmbeddingType = EmbeddingType.TEXT,
        model: Optional[str] = None,
        **kwargs,
    ) -> List[List[float]]:
        """Generate embeddings for provided texts or images"""
        pass
