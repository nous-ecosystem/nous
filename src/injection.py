from dependency_injector import containers, providers

from src.core.config import config
from src.utils.logging import get_logger
from src.core.bot import DiscordBot
from src.core.module_manager import ModuleManager


class Container(containers.DeclarativeContainer):
    """
    Centralized dependency injection container for the Discord bot.
    """

    # Configuration provider (singleton)
    config = providers.Singleton(lambda: config)

    # Logging provider
    logger = providers.Singleton(get_logger)

    # Discord Bot provider
    discord_bot = providers.Singleton(
        DiscordBot, token=lambda: config.DISCORD_TOKEN, logger=logger
    )

    # Module Manager provider
    module_manager = providers.Singleton(ModuleManager, bot=discord_bot, logger=logger)


def configure_container(container: Container):
    """
    Configure the dependency injection container.
    """
    container.wire(
        modules=[
            "src.core.bot",
            "src.core.module_manager",
            "src.injection",
            "main",
        ]
    )
