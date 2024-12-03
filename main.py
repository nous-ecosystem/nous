import asyncio
import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.bot import create_bot
from src.config import Config
from src.utils.logger import logger


async def main():
    """
    Main async entry point for the Discord bot
    """
    try:
        # Create bot instance
        bot = create_bot()

        # Get configuration
        config = Config()

        # Start the bot
        await bot.start(config.DISCORD_TOKEN)

    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        raise


if __name__ == "__main__":
    try:
        # Run the bot using asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
