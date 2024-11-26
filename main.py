# src/core/main.py

import asyncio
import logging
import signal
from src.containers import Container
from src.core.bot import Bot

logger = logging.getLogger(__name__)


async def main():
    """Entry point for the Discord bot."""
    bot = None
    container = None
    try:
        # Initialize the container
        logger.debug("Creating container...")
        container = Container()
        await container.initialize()

        # Create bot instance
        logger.debug("Creating bot instance...")
        bot = Bot(container=container)

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(shutdown(bot)))
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.create_task(shutdown(bot)))

        # Start the bot
        logger.debug("Starting bot...")
        async with bot:
            await bot.start(container.config().discord.token)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if bot is not None:
            await shutdown(bot)
        elif container is not None:
            try:
                await container.shutdown_resources()
            except Exception as e:
                logger.error(f"Error shutting down container: {e}", exc_info=True)


async def shutdown(bot: Bot):
    """Perform graceful shutdown."""
    if bot is None:
        logger.warning("No bot instance to shutdown")
        return

    logger.info("Shutting down bot...")
    try:
        # Close bot connection if it exists and is open
        if hasattr(bot, "close") and not bot.is_closed():
            await bot.close()

        # Shutdown container resources if they exist
        if hasattr(bot, "container") and bot.container is not None:
            try:
                await bot.container.shutdown_resources()
            except Exception as e:
                logger.error(
                    f"Error shutting down container resources: {e}", exc_info=True
                )
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        logger.info("Bot shutdown complete")
