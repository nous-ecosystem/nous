import discord
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger
from src.llm.events import setup_llm_events
from src.database.manager import DatabaseManager
from src.utils.feature_manager import FeatureManager
from src.utils.permissions import PermissionManager
from src.utils.command_sync import CommandSyncer


async def create_bot() -> commands.Bot:
    """Create and configure the bot instance"""
    config = Config()

    # Set up logging first
    logger.info("Initializing bot...")

    # Validate critical configuration
    if not config.validate():
        logger.error("Invalid configuration")
        raise ValueError("Invalid configuration")

    # Just verify database connection
    db = DatabaseManager()
    await db.verify_database_exists()

    # Create bot instance with specified command prefix
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(
        command_prefix=config.discord.command_prefix,
        intents=intents,
        owner_id=config.discord.owner_id,
    )

    # Store config and database references
    bot.config = config
    bot.db = db

    # Initialize core systems
    try:
        # Permission system
        logger.info("Setting up permission system...")
        bot.permissions = PermissionManager()

        # Feature manager and load features
        logger.info("Loading features...")
        feature_manager = FeatureManager(bot)
        bot.feature_manager = feature_manager
        await feature_manager.load_all_features()

        # Set up LLM event handlers
        logger.info("Setting up LLM events...")
        await setup_llm_events(bot)

        # Initialize command syncer
        logger.info("Initializing command syncer...")
        bot.command_syncer = CommandSyncer(bot)

        logger.info("Bot initialization complete!")

    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        raise

    return bot
