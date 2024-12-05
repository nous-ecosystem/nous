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


class PermissionsView(discord.ui.View):
    def __init__(self, cog, interaction, target):
        super().__init__(timeout=180)
        self.cog = cog
        self.interaction = interaction
        self.target = target
        self.current_view = "categories"
        self.permission_categories = {
            "admin_perms": {
                "display": "Admin Permissions",
                "permissions": {
                    "manage_server": "Manage Server",
                    "manage_roles": "Manage Roles",
                    "manage_channels": "Manage Channels",
                },
            },
            "message_perms": {
                "display": "Message Permissions",
                "permissions": {
                    "send_messages": "Send Messages",
                    "manage_messages": "Manage Messages",
                    "embed_links": "Embed Links",
                },
            },
            "channel_perms": {
                "display": "Channel Permissions",
                "permissions": {
                    "view_channels": "View Channels",
                    "manage_channels": "Manage Channels",
                    "connect": "Connect to Voice",
                },
            },
            "moderation_perms": {
                "display": "Moderation Permissions",
                "permissions": {
                    "kick_members": "Kick Members",
                    "ban_members": "Ban Members",
                    "timeout_members": "Timeout Members",
                },
            },
        }
        self.update_view_items()

    def update_view_items(self):
        self.clear_items()
        if self.current_view == "categories":
            self.add_item(CategorySelect(self.permission_categories))
        else:
            self.add_item(
                PermissionSelect(
                    self.permission_categories[self.current_view]["permissions"]
                )
            )
            self.add_item(BackButton())

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
        title=f"Permission Management - {category_data['display']}",
        color=discord.Color.blue(),
    )

    target_type = (
        "User"
        if isinstance(target, Member)
        else "Role"
        if isinstance(target, Role)
        else "Channel"
    )

    embed.add_field(
        name="Target", value=f"**{target.name}** (`{target_type}`)", inline=False
    )

    status_list = []
    for perm_name, display_name in category_data["permissions"].items():
        value = getattr(current_perms, perm_name, False)
        emoji = "✅" if value else "❌"
        status_list.append(f"{emoji} {display_name}")

    embed.add_field(
        name="Permissions",
        value="\n".join(status_list) if status_list else "No permissions available",
        inline=False,
    )

    return embed


async def create_category_overview_embed(target, categories, current_perms):
    embed = discord.Embed(title="Permission Management", color=discord.Color.blue())

    target_type = (
        "User"
        if isinstance(target, Member)
        else "Role"
        if isinstance(target, Role)
        else "Channel"
    )

    embed.add_field(
        name="Target", value=f"**{target.name}** (`{target_type}`)", inline=False
    )

    status_list = []
    for category_name, category_data in categories.items():
        category_enabled = any(
            getattr(current_perms, perm_name, False)
            for perm_name in category_data["permissions"].keys()
        )
        emoji = "✅" if category_enabled else "❌"
        status_list.append(f"{emoji} {category_data['display']}")

    embed.add_field(
        name="Permission Categories", value="\n".join(status_list), inline=False
    )

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
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Changed from owner check to admin check
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
        # Check if exactly one target was provided
        provided_params = sum(param is not None for param in [member, role, channel])
        if provided_params != 1:
            await interaction.response.send_message(
                "Invalid usage. Please specify a valid user, role, or channel.",
                ephemeral=True,
            )
            return

        target = member or role or channel

        if not target:
            await interaction.response.send_message(
                "Invalid target. Please specify a valid user, role, or channel.",
                ephemeral=True,
            )
            return

        view = PermissionsView(self, interaction, target)

        # Get current permissions
        current_perms = await permission_manager.repo.get_permissions(
            target_type=self._get_target_type(target),
            target_id=target.id,
            guild_id=interaction.guild_id,
        )

        embed = discord.Embed(title="Permission Management", color=discord.Color.blue())

        # Add target info
        target_type = (
            "User"
            if isinstance(target, Member)
            else "Role"
            if isinstance(target, Role)
            else "Channel"
        )

        target_emoji = "X"  # Placeholder for emoji
        embed.add_field(
            name="Target",
            value=f"{target_emoji} **{target.name}** (`{target_type}`)",
            inline=False,
        )

        # Add current permissions status if any exist
        if current_perms:
            status_list = []
            for perm_name, display_name in view.permission_categories["admin_perms"][
                "permissions"
            ].items():
                value = getattr(current_perms, perm_name, False)
                emoji = "✅" if value else "❌"
                status_list.append(f"{emoji} {display_name}")

            embed.add_field(
                name="Current Permissions",
                value="\n".join(status_list),
                inline=False,
            )

        await interaction.response.send_message(embed=embed, view=view)

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
