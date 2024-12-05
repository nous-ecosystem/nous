import discord
from discord import app_commands
from discord.ext import commands
from src.database.models.permission import PermissionType
from src.utils.permissions import permission_manager
from typing import Optional, Union
from discord.abc import GuildChannel
from discord import Member, Role, TextChannel, VoiceChannel, CategoryChannel
from src.utils.logger import logger

# Define separate Union types
ChannelType = Union[TextChannel, VoiceChannel, CategoryChannel]
MemberRoleType = Union[Member, Role]


class TargetIndicator(discord.ui.Button):
    def __init__(self, text: str):
        super().__init__(style=discord.ButtonStyle.secondary, label=text, disabled=True)


class PermissionCategory:
    def __init__(
        self, display_name: str, description: str, permissions: dict, emoji: str
    ):
        self.display_name = display_name
        self.description = description
        self.permissions = permissions
        self.emoji = emoji


class PermissionsView(discord.ui.View):
    def __init__(self, cog, interaction, target):
        super().__init__(timeout=180)
        self.cog = cog
        self.interaction = interaction
        self.target = target
        self.current_view = "categories"
        self.permission_categories = {
            "general": PermissionCategory(
                "General Access",
                "Basic bot usage and access permissions",
                {
                    "use_commands": "Use Basic Commands",
                    "view_content": "View Bot Content",
                    "interact_features": "Use Basic Features",
                },
                "🔑",
            ),
            "moderation": PermissionCategory(
                "Moderation Tools",
                "Moderation and member management capabilities",
                {
                    "manage_messages": "Delete/Edit Messages",
                    "manage_members": "Manage Members",
                    "view_logs": "View Logs",
                },
                "🛡️",
            ),
            "advanced": PermissionCategory(
                "Advanced Controls",
                "Advanced configuration and management",
                {
                    "manage_settings": "Configure Bot",
                    "manage_integrations": "Manage Integrations",
                    "override_limits": "Override Limits",
                },
                "⚙️",
            ),
        }
        self.update_view_items()

    def update_view_items(self):
        self.clear_items()

        # Add target indicator
        target_type = self._get_target_type_display()
        self.add_item(TargetIndicator(f"{target_type}: {self.target.name}"))

        if self.current_view == "categories":
            self.add_item(CategorySelect(self.permission_categories))
        else:
            category = self.permission_categories[self.current_view]
            self.add_item(PermissionSelect(category.permissions))
            self.add_item(BackButton())

    def _get_target_type_display(self):
        if isinstance(self.target, discord.Member):
            return "User"
        elif isinstance(self.target, discord.Role):
            return "Role"
        return "Channel"

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="Session Expired",
            description="⌛ The permission management session has timed out.",
            color=discord.Color.red(),
        )
        await self.interaction.followup.edit_message(
            self.interaction.message.id, embed=embed, view=self
        )


class CategorySelect(discord.ui.Select):
    def __init__(self, categories):
        options = [
            discord.SelectOption(
                label=data["display"],
                value=category_name,
            )
            for category_name, data in categories.items()
        ]
        super().__init__(placeholder="Select permission category", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.current_view = self.values[0]

        embed = await create_permissions_embed(
            self.view.target,
            self.view.permission_categories[self.values[0]],
            await get_current_permissions(interaction, self.view),
        )

        self.view.update_view_items()
        await interaction.message.edit(embed=embed, view=self.view)


class PermissionSelect(discord.ui.Select):
    def __init__(self, permissions):
        options = [
            discord.SelectOption(
                label=display_name,
                value=perm_name,
            )
            for perm_name, display_name in permissions.items()
        ]
        super().__init__(placeholder="Toggle permission", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        permission = self.values[0]
        category = self.view.current_view

        try:
            current_perms = await get_current_permissions(interaction, self.view)
            new_value = not getattr(current_perms, permission, False)

            await permission_manager.set_permission(
                guild_id=interaction.guild_id,
                target_type=self.view.cog._get_target_type(self.view.target),
                target_id=self.view.target.id,
                **{permission: new_value},
            )

            embed = await create_permissions_embed(
                self.view.target,
                self.view.permission_categories[category],
                await get_current_permissions(interaction, self.view),
            )

            await interaction.message.edit(embed=embed, view=self.view)

            confirm_embed = discord.Embed(
                title="Permission Updated",
                description=f"{'✅' if new_value else '❌'} **{permission.replace('_', ' ').title()}**",
                color=discord.Color.green() if new_value else discord.Color.red(),
            )
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Failed to update permission: {str(e)}")
            await interaction.followup.send(
                "An error occurred while updating the permission. Please try again.",
                ephemeral=True,
            )


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Back")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.current_view = "categories"

        embed = await create_category_overview_embed(
            self.view.target,
            self.view.permission_categories,
            await get_current_permissions(interaction, self.view),
        )

        self.view.update_view_items()
        await interaction.message.edit(embed=embed, view=self.view)


async def create_permissions_embed(target, category_data, current_perms):
    embed = discord.Embed(
        title=f"{category_data.emoji} {category_data.display_name}",
        description=category_data.description,
        color=discord.Color.blue(),
    )

    target_type = (
        "👤 User"
        if isinstance(target, Member)
        else "🎭 Role"
        if isinstance(target, Role)
        else "📝 Channel"
    )
    embed.add_field(
        name="Managing Permissions For:",
        value=f"{target_type} **{target.name}**",
        inline=False,
    )

    status_list = []
    for perm_name, display_name in category_data.permissions.items():
        value = getattr(current_perms, perm_name, False)
        emoji = "✅" if value else "❌"
        status_list.append(f"{emoji} **{display_name}**")

    embed.add_field(
        name="Current Settings",
        value="\n".join(status_list) if status_list else "*No permissions configured*",
        inline=False,
    )

    embed.set_footer(
        text="Select a permission to toggle it • Changes are saved automatically"
    )
    return embed


async def create_category_overview_embed(target, categories, current_perms):
    embed = discord.Embed(
        title="🔐 Permission Management",
        description="Select a category to manage specific permissions",
        color=discord.Color.blue(),
    )

    target_type = (
        "👤 User"
        if isinstance(target, Member)
        else "🎭 Role"
        if isinstance(target, Role)
        else "📝 Channel"
    )
    embed.add_field(
        name="Managing Permissions For:",
        value=f"{target_type} **{target.name}**",
        inline=False,
    )

    for category_name, category_data in categories.items():
        enabled_count = sum(
            1
            for perm_name in category_data.permissions.keys()
            if getattr(current_perms, perm_name, False)
        )
        total_count = len(category_data.permissions)

        status = f"{enabled_count}/{total_count} enabled"
        embed.add_field(
            name=f"{category_data.emoji} {category_data.display_name}",
            value=f"{category_data.description}\n*{status}*",
            inline=False,
        )

    embed.set_footer(text="Select a category to manage its permissions")
    return embed


async def get_current_permissions(interaction, view):
    return await permission_manager.repo.get_permissions(
        target_type=view.cog._get_target_type(view.target),
        target_id=view.target.id,
        guild_id=interaction.guild_id,
    )


class PermissionsCog(commands.Cog, name="Permissions"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perms")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        member="The user to manage permissions for",
        role="The role to manage permissions for",
        channel="The channel to manage permissions for",
    )
    async def perms(
        self,
        interaction: discord.Interaction,
        member: Optional[Member] = None,
        role: Optional[Role] = None,
        channel: Optional[ChannelType] = None,
    ):
        """Open the permissions management GUI for the specified target"""
        try:
            # Check if exactly one target was provided
            provided_params = sum(
                param is not None for param in [member, role, channel]
            )
            if provided_params != 1:
                await interaction.response.send_message(
                    "Please specify exactly one target (user, role, or channel).",
                    ephemeral=True,
                )
                return

            target = member or role or channel
            view = PermissionsView(self, interaction, target)

            # Get current permissions and create initial embed
            current_perms = await get_current_permissions(interaction, view)
            embed = await create_category_overview_embed(
                target, view.permission_categories, current_perms
            )

            await interaction.response.send_message(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Error in perms command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An error occurred while setting up permissions management.",
                    ephemeral=True,
                )

    async def handle_user(self, interaction: discord.Interaction, target: Member):
        target = interaction.guild.get_member(target.id)
        if not target:
            await interaction.response.send_message(
                "Invalid target. Please specify a valid user.", ephemeral=True
            )
            return
        view = PermissionsView(self, interaction, target)
        await interaction.response.send_message(
            "Managing permissions for the user.", view=view
        )

    async def handle_role(self, interaction: discord.Interaction, target: Role):
        target = interaction.guild.get_role(target.id)
        if not target:
            await interaction.response.send_message(
                "Invalid target. Please specify a valid role.", ephemeral=True
            )
            return
        view = PermissionsView(self, interaction, target)
        await interaction.response.send_message(
            "Managing permissions for the role.", view=view
        )

    async def handle_channel(
        self,
        interaction: discord.Interaction,
        target: ChannelType,
    ):
        target = interaction.guild.get_channel(target.id)
        if not isinstance(target, ChannelType):
            await interaction.response.send_message(
                "Invalid target. Please specify a valid channel.", ephemeral=True
            )
            return
        view = PermissionsView(self, interaction, target)
        await interaction.response.send_message(
            "Managing permissions for the channel.", view=view
        )

    def _get_target_type(self, target: MemberRoleType) -> str:
        """Helper method to determine target type"""
        if isinstance(target, Member):
            return "user"
        elif isinstance(target, Role):
            return "role"
        elif isinstance(target, (TextChannel, VoiceChannel, CategoryChannel)):
            return "channel"
        raise ValueError("Invalid target type")


async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
