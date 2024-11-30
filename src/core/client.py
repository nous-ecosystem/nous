import asyncio
import os
from typing import Optional, List

import discord
from discord.ext import commands

from src.injection import container
from src.core.config import get_settings
from src.utils.logging import SingletonLogger
from src.database import SupabaseDatabase


class DiscordBotClient(commands.Bot):
    """
    Custom Discord bot client with advanced features and dependency injection.
    """

    def __init__(
        self,
        intents: discord.Intents,
        database: Optional[SupabaseDatabase] = None,
        logger=None,
    ):
        """
        Initialize the Discord bot with custom configurations.

        :param intents: Discord intents for bot functionality
        :param database: Optional Supabase database instance
        :param logger: Optional logger instance
        """
        settings = get_settings()

        # Configure bot with command prefix and intents
        super().__init__(
            command_prefix=settings.discord_command_prefix,
            intents=intents,
            owner_id=settings.discord_owner_id,
        )

        # Dependency injection
        self.settings = settings
        self.database = database or container.database()
        self.logger = logger or SingletonLogger().get_logger()

        # Bot state tracking
        self.is_ready = False

    async def setup_hook(self):
        """
        Asynchronous setup method for bot initialization.
        Runs before the bot starts connecting to Discord.
        """
        self.logger.info("Setting up bot hooks...")

        # Load extensions (cogs)
        await self.load_extensions()

        # Optional: Sync application commands (slash commands)
        await self.tree.sync()

    async def load_extensions(self, extension_dir: str = "src/modules"):
        """
        Dynamically load bot extensions (cogs) from a directory.

        :param extension_dir: Directory containing bot extensions
        """
        for filename in os.listdir(extension_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await self.load_extension(f"src.modules.{filename[:-3]}")
                    self.logger.info(f"Loaded extension: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to load extension {filename}: {e}")

    async def on_ready(self):
        """
        Event triggered when the bot successfully connects to Discord.
        """
        if not self.is_ready:
            self.is_ready = True
            self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
            self.logger.info("Bot is ready and connected to Discord!")

    async def on_command_error(self, ctx, error):
        """
        Global error handler for bot commands.

        :param ctx: Command context
        :param error: Error that occurred
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, I couldn't find that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Missing required arguments. Please check the command usage."
            )
        else:
            self.logger.error(f"Unhandled error: {error}")
            await ctx.send("An unexpected error occurred.")

    def run(self):
        """
        Start the bot with the Discord token from settings.
        """
        try:
            super().run(self.settings.discord_token.get_secret_value())
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise


def create_bot_client() -> DiscordBotClient:
    """
    Create and configure a Discord bot client with recommended intents.

    :return: Configured DiscordBotClient instance
    """
    # Configure intents with recommended settings
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    return DiscordBotClient(intents=intents)
