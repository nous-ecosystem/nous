import discord
from discord import app_commands
from discord.ext import commands


class UtilityCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
