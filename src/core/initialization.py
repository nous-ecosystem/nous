from src.injection import Application
from src.core.bot import DiscordBot


async def initialize_bot() -> DiscordBot:
    """
    Initialize the bot and load modules.
    """
    app = Application.create()

    # Initialize database
    database = app.services.database()
    await database.initialize()

    # Get bot instance
    bot = app.bot.discord_bot()

    # Initialize chat handler
    chat_handler = app.bot.chat_handler()
    bot.logger.info(f"Chat handler initialized: {chat_handler}")

    # Initialize and load modules
    module_manager = app.bot.module_manager()
    module_manager.load_modules()

    return bot
