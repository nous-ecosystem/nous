# chat/events.py

import discord
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chat import ChatCog


async def handle_message(
    bot: commands.Bot, cog: "ChatCog", message: discord.Message
) -> None:
    """
    Handle incoming messages.

    Args:
        bot: Discord bot instance
        cog: ChatCog instance
        message: Discord message
    """
    # Ignore bot messages
    if message.author.bot:
        return

    # Handle DMs and server messages appropriately
    if isinstance(message.channel, discord.DMChannel):
        await cog.handle_direct_message(message)
    else:
        # Check for mentions or replies
        if await cog.should_respond(message):
            await cog.handle_mention(message)


def setup_events(bot: commands.Bot, cog: "ChatCog") -> None:
    """
    Set up event listeners.

    Args:
        bot: Discord bot instance
        cog: ChatCog instance
    """
    # Remove any existing on_message handlers
    if hasattr(bot, "on_message"):
        bot.remove_listener(bot.on_message)

    # Create a closure to capture bot and cog
    async def on_message(message: discord.Message):
        await handle_message(bot, cog, message)

    # Add the new event handler
    bot.add_listener(on_message)
