from typing import Dict, Optional, Type
from dependency_injector.wiring import inject, Provide
from containers import Container
from utils.logging import BotLogger
from utils.decorators import with_logger
from .base import BaseLLMProvider
from .providers.cohere import CohereProvider
from .providers.groq import GroqProvider
from .providers.openai import OpenAIProvider


@with_logger
class LLMManager:
    """Manages different LLM providers"""

    PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
        "cohere": CohereProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }

    @inject
    def __init__(
        self, name: str = "default", logger: BotLogger = Provide[Container.logger]
    ):
        self.name = name
        self._active_providers: Dict[str, BaseLLMProvider] = {}
        self.logger = logger
        self.logger.info(f"Initialized LLM Manager: {name}")

    def register_provider(self, name: str, provider: BaseLLMProvider) -> None:
        """Register a provider instance"""
        self._active_providers[name] = provider
        self.logger.info(f"Registered LLM provider: {name}")

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a registered provider instance"""
        provider = self._active_providers.get(name)
        if provider is None:
            self.logger.warning(f"Attempted to access unregistered provider: {name}")
        return provider
