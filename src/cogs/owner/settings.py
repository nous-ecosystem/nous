import discord
from discord import app_commands
from discord.ext import commands
from src.config import Config
from src.utils.logger import logger


class SettingsCategory:
    def __init__(self, display_name: str, description: str, settings: dict):
        self.display_name = display_name
        self.description = description
        self.settings = settings


class SettingsView(discord.ui.View):
    def __init__(self, cog, interaction, guild_id=None):
        super().__init__(timeout=180)
        self.cog = cog
        self.interaction = interaction
        self.guild_id = guild_id
        self.current_view = "categories"
        self.settings_categories = {
            "bot_core": SettingsCategory(
                "Core Settings",
                "Essential bot configuration settings",
                {
                    "enable_commands": "Enable Command Usage",
                    "enable_logging": "Enable Error Logging",
                    "enable_analytics": "Enable Usage Analytics",
                },
            ),
            "permissions": SettingsCategory(
                "Permission Settings",
                "Control access and restrictions",
                {
                    "strict_permissions": "Strict Permission Checking",
                    "allow_dm_commands": "Allow DM Commands",
                    "require_verification": "Require User Verification",
                },
            ),
            "features": SettingsCategory(
                "Feature Settings",
                "Toggle bot features and modules",
                {
                    "enable_ai": "Enable AI Features",
                    "enable_moderation": "Enable Moderation",
                    "enable_utilities": "Enable Utility Commands",
                },
            ),
        }
        self.update_view_items()

    def update_view_items(self):
        self.clear_items()

        # Add scope indicator
        scope_text = "Global Settings" if not self.guild_id else f"Server Settings"
        self.add_item(ScopeIndicator(scope_text))

        if self.current_view == "categories":
            self.add_item(CategorySelect(self.settings_categories))
        else:
            category = self.settings_categories[self.current_view]
            self.add_item(SettingSelect(category.settings))
            self.add_item(BackButton())


class CategorySelect(discord.ui.Select):
    def __init__(self, categories):
        options = [
            discord.SelectOption(
                label=data.display_name,
                value=category_name,
            )
            for category_name, data in categories.items()
        ]
        super().__init__(placeholder="Select settings category", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.current_view = self.values[0]

        embed = await create_settings_embed(
            self.view.settings_categories[self.values[0]],
            await get_current_settings(interaction, self.view),
        )

        self.view.update_view_items()
        await interaction.message.edit(embed=embed, view=self.view)


class SettingSelect(discord.ui.Select):
    def __init__(self, settings):
        options = [
            discord.SelectOption(
                label=display_name,
                value=setting_name,
            )
            for setting_name, display_name in settings.items()
        ]
        super().__init__(placeholder="Configure setting", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        setting = self.values[0]
        category = self.view.current_view

        try:
            current_settings = await get_current_settings(interaction, self.view)
            new_value = not getattr(current_settings, setting, False)

            # Update the setting in your config
            # await update_setting(setting, new_value)

            embed = await create_settings_embed(
                self.view.settings_categories[category],
                await get_current_settings(interaction, self.view),
            )

            await interaction.message.edit(embed=embed, view=self.view)

            confirm_embed = discord.Embed(
                title="Setting Updated",
                description=f"{'✅' if new_value else '❌'} **{setting.replace('_', ' ').title()}**",
                color=discord.Color.green() if new_value else discord.Color.red(),
            )
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Failed to update setting: {str(e)}")
            await interaction.followup.send(
                "An error occurred while updating the setting. Please try again.",
                ephemeral=True,
            )


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Back")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.current_view = "categories"

        embed = await create_category_overview_embed(
            self.view.settings_categories,
            await get_current_settings(interaction, self.view),
        )

        self.view.update_view_items()
        await interaction.message.edit(embed=embed, view=self.view)


class ScopeIndicator(discord.ui.Button):
    def __init__(self, text: str):
        super().__init__(style=discord.ButtonStyle.secondary, label=text, disabled=True)


class OwnerSettingsCog(commands.Cog, name="Owner Settings"):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    async def is_owner(self, interaction: discord.Interaction) -> bool:
        return await self.bot.is_owner(interaction.user)

    @app_commands.command(name="settings")
    async def settings(self, interaction: discord.Interaction):
        """Configure bot-wide settings (Owner only)"""
        if not await self.is_owner(interaction):
            embed = discord.Embed(
                title="Access Denied",
                description="❌ Only bot owners can use this command.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = SettingsView(self, interaction)
        current_settings = await get_current_settings(interaction, view)
        embed = await create_category_overview_embed(
            view.settings_categories, current_settings
        )
        await interaction.response.send_message(embed=embed, view=view)


async def create_settings_embed(category_data, current_settings, guild_name=None):
    embed = discord.Embed(
        title=f"Settings Management - {category_data.display_name}",
        description=category_data.description,
        color=discord.Color.blue(),
    )

    if guild_name:
        embed.set_author(name=f"Server: {guild_name}")

    settings_text = []
    for setting_name, display_name in category_data.settings.items():
        value = getattr(current_settings, setting_name, False)
        status = "[ENABLED]" if value else "[DISABLED]"
        settings_text.append(f"{status} {display_name}")

    embed.add_field(
        name="Available Settings",
        value="\n".join(settings_text) if settings_text else "No settings available",
        inline=False,
    )

    return embed


async def create_category_overview_embed(categories, current_settings):
    embed = discord.Embed(title="Settings Management", color=discord.Color.blue())

    status_list = []
    for category_name, category_data in categories.items():
        category_enabled = any(
            getattr(current_settings, setting_name, False)
            for setting_name in category_data["settings"].keys()
        )
        emoji = "✅" if category_enabled else "❌"
        status_list.append(f"{emoji} {category_data['display']}")

    embed.add_field(
        name="Setting Categories", value="\n".join(status_list), inline=False
    )

    return embed


async def get_current_settings(interaction, view):
    # Implement this to fetch current settings from your config
    return view.cog.config


async def setup(bot):
    await bot.add_cog(OwnerSettingsCog(bot))
