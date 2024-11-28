# chat/events.py

import discord
from discord.ext import commands


async def on_message(bot, cog, message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        await cog.handle_direct_message(message)
    else:
        if bot.user in message.mentions:
            await cog.handle_mention(message)


async def setup_events(bot, cog):
    bot.add_listener(lambda message: on_message(bot, cog, message), "on_message")
