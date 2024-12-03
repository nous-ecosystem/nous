import asyncio
import discord
from discord.ext import commands
from src.bot.config import config
from src.database import initialize_database
from src.database.repositories.user_repository import UserRepository
from src.llm.providers.groq import GroqFactory
from src.llm.providers.openai import OpenAIFactory
from src.utils.logger import logger


class DiscordAIBot(commands.Bot):
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        # Initialize bot with command prefix and intents
        super().__init__(
            command_prefix=config.DISCORD_COMMAND_PREFIX or "!", intents=intents
        )

        # Initialize LLM providers
        self.groq_client = GroqFactory(api_key=config.GROQ_API_KEY)
        self.openai_client = OpenAIFactory(api_key=config.OPENAI_API_KEY)

    async def setup_hook(self):
        """
        Async setup method called when the bot starts
        Handles database initialization and extension loading
        """
        # Initialize database
        try:
            await self.init_database()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

        # Load extensions (cogs)
        await self.load_extensions()

    async def init_database(self):
        """Initialize database models"""
        from src.database import init_models

        await init_models()
        logger.info("Database initialized successfully")

    async def load_extensions(self):
        """
        Load bot extensions (cogs)
        You can expand this to dynamically load cogs from a directory
        """
        # Example of loading a cog
        # await self.load_extension('src.bot.cogs.some_cog')
        logger.info("Bot extensions loaded")

    async def on_ready(self):
        """
        Event triggered when the bot is ready and connected
        """
        logger.info(f"Logged in as {self.user.name}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info("------")

    async def on_message(self, message):
        """
        Custom message handler
        Tracks user activity and processes commands
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # Track user activity
        try:
            await UserRepository.increment_message_count(str(message.author.id))
        except Exception as e:
            logger.error(f"Error tracking user message: {e}")

        # Process commands
        await self.process_commands(message)


def create_bot():
    """
    Factory method to create and configure the bot
    """
    # Validate configuration before bot creation
    config.validate_config()

    # Create bot instance
    bot = DiscordAIBot()
    return bot
