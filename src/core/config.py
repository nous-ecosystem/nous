from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dependency_injector import containers, providers


class DiscordConfig(BaseModel):
    """Discord-specific configuration settings."""

    token: str = Field(..., alias="DISCORD_TOKEN")
    secret: str = Field(..., alias="DISCORD_SECRET")
    owner_id: int = Field(..., alias="DISCORD_OWNER_ID")
    command_prefix: str = Field(..., alias="DISCORD_COMMAND_PREFIX")


class AIProviderConfig(BaseModel):
    """AI provider API configurations."""

    xai: str = Field(..., alias="XAI__API_KEY")
    openai: str = Field(..., alias="OPENAI__API_KEY")
    groq: str = Field(..., alias="GROQ__API_KEY")
    cohere: str = Field(..., alias="COHERE__API_KEY")
    fal: str = Field(..., alias="FAL__API_KEY")


class RedisConfig(BaseModel):
    """Redis connection configuration."""

    host: str = Field(..., alias="REDIS__HOST")
    port: int = Field(..., alias="REDIS__PORT")
    password: Optional[str] = Field(None, alias="REDIS__PASSWORD")
    conversation_ttl: int = Field(..., alias="REDIS__CONVERSATION_TTL")


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    host: str = Field(..., alias="DB_HOST")
    port: int = Field(..., alias="DB_PORT")
    name: str = Field(..., alias="DB_NAME")
    user: str = Field(..., alias="DB_USER")
    password: str = Field(..., alias="DB_PASSWORD")


class LogConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(..., alias="LOG_LEVEL")
    directory: Path = Field(..., alias="LOG_DIR")


class BotConfig(BaseSettings):
    """
    Main configuration class that loads and validates all bot settings.
    Uses pydantic for validation and environment variable loading.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Discord Configuration
    DISCORD_TOKEN: str
    DISCORD_SECRET: str
    DISCORD_OWNER_ID: int
    DISCORD_COMMAND_PREFIX: str

    # AI Provider Configuration
    XAI__API_KEY: str
    OPENAI__API_KEY: str
    GROQ__API_KEY: str
    COHERE__API_KEY: str
    FAL__API_KEY: str

    # Redis Configuration
    REDIS__HOST: str
    REDIS__PORT: int
    REDIS__PASSWORD: Optional[str] = None
    REDIS__CONVERSATION_TTL: int

    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Logging Configuration
    LOG_LEVEL: str
    LOG_DIR: Path

    @property
    def discord(self) -> DiscordConfig:
        return DiscordConfig(
            DISCORD_TOKEN=self.DISCORD_TOKEN,
            DISCORD_SECRET=self.DISCORD_SECRET,
            DISCORD_OWNER_ID=self.DISCORD_OWNER_ID,
            DISCORD_COMMAND_PREFIX=self.DISCORD_COMMAND_PREFIX,
        )

    @property
    def ai(self) -> AIProviderConfig:
        return AIProviderConfig(
            XAI__API_KEY=self.XAI__API_KEY,
            OPENAI__API_KEY=self.OPENAI__API_KEY,
            GROQ__API_KEY=self.GROQ__API_KEY,
            COHERE__API_KEY=self.COHERE__API_KEY,
            FAL__API_KEY=self.FAL__API_KEY,
        )

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(
            REDIS__HOST=self.REDIS__HOST,
            REDIS__PORT=self.REDIS__PORT,
            REDIS__PASSWORD=self.REDIS__PASSWORD,
            REDIS__CONVERSATION_TTL=self.REDIS__CONVERSATION_TTL,
        )

    @property
    def database(self) -> DatabaseConfig:
        return DatabaseConfig(
            DB_HOST=self.DB_HOST,
            DB_PORT=self.DB_PORT,
            DB_NAME=self.DB_NAME,
            DB_USER=self.DB_USER,
            DB_PASSWORD=self.DB_PASSWORD,
        )

    @property
    def logging(self) -> LogConfig:
        return LogConfig(
            LOG_LEVEL=self.LOG_LEVEL,
            LOG_DIR=self.LOG_DIR,
        )


class ConfigContainer(containers.DeclarativeContainer):
    """Dependency Injection container for configuration."""

    # Configuration provider
    config = providers.Singleton(BotConfig)

    # Individual config section providers for more granular injection
    discord_config = providers.Singleton(lambda config: config.discord, config)
    ai_config = providers.Singleton(lambda config: config.ai, config)
    redis_config = providers.Singleton(lambda config: config.redis, config)
    database_config = providers.Singleton(lambda config: config.database, config)
    logging_config = providers.Singleton(lambda config: config.logging, config)
