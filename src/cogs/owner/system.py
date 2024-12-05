import discord
from discord import app_commands
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger


class SystemCog(commands.Cog, name="System"):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    async def is_owner(self, interaction: discord.Interaction) -> bool:
        """Check if the user is the bot owner"""
        return interaction.user.id == int(self.config.DISCORD_OWNER_ID)

    @app_commands.command(name="reload")
    async def reload(self, interaction: discord.Interaction, module: str):
        """Reload a specific module"""
        if not await self.is_owner(interaction):
            await interaction.response.send_message(
                "Only the bot owner can use this command.", ephemeral=True
            )
            return

        try:
            await self.bot.reload_extension(f"src.cogs.{module}")
            await interaction.response.send_message(
                f"✅ Module `{module}` reloaded successfully!", ephemeral=True
            )
        except Exception as e:
            logger.error(f"Failed to reload module {module}: {str(e)}")
            await interaction.response.send_message(
                f"❌ Failed to reload module: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="shutdown")
    async def shutdown(self, interaction: discord.Interaction):
        """Safely shut down the bot"""
        if not await self.is_owner(interaction):
            await interaction.response.send_message(
                "Only the bot owner can use this command.", ephemeral=True
            )
            return

        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(SystemCog(bot))
