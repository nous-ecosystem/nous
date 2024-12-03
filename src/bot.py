import discord
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger
from src.llm.events import setup_llm_events


def create_bot():
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

    @bot.event
    async def on_ready():
        """Log when the bot is ready and connected"""
        # Set up LLM event handlers
        await setup_llm_events(bot)

        logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
        logger.info("------")

    return bot
