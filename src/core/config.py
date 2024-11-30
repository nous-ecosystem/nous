from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import SecretStr, HttpUrl


class Settings(BaseSettings):
    # Discord Configuration
    discord_token: SecretStr
    discord_secret: SecretStr
    discord_owner_id: int
    discord_command_prefix: str

    # AI Provider Configurations
    xai_api_key: SecretStr
    openai_api_key: SecretStr
    groq_api_key: SecretStr
    cohere_api_key: SecretStr
    fal_api_key: SecretStr

    # Redis Configuration
    redis_host: str
    redis_port: int
    redis_password: SecretStr
    redis_conversation_ttl: int

    # Logging Configuration
    log_level: str
    log_dir: str

    # Supabase Configuration
    supabase_password: SecretStr
    supabase_service_role_secret: SecretStr
    supabase_url: HttpUrl
    supabase_key: SecretStr

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings class.
    Using lru_cache ensures we only create one instance.
    """
    return Settings()


# Usage:
# from config import get_settings
# settings = get_settings()
# token = settings.discord_token.get_secret_value()
