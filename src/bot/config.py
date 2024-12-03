import os
from dotenv import load_dotenv
import threading


class BotConfig:
    """
    Singleton configuration class for loading and accessing environment variables.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Discord Configuration
        self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
        self.DISCORD_SECRET = os.getenv("DISCORD_SECRET")
        self.DISCORD_OWNER_ID = os.getenv("DISCORD_OWNER_ID")
        self.DISCORD_COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX")

        # AI Provider Configuration
        self.XAI_API_KEY = os.getenv("XAI_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.COHERE_API_KEY = os.getenv("COHERE_API_KEY")
        self.FAL_API_KEY = os.getenv("FAL_API_KEY")

        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # Redis Configuration
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_CONVERSATION_TTL = int(os.getenv("REDIS_CONVERSATION_TTL", 5400))

        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_DIR = os.getenv("LOG_DIR", "logs")

        # Supabase Configuration
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.SUPABASE_SERVICE_ROLE_SECRET = os.getenv("SUPABASE_SERVICE_ROLE_SECRET")

    @classmethod
    def get_instance(cls):
        """
        Thread-safe method to get the singleton instance of BotConfig.

        Returns:
            BotConfig: The singleton instance of the configuration.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def validate_config(self):
        """
        Validate critical configuration parameters.

        Raises:
            ValueError: If any critical configuration is missing.
        """
        critical_configs = ["DISCORD_TOKEN"]

        for config in critical_configs:
            if not getattr(self, config):
                raise ValueError(f"Critical configuration missing: {config}")


# Create a singleton instance
config = BotConfig.get_instance()
