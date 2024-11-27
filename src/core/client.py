import logging
from typing import Optional
from pathlib import Path

import discord
from discord.ext import commands
from dependency_injector.wiring import inject, Provide

from .config import ConfigContainer, DiscordConfig, LogConfig


class NousBot(commands.Bot):
    """
    Custom Discord bot client with enhanced functionality and configuration integration.
    Implements dependency injection for configuration management.
    """

    @inject
    def __init__(
        self,
        discord_config: DiscordConfig = Provide[ConfigContainer.discord_config],
        log_config: LogConfig = Provide[ConfigContainer.logging_config],
        *args,
        **kwargs,
    ):
        """
        Initialize the bot with configuration dependencies.

        Args:
            discord_config: Injected Discord configuration
            log_config: Injected logging configuration
            *args: Additional positional arguments for the parent class
            **kwargs: Additional keyword arguments for the parent class
        """
        # Setup basic bot configuration
        super().__init__(
            command_prefix=discord_config.command_prefix,
            intents=discord.Intents.all(),
            *args,
            **kwargs,
        )

        # Store configuration
        self.discord_config = discord_config
        self.owner_id = discord_config.owner_id

        # Setup logging
        self._setup_logging(log_config)

    def _setup_logging(self, log_config: LogConfig) -> None:
        """
        Configure logging for the bot.

        Args:
            log_config: Logging configuration settings
        """
        log_path = log_config.directory / "bot.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_config.level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("nous_bot")

    async def setup_hook(self) -> None:
        """
        Async setup hook that runs before the bot starts.
        Load extensions and perform any necessary async initialization here.
        """
        # TODO: Add extension loading logic here
        self.logger.info("Bot setup completed successfully")

    async def on_ready(self):
        """Event handler for when the bot has successfully connected to Discord."""
        self.logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")

    async def on_error(self, event_method: str, *args, **kwargs):
        """
        Global error handler for all events.

        Args:
            event_method: The name of the event that raised the error
            *args: Positional arguments that were passed to the event
            **kwargs: Keyword arguments that were passed to the event
        """
        self.logger.error(f"Error in {event_method}", exc_info=True)
