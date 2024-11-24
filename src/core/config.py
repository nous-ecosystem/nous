from typing import Any
from pathlib import Path
import os
from dotenv import load_dotenv


class _ConfigSection:
    """Helper class to create nested config sections"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                setattr(self, key, _ConfigSection(**value))
            else:
                setattr(self, key, value)


class Config:
    """Singleton configuration class that loads from .env file"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Load .env file
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)

        # Discord settings
        self.discord = _ConfigSection(
            token=os.getenv("DISCORD_TOKEN"),
            secret=os.getenv("DISCORD_SECRET"),
            owner_id=int(os.getenv("DISCORD_OWNER_ID")),
            command_prefix=os.getenv("DISCORD_COMMAND_PREFIX", "!"),
        )

        # LLM Provider settings
        self.openai = _ConfigSection(
            api_key=os.getenv("OPENAI__API_KEY"),
            audio_model=os.getenv("OPENAI__AUDIO_MODEL"),
        )

        self.groq = _ConfigSection(
            api_key=os.getenv("GROQ__API_KEY"),
            audio_model=os.getenv("GROQ__AUDIO_MODEL"),
        )

        self.cohere = _ConfigSection(api_key=os.getenv("COHERE__API_KEY"))

        # Redis settings
        self.redis = _ConfigSection(
            host=os.getenv("REDIS__HOST", "localhost"),
            port=int(os.getenv("REDIS__PORT", 6379)),
            password=os.getenv("REDIS__PASSWORD", ""),
            conversation_ttl=int(os.getenv("REDIS__CONVERSATION_TTL", 5400)),
        )

        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        try:
            current = self
            for part in key.split("."):
                current = getattr(current, part)
            return current
        except AttributeError:
            return default
