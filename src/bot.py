import asyncio
import sys
from dependency_injector.wiring import inject, Provide

from src.containers import Container
from src.core.client import NousBot


@inject
async def main(bot: NousBot = Provide[Container.bot]) -> None:
    """
    Main entry point for the Discord bot.

    Args:
        bot: Injected bot instance from the container
    """
    async with bot:
        await bot.start(bot.discord_config.token)


if __name__ == "__main__":
    # Wire the container to inject dependencies
    from src.containers import container

    container.wire(modules=[__name__, "src.core.client"])

    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown initiated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
