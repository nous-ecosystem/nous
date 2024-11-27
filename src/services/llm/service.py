from dependency_injector import containers, providers
from .base import LLMManager


class LLMContainer(containers.DeclarativeContainer):
    """Dependency Injection container for LLM service."""

    # Configuration
    config = providers.Dependency()

    # LLM Manager instance
    llm_manager = providers.Singleton(
        LLMManager,
        cleanup_interval=3600,  # 1 hour cleanup interval
    )
