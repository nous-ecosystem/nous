import asyncio
from src.injection import Container, configure_container
from src.core.config import config
from src.core.module_manager import initialize_bot


async def main():
    """
    Main entry point for the Discord bot application.
    """
    # Create and configure dependency injection container
    container = Container()
    configure_container(container)

    # Initialize and run the bot
    bot = await initialize_bot()
    await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
