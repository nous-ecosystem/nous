from discord.ext import commands
import discord
from src.core.config import config
from src.utils.logging import get_logger


class DiscordBot(commands.Bot):
    """
    Custom Discord bot class with enhanced logging and configuration.
    """

    def __init__(self, token: str, logger=None):
        """
        Initialize the Discord bot with custom intents and configuration.

        Args:
            token: Discord bot token
            logger: Optional logger instance
        """
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        # Call parent constructor
        super().__init__(
            command_prefix=config.DISCORD_COMMAND_PREFIX,
            intents=intents,
            owner_id=int(config.DISCORD_OWNER_ID),
        )

        self.token = token
        self.logger = logger or get_logger()

    async def on_ready(self):
        """
        Logging and setup when bot is ready and connected.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"Bot ID: {self.user.id}")
        self.logger.info("------")

    async def on_command_error(self, ctx, error):
        """
        Global error handler for commands.

        Args:
            ctx: Command context
            error: Error that occurred
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Try using the help command.")
        else:
            self.logger.error(f"An error occurred: {error}")
            await ctx.send("An unexpected error occurred.")
