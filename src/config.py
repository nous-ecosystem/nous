# src/config.py

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


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

        # Add detailed logging for owner ID
        raw_owner_id = os.getenv("DISCORD_OWNER_ID")
        logger.info(
            f"Raw DISCORD_OWNER_ID from env: {raw_owner_id!r}"
        )  # Use !r for exact representation

        try:
            if not raw_owner_id:
                logger.error("DISCORD_OWNER_ID is not set in environment variables")
                self.DISCORD_OWNER_ID = None
            else:
                self.DISCORD_OWNER_ID = int(raw_owner_id)
                logger.info(
                    f"Successfully parsed DISCORD_OWNER_ID: {self.DISCORD_OWNER_ID}"
                )
        except ValueError as e:
            logger.error(f"Failed to parse DISCORD_OWNER_ID '{raw_owner_id}': {e}")
            self.DISCORD_OWNER_ID = None

        self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
        self.DISCORD_SECRET = os.getenv("DISCORD_SECRET")
        self.DISCORD_COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX")

        self.XAI_API_KEY = os.getenv("XAI_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.COHERE_API_KEY = os.getenv("COHERE_API_KEY")
        self.FAL_API_KEY = os.getenv("FAL_API_KEY")

        self.DATABASE_URL = os.getenv("DATABASE_URL")

        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_CONVERSATION_TTL = os.getenv("REDIS_CONVERSATION_TTL")

        self.LOG_LEVEL = os.getenv("LOG_LEVEL")
        self.LOG_DIR = os.getenv("LOG_DIR")

        self.SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
        self.SUPABASE_SERVICE_ROLE_SECRET = os.getenv("SUPABASE_SERVICE_ROLE_SECRET")
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    def reload(self):
        """Force reload of all configuration values"""
        self._initialize()
        logger.info("Configuration reloaded")


# Usage example
if __name__ == "__main__":
    config = Config()
    print("Discord Token:", config.DISCORD_TOKEN)
    print("Log Level:", config.LOG_LEVEL)
