from dependency_injector import containers, providers
from typing import Dict, Any

from src.core.config import config
from src.utils.logging import get_logger
from src.core.bot import DiscordBot
from src.core.module_manager import ModuleManager
from src.database.service import DatabaseService
from src.chat.handler import ChatHandler
from src.chat.groq_client import GroqClient


class Services(containers.DeclarativeContainer):
    """Container for core services"""

    config = providers.Singleton(lambda: config)  # Your existing config instance
    logger = providers.Singleton(get_logger)

    database = providers.Singleton(DatabaseService)

    groq_client = providers.Singleton(GroqClient, api_key=config.provided.GROQ_API_KEY)


class BotComponents(containers.DeclarativeContainer):
    """Container for bot-specific components"""

    services = providers.DependenciesContainer()

    discord_bot = providers.Singleton(
        DiscordBot, token=services.config.provided.DISCORD_TOKEN, logger=services.logger
    )

    module_manager = providers.Singleton(
        ModuleManager, bot=discord_bot, logger=services.logger
    )

    chat_handler = providers.Singleton(
        ChatHandler,
        client=discord_bot,
        groq_api_key=services.config.provided.GROQ_API_KEY,
    )


class Application(containers.DeclarativeContainer):
    """Main application container"""

    services = providers.Container(Services)
    bot = providers.Container(BotComponents, services=services)

    # Helper method to initialize the application
    @classmethod
    def create(cls) -> "Application":
        container = cls()
        container.init_resources()
        return container


def configure_container(container: Application):
    """
    Configure the dependency injection container.
    """
    container.wire(
        modules=[
            "src.core.bot",
            "src.core.module_manager",
            "src.database.service",
            "src.chat.handler",
            "src.injection",
            "main",
        ]
    )
