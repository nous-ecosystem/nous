from typing import Dict, Optional
from .manager import LLMManager


class LLMFactory:
    _instance = None
    _managers: Dict[str, LLMManager] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
        return cls._instance

    @classmethod
    def create_manager(cls, name: str = "default") -> LLMManager:
        """Create a new named LLM manager instance"""
        if name in cls._managers:
            raise ValueError(f"Manager with name '{name}' already exists")

        manager = LLMManager()
        cls._managers[name] = manager
        return manager

    @classmethod
    def get_manager(cls, name: str = "default") -> Optional[LLMManager]:
        """Get an existing named LLM manager instance"""
        return cls._managers.get(name)

    @classmethod
    def get_or_create_manager(cls, name: str = "default") -> LLMManager:
        """Get existing manager or create new one if it doesn't exist"""
        manager = cls.get_manager(name)
        if manager is None:
            manager = cls.create_manager(name)
        return manager

    @classmethod
    def remove_manager(cls, name: str) -> None:
        """Remove a named manager instance"""
        if name in cls._managers:
            del cls._managers[name]
