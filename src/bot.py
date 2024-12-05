import discord
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger
from src.llm.events import setup_llm_events
from src.database.manager import DatabaseManager
from src.module_manager import ModuleManager
from src.utils.permissions import permission_manager
from src.utils.command_sync import CommandSyncer


class Bot(commands.Bot):
    def __init__(self):
        # Get configuration
        self.config = Config()

        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration")

        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.dm_messages = True
        intents.dm_reactions = True
        intents.dm_typing = True
        intents.guild_messages = True

        # Initialize bot with command prefix and intents
        super().__init__(
            command_prefix=self.config.discord.command_prefix,
            intents=intents,
            owner_id=self.config.discord.owner_id,
        )

        # Set up activity if configured
        if self.config.discord.activity:
            self.activity = discord.Game(name=self.config.discord.activity)

        # Initialize managers
        self.db = DatabaseManager()
        self.module_manager = ModuleManager(self)
        self.permission_manager = permission_manager
        self.command_syncer = CommandSyncer(self)

    async def setup_hook(self):
        """Initialize bot components before starting"""
        try:
            # Initialize database
            await self.db.create_tables()
            logger.info("Database tables created successfully")

            # Set up LLM event handlers
            await setup_llm_events(self)
            logger.info("LLM events setup complete")

            # Load all cog modules
            loaded_modules = await self.module_manager.load_all_modules()
            logger.info(
                f"Loaded {len(loaded_modules)} modules: {', '.join(loaded_modules)}"
            )

            # Initial command sync will happen in on_ready
            logger.info("Command sync scheduled for when bot is ready")

        except Exception as e:
            logger.error(f"Error during bot setup: {str(e)}")
            raise

    async def on_ready(self):
        """Log when the bot is ready and connected"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")

        # Sync commands after bot is fully ready
        try:
            await self.command_syncer.sync_all_guilds()
            logger.info("Command sync completed")
        except Exception as e:
            logger.error(f"Failed to sync commands: {str(e)}")

        logger.info("------")


async def create_bot():
    """
    Create and configure the Discord bot instance

    Returns:
        Bot: Configured Discord bot
    """
    try:
        bot = Bot()
        return bot
    except Exception as e:
        logger.error(f"Failed to create bot: {str(e)}")
        raise
