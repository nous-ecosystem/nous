import discord
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger
from src.llm.events import setup_llm_events
from src.database.manager import DatabaseManager
from src.module_manager import ModuleManager


async def create_bot():
    """
    Create and configure the Discord bot instance

    Returns:
        commands.Bot: Configured Discord bot
    """
    # Get configuration
    config = Config()

    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.dm_reactions = True
    intents.dm_typing = True
    intents.guild_messages = True

    # Create bot with command prefix and intents
    bot = commands.Bot(
        command_prefix=config.DISCORD_COMMAND_PREFIX or "!", intents=intents
    )

    # Initialize database
    db = DatabaseManager()
    await db.create_tables()

    @bot.event
    async def on_ready():
        """Log when the bot is ready and connected"""
        # Set up LLM event handlers
        await setup_llm_events(bot)

        # Load all cog modules
        module_manager = ModuleManager(bot)
        await module_manager.load_all_modules()

        logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
        logger.info("------")

    return bot
