from discord.ext import commands
from dependency_injector.wiring import inject, Provide
from containers import Container
from utils.logging import BotLogger
from utils.decorators import with_logger


@with_logger
class Bot(commands.Bot):
    @inject
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info("Discord bot initialized")

    async def setup_hook(self):
        """Setup hook runs before the bot starts"""
        self.logger.info("Running bot setup hook")
        # Load your cogs here
        pass

    async def on_ready(self):
        self.logger.info(f"Bot is ready! Logged in as {self.user.name}")
