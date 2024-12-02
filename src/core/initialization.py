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

    # Initialize chat handler (this will wire up the event listeners)
    chat_handler = container.chat_handler()
    bot.logger.info(f"Chat handler initialized: {chat_handler}")

    # Load modules
    module_manager.load_modules()

    return bot
