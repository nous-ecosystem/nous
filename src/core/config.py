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

        # Validate and load Discord settings
        discord_token = self._require_env("DISCORD_TOKEN", "Discord token")
        discord_owner_id = self._require_env("DISCORD_OWNER_ID", "Discord owner ID")

        self.discord = _ConfigSection(
            token=discord_token,
            secret=os.getenv("DISCORD_SECRET"),  # Optional
            owner_id=self._validate_int(discord_owner_id, "Discord owner ID"),
            command_prefix=os.getenv("DISCORD_COMMAND_PREFIX", "!"),
        )

        # Validate and load LLM Provider settings
        self.openai = _ConfigSection(
            api_key=self._require_env("OPENAI__API_KEY", "OpenAI API key"),
            audio_model=os.getenv("OPENAI__AUDIO_MODEL"),
        )

        self.groq = _ConfigSection(
            api_key=self._require_env("GROQ__API_KEY", "Groq API key"),
            audio_model=os.getenv("GROQ__AUDIO_MODEL"),
        )

        self.cohere = _ConfigSection(
            api_key=self._require_env("COHERE__API_KEY", "Cohere API key")
        )

        # Validate and load Redis settings
        self.redis = _ConfigSection(
            host=os.getenv("REDIS__HOST", "localhost"),
            port=self._validate_int(os.getenv("REDIS__PORT", "6379"), "Redis port"),
            password=os.getenv("REDIS__PASSWORD", ""),
            conversation_ttl=self._validate_int(
                os.getenv("REDIS__CONVERSATION_TTL", "5400"), "Redis conversation TTL"
            ),
        )

        self.logging = _ConfigSection(
            level=os.getenv("LOG_LEVEL", "INFO"), directory=os.getenv("LOG_DIR", "logs")
        )

        self.database = _ConfigSection(
            sqlite_path=os.getenv("DATABASE_PATH", "data/db/bot.db"),
        )

        self._initialized = True

    def _require_env(self, key: str, description: str) -> str:
        """Require and validate an environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Missing required environment variable: {key} ({description})"
            )
        return value

    def _validate_int(self, value: str, description: str) -> int:
        """Validate and convert a string to integer"""
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid integer value for {description}: {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        try:
            current = self
            for part in key.split("."):
                current = getattr(current, part)
            return current
        except AttributeError:
            return default
