import logging
import discord
from discord.ext import commands
from src.containers import Container

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    """Custom Discord bot implementation."""

    def __init__(self, container: Container):
        """Initialize the bot with container dependencies."""
        self.container = container

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=container.config().discord.command_prefix, intents=intents
        )

    async def setup_hook(self) -> None:
        """Initialize bot resources after Discord connection is established."""
        logger.info("Setting up bot...")
        # Add any additional setup here (like loading cogs)

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
