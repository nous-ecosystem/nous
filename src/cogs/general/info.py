import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class InfoCog(commands.Cog, name="Info"):
    def __init__(self, bot):
        self.bot = bot
        self._start_time = datetime.utcnow()

    @app_commands.command(name="about")
    async def about(self, interaction: discord.Interaction):
        """Display information about the bot"""
        embed = discord.Embed(
            title="Bot Information",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        # Calculate uptime
        uptime = datetime.utcnow() - self._start_time

        # Add fields
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server")
    async def server(self, interaction: discord.Interaction):
        """Display information about the current server"""
        guild = interaction.guild

        embed = discord.Embed(
            title=f"{guild.name} Information",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        # Add server information
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(
            name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(InfoCog(bot))
