import asyncio
import sys
import traceback
from src.core.initialization import initialize_bot
from src.core.config import config
from src.utils.logging import get_logger

logger = get_logger()


async def start_bot():
    """
    Attempt to start the bot with multiple retry attempts.
    """
    max_retries = 5
    retry_delay = 10  # seconds between retries

    for attempt in range(max_retries):
        try:
            bot = await initialize_bot()
            await bot.start(config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Bot startup attempt {attempt + 1} failed: {e}")
            logger.error(traceback.format_exc())

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.critical("Failed to start bot after multiple attempts. Exiting.")
                sys.exit(1)


async def main():
    """
    Main entry point with comprehensive error handling.
    """
    try:
        await start_bot()
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Critical error during bot execution: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
