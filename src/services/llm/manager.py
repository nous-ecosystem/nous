from typing import Dict, Optional, Type
from .base import BaseLLMProvider
from .providers.cohere import CohereProvider
from .providers.groq import GroqProvider
from .providers.openai import OpenAIProvider


class LLMManager:
    """Manages different LLM providers"""

    PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
        "cohere": CohereProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }

    def __init__(self, name: str = "default"):
        self.name = name
        self._active_providers: Dict[str, BaseLLMProvider] = {}

    def register_provider(self, name: str, api_key: str, **kwargs) -> None:
        """Register a new provider instance"""
        if name not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {name}")

        provider_class = self.PROVIDERS[name]
        self._active_providers[name] = provider_class(api_key, **kwargs)

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a registered provider instance"""
        return self._active_providers.get(name)
