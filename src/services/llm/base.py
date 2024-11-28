from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import asyncio
import time
from weakref import WeakValueDictionary


@dataclass
class LLMConfig:
    """Configuration for an LLM instance"""

    provider: str
    model: str
    api_key: str
    name: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.last_used = time.time()

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the LLM"""
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream text from the LLM"""
        pass


class LLMManager:
    """Manages multiple LLM instances"""

    def __init__(self, cleanup_interval: int = 3600):
        # Use WeakValueDictionary for automatic cleanup of unused instances
        self._instances: WeakValueDictionary[str, LLMProvider] = WeakValueDictionary()
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None

    async def setup(self) -> None:
        """Initialize the LLM manager."""
        # Get configuration from container
        from src.containers import config

        # Register default providers
        try:
            # Register xAI provider
            self.register(
                LLMConfig(
                    provider="xai",
                    model="gpt-4",
                    api_key=config.XAI__API_KEY,
                    name="xai",
                )
            )

            # Start cleanup task
            await self.start()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM services: {str(e)}")

    async def start(self):
        """Start the cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop the cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self):
        """Periodically clean up old instances"""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            current_time = time.time()
            # Update last_used time for instances still in use
            for instance in self._instances.values():
                if hasattr(instance, "last_used"):
                    if current_time - instance.last_used > self._cleanup_interval:
                        # Let the WeakValueDictionary handle cleanup
                        pass

    def register(self, config: LLMConfig) -> LLMProvider:
        """Register a new LLM instance"""
        from .providers import PROVIDER_MAP

        if config.name is None:
            config.name = f"{config.provider}-{config.model}"

        if config.name in self._instances:
            raise ValueError(f"LLM instance with name {config.name} already exists")

        provider_class = PROVIDER_MAP.get(config.provider)
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.provider}")

        instance = provider_class(config)
        self._instances[config.name] = instance
        return instance

    def get(self, name: str) -> Optional[LLMProvider]:
        """Get an LLM instance by name"""
        instance = self._instances.get(name)
        if instance:
            instance.last_used = time.time()
        return instance

    def list_instances(self) -> Dict[str, str]:
        """List all registered instances and their providers"""
        return {
            name: instance.config.provider for name, instance in self._instances.items()
        }
