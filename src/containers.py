from dependency_injector import containers, providers
from src.core.config import ConfigContainer
from src.utils.logging import LoggerContainer
from src.core.client import NousBot
from src.core.mod_manager import ModuleManagerContainer
from src.services.llm.service import LLMContainer
from src.services.database.service import DatabaseContainer


class Container(containers.DeclarativeContainer):
    """Main dependency injection container for the Discord bot."""

    # Core containers
    config = providers.Container(ConfigContainer)

    # Logger container with config override
    logger = providers.Container(LoggerContainer)
    logger.config.override(config)
    logger.logger.override(
        providers.Singleton(
            LoggerContainer.logger.cls, log_config=config.logging_config
        )
    )

    # LLM container
    llm = providers.Container(LLMContainer)
    llm.config.override(config)

    # Database container
    database = providers.Container(DatabaseContainer)
    database.config.override(config)

    # Bot provider
    bot = providers.Singleton(
        NousBot, discord_config=config.discord_config, log_config=config.logging_config
    )

    # Module manager container with bot and logger dependencies
    module_manager = providers.Container(ModuleManagerContainer)
    module_manager.bot.override(bot)
    module_manager.logger.override(logger.logger)

    # Wire dependencies
    wiring_config = containers.WiringConfiguration(
        packages=[
            "src.core",
            "src.utils",
            "src.services",
            "src.modules",
        ]
    )


# Create the main container instance
container = Container()

# Create instances that can be imported directly
config = container.config.config()
logger = container.logger.logger()
module_manager = container.module_manager.module_manager()
llm_manager = container.llm.llm_manager()
db_manager = container.database.db_manager()
