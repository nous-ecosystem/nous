import os
from dotenv import load_dotenv
from src.utils.logging import get_logger

# Load environment variables
load_dotenv()


class Config:
    # Initialize logger
    _logger = get_logger()

    # Discord Configuration
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_SECRET = os.getenv("DISCORD_SECRET")
    DISCORD_OWNER_ID = os.getenv("DISCORD_OWNER_ID")
    DISCORD_COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "n!")

    # AI Provider Keys
    XAI_API_KEY = os.getenv("XAI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    FAL_API_KEY = os.getenv("FAL_API_KEY")

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_CONVERSATION_TTL = int(os.getenv("REDIS_CONVERSATION_TTL", 5400))

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_SECRET = os.getenv("SUPABASE_SERVICE_ROLE_SECRET")
    SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")

    def __init__(self):
        # Log configuration loading
        self._logger.info("Configuration loaded successfully")

        # Validate critical configurations
        self._validate_critical_configs()

    def _validate_critical_configs(self):
        """
        Validate critical configuration settings.
        Log warnings for missing critical configurations.
        """
        critical_configs = [
            ("DISCORD_TOKEN", self.DISCORD_TOKEN),
            ("DISCORD_SECRET", self.DISCORD_SECRET),
            ("DISCORD_OWNER_ID", self.DISCORD_OWNER_ID),
        ]

        for config_name, config_value in critical_configs:
            if not config_value:
                self._logger.warning(f"Missing critical configuration: {config_name}")


# Create a single instance
config = Config()
