import discord
from src.llm.interactions import handler
from src.utils.logger import logger


async def setup_llm_events(bot: discord.ext.commands.Bot):
    """Set up LLM event handlers for the bot"""

    async def on_message(message: discord.Message) -> None:
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return

        # Check if bot should respond
        should_respond = (
            (message.mentions and bot.user in message.mentions)  # Mentioned in server
            or isinstance(message.channel, discord.DMChannel)  # Direct message
        )

        if should_respond:
            async with message.channel.typing():
                response: str = await handler.handle_message(message)
                await message.channel.send(response)

    # Remove any existing message listeners to avoid duplicates
    bot.remove_listener(on_message)
    # Add the message listener
    bot.add_listener(on_message)
