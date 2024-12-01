from src.injection import Container, configure_container
from src.core.bot import DiscordBot


async def initialize_bot() -> DiscordBot:
    """
    Initialize the bot and load modules.
    """
    container = Container()
    configure_container(container)

    # Initialize database first
    database = container.database()
    await database.initialize()

    bot = container.discord_bot()
    module_manager = container.module_manager()

    module_manager.load_modules()
    return bot
