import discord
from discord import app_commands
from discord.ext import commands
from src.database.models.permission import PermissionType
from src.utils.permissions import permission_manager
from src.utils.logger import logger
from typing import Optional, Union
from discord import (
    TextChannel,
    VoiceChannel,
    CategoryChannel,
    ForumChannel,
)
from discord.abc import GuildChannel
from discord import Member, Role

# Define the valid channel types for slash commands
VALID_CHANNEL_TYPES = [
    discord.ChannelType.text,
    discord.ChannelType.voice,
    discord.ChannelType.category,
    discord.ChannelType.news,
    discord.ChannelType.forum,
]


class PermissionsCog(commands.Cog, name="Permissions"):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, interaction: discord.Interaction) -> bool:
        """Only allow guild-based commands and bot owners"""
        return interaction.guild is not None and self.bot.is_owner(interaction.user)

    perms_group = app_commands.Group(
        name="perms", description="Manage bot permissions", guild_only=True
    )

    @perms_group.command(name="set")
    @app_commands.describe(
        target_type="Type of target (user/role/channel)",
        target_user="The user to set permissions for",
        target_role="The role to set permissions for",
        target_channel="The channel to set permissions for",
        permission="The permission to set",
        value="The permission value (true/false)",
    )
    async def set_permission(
        self,
        interaction: discord.Interaction,
        target_type: str,
        permission: str,
        value: bool,
        target_user: Optional[Member] = None,
        target_role: Optional[Role] = None,
        target_channel: Optional[GuildChannel] = None,
    ):
        """Set a permission for a target"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        if target_type not in ["user", "role", "channel"]:
            await interaction.followup.send(
                "❌ Invalid target type. Use: user, role, or channel"
            )
            return

        target = target_user or target_role or target_channel
        if not target:
            await interaction.followup.send("❌ No target specified")
            return

        success = await permission_manager.set_permission(
            interaction.guild_id, target_type, target.id, **{permission: value}
        )

        if success:
            await interaction.followup.send(
                f"✅ Set `{permission}` to `{value}` for {target_type} {target.name}"
            )
        else:
            await interaction.followup.send("❌ Failed to set permission")

    @perms_group.command(name="view")
    @app_commands.describe(
        target_type="Type of target (user/role/channel)",
        target_user="The user to view permissions for",
        target_role="The role to view permissions for",
        target_channel="The channel to view permissions for",
    )
    async def view_permissions(
        self,
        interaction: discord.Interaction,
        target_type: str,
        target_user: Optional[Member] = None,
        target_role: Optional[Role] = None,
        target_channel: Optional[GuildChannel] = None,
    ):
        """View permissions for a target"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        target = target_user or target_role or target_channel
        if not target:
            await interaction.followup.send("❌ No target specified")
            return

        perms = await permission_manager.repo.get_permissions(
            target_type, target.id, interaction.guild_id
        )

        if not perms:
            await interaction.followup.send(
                "ℹ️ No specific permissions set (using defaults)"
            )
            return

        embed = discord.Embed(
            title=f"Permissions for {target.name}",
            color=discord.Color.blue(),
            description=f"Type: {target_type}\nID: {target.id}",
        )

        for column in perms.__table__.columns:
            if column.name not in [
                "id",
                "created_at",
                "updated_at",
                "target_type",
                "target_id",
                "guild_id",
            ]:
                value = getattr(perms, column.name)
                embed.add_field(
                    name=column.name.replace("_", " ").title(),
                    value=f"`{value}`",
                    inline=True,
                )

        await interaction.followup.send(embed=embed)

    @perms_group.command(name="reset")
    @app_commands.describe(
        target_type="Type of target (user/role/channel)",
        target_user="The user to reset permissions for",
        target_role="The role to reset permissions for",
        target_channel="The channel to reset permissions for",
    )
    async def reset_permissions(
        self,
        interaction: discord.Interaction,
        target_type: str,
        target_user: Optional[Member] = None,
        target_role: Optional[Role] = None,
        target_channel: Optional[GuildChannel] = None,
    ):
        """Reset permissions for a target to default"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        target = target_user or target_role or target_channel
        if not target:
            await interaction.followup.send("❌ No target specified")
            return

        success = await permission_manager.repo.delete_by_target(
            target_type, target.id, interaction.guild_id
        )

        if success:
            await interaction.followup.send(
                f"✅ Reset permissions for {target_type} {target.name}"
            )
        else:
            await interaction.followup.send("❌ No permissions found to reset")

    @perms_group.command(name="list")
    @app_commands.describe(
        target_type="Optional: Filter by target type (user/role/channel)"
    )
    async def list_permissions(
        self, interaction: discord.Interaction, target_type: str = None
    ):
        """List all permission entries for the guild"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        perms = await permission_manager.repo.get_all_guild_permissions(
            interaction.guild_id
        )

        if target_type:
            perms = [p for p in perms if p.target_type == target_type]

        if not perms:
            await interaction.followup.send("ℹ️ No permission entries found")
            return

        embed = discord.Embed(
            title=f"Permission Entries for {interaction.guild.name}",
            color=discord.Color.blue(),
        )

        for perm in perms:
            target = None
            if perm.target_type == "user":
                target = interaction.guild.get_member(perm.target_id)
            elif perm.target_type == "role":
                target = interaction.guild.get_role(perm.target_id)
            elif perm.target_type == "channel":
                target = interaction.guild.get_channel(perm.target_id)

            target_name = target.name if target else f"Unknown ({perm.target_id})"

            value = "\n".join(
                [
                    f"{k.replace('_', ' ').title()}: `{v}`"
                    for k, v in perm.__dict__.items()
                    if k
                    not in [
                        "_sa_instance_state",
                        "id",
                        "created_at",
                        "updated_at",
                        "target_type",
                        "target_id",
                        "guild_id",
                    ]
                ]
            )

            embed.add_field(
                name=f"{perm.target_type.title()}: {target_name}",
                value=value,
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @perms_group.command(name="sync")
    @app_commands.describe(
        target_type="Type of target (role)",
        target="The role to sync permissions from",
    )
    async def sync_discord_permissions(
        self,
        interaction: discord.Interaction,
        target_type: str,
        target: discord.Role,
    ):
        """Sync Discord role permissions with bot permissions"""
        await interaction.response.defer()

        if target_type != "role":
            await interaction.followup.send("❌ Can only sync permissions from roles")
            return

        # Convert Discord permissions to bot permissions
        discord_perms = target.permissions
        permission_updates = {
            perm_name: getattr(discord_perms, perm_name)
            for perm_name in permission_manager.discord_permission_map
            if hasattr(discord_perms, perm_name)
        }

        success = await permission_manager.set_permission(
            interaction.guild_id,
            target_type,
            target.id,
            PermissionType.ALLOW,
            **permission_updates,
        )

        if success:
            await interaction.followup.send(
                f"✅ Synced Discord permissions for role {target.name}"
            )
        else:
            await interaction.followup.send("❌ Failed to sync permissions")

    @perms_group.command(name="view_effective")
    @app_commands.describe(
        target="The user to view effective permissions for",
        channel="Optional: Check permissions in specific channel",
    )
    async def view_effective_permissions(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        channel: Optional[discord.TextChannel] = None,
    ):
        """View effective permissions for a user"""
        await interaction.response.defer()

        effective_perms = await permission_manager.get_effective_permissions(
            interaction.guild_id, target, channel
        )

        embed = discord.Embed(
            title=f"Effective Permissions for {target.name}",
            color=discord.Color.blue(),
            description=f"Channel: {channel.name if channel else 'Global'}",
        )

        # Group permissions by category
        categories = {
            "Bot Permissions": [
                "can_use_bot",
                "can_manage_permissions",
                "can_use_admin_commands",
                "max_requests_per_day",
            ],
            "Channel Permissions": [
                "view_channel",
                "send_messages",
                "manage_messages",
                "attach_files",
            ],
            "Thread Permissions": [
                "create_public_threads",
                "create_private_threads",
                "send_messages_in_threads",
            ],
            "Other Permissions": [
                "add_reactions",
                "use_external_emojis",
                "use_external_stickers",
                "mention_everyone",
                "manage_webhooks",
                "moderate_members",
            ],
        }

        for category, perms in categories.items():
            perm_text = "\n".join(
                f"{perm.replace('_', ' ').title()}: `{effective_perms.get(perm, False)}`"
                for perm in perms
                if perm in effective_perms
            )
            if perm_text:
                embed.add_field(name=category, value=perm_text, inline=False)

        await interaction.followup.send(embed=embed)

    # Autocomplete for permission names
    @set_permission.autocomplete("permission")
    async def permission_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        permissions = [
            "can_use_bot",
            "can_manage_permissions",
            "can_use_admin_commands",
            "max_requests_per_day",
        ]
        return [
            app_commands.Choice(name=perm, value=perm)
            for perm in permissions
            if current.lower() in perm.lower()
        ][:25]

    # Autocomplete for target types
    @set_permission.autocomplete("target_type")
    @view_permissions.autocomplete("target_type")
    @reset_permissions.autocomplete("target_type")
    @list_permissions.autocomplete("target_type")
    async def target_type_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        target_types = ["user", "role", "channel"]
        return [
            app_commands.Choice(name=t_type, value=t_type)
            for t_type in target_types
            if current.lower() in t_type.lower()
        ]


async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
