# src/config.py

from dataclasses import dataclass, field
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    url: str = "sqlite+aiosqlite:///./data/database.sqlite"
    echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # Optional pooling settings (only used for PostgreSQL/MySQL)
    @property
    def pooling_settings(self) -> dict:
        if not self.url.startswith("sqlite"):
            return {
                "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "5")),
                "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
                "pool_timeout": int(os.getenv("DATABASE_POOL_TIMEOUT", "30")),
            }
        return {}


@dataclass
class RedisConfig:
    enabled: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    db: int = int(os.getenv("REDIS_DB", "0"))
    ttl: int = int(os.getenv("REDIS_TTL", "3600"))


@dataclass
class DiscordConfig:
    token: str = os.getenv("DISCORD_TOKEN", "")
    owner_id: int = int(os.getenv("DISCORD_OWNER_ID", "0"))
    command_prefix: str = os.getenv("DISCORD_COMMAND_PREFIX", "!")
    guild_ids: list[int] = field(
        default_factory=lambda: [
            int(id) for id in os.getenv("DISCORD_GUILD_IDS", "").split(",") if id
        ]
    )
    status: str = os.getenv("DISCORD_STATUS", "online")
    activity: str = os.getenv("DISCORD_ACTIVITY", "")


@dataclass
class LoggingConfig:
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    directory: str = os.getenv("LOG_DIR", "logs")
    file_name: str = os.getenv("LOG_FILE", "bot.log")


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Force reload environment variables
        load_dotenv(override=True)

        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.discord = DiscordConfig()
        self.logging = LoggingConfig()

        # API Keys
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.fal_api_key = os.getenv("FAL_API_KEY")

        # Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_password = os.getenv("SUPABASE_PASSWORD")
        self.supabase_service_role = os.getenv("SUPABASE_SERVICE_ROLE_SECRET")

    def reload(self):
        """Force reload of all configuration values"""
        self._initialize()
        logger.info("Configuration reloaded")

    def validate(self) -> bool:
        """Validate critical configuration values"""
        if not self.discord.token:
            logger.error("Discord token is not set")
            return False
        if not self.discord.owner_id:
            logger.error("Discord owner ID is not set")
            return False
        return True


# Usage example
if __name__ == "__main__":
    config = Config()
    print("Discord Token:", config.discord.token)
    print("Log Level:", config.logging.level)
