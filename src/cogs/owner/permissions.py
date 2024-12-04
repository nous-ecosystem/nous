import discord
from discord import app_commands
from discord.ext import commands
from src.database.models.permission import PermissionType
from src.utils.permissions import permission_manager
from typing import Optional, Union
from discord.abc import GuildChannel
from discord import Member, Role
from src.config import Config

# Define the valid channel types for slash commands
VALID_CHANNEL_TYPES = [
    discord.ChannelType.text,
    discord.ChannelType.voice,
    discord.ChannelType.category,
    discord.ChannelType.news,
    discord.ChannelType.forum,
]

# Define target type union
TargetType = Union[Member, Role]
ChannelType = GuildChannel


class PermissionsCog(commands.Cog, name="Permissions"):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    async def is_owner(self, interaction: discord.Interaction) -> bool:
        """Check if the user is the bot owner"""
        return str(interaction.user.id) == self.config.DISCORD_OWNER_ID

    perm = app_commands.Group(
        name="perm",
        description="Manage bot permissions",
        guild_only=True,
        default_permissions=discord.Permissions(administrator=True),
    )

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

    @perm.command(name="set")
    @app_commands.describe(
        target="The user or role to set permissions for",
        permission="The permission to set",
        value="The permission value (true/false)",
    )
    @app_commands.autocomplete(permission=permission_autocomplete)
    async def set(
        self,
        interaction: discord.Interaction,
        target: TargetType,
        permission: str,
        value: bool,
    ):
        """Set a permission for a target"""
        if not await self.is_owner(interaction):
            await interaction.response.send_message(
                "❌ Only bot owners can use this command", ephemeral=True
            )
            return

        target_type = self._get_target_type(target)
        await permission_manager.set_permission(
            interaction.guild_id, target_type, target.id, permission, value
        )
        await interaction.response.send_message(
            f"✅ Set {permission} to {value} for {target_type} {target.name}"
        )

    @perm.command(name="view")
    @app_commands.describe(
        target="The user or role to view permissions for",
    )
    async def view(
        self,
        interaction: discord.Interaction,
        target: TargetType,
    ):
        """View permissions for a target"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        target_type = self._get_target_type(target)
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

    @perm.command(name="reset")
    @app_commands.describe(
        target="The user or role to reset permissions for",
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        target: TargetType,
    ):
        """Reset permissions for a target"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        target_type = self._get_target_type(target)
        success = await permission_manager.repo.delete_by_target(
            target_type, target.id, interaction.guild_id
        )

        if success:
            await interaction.followup.send(
                f"✅ Reset permissions for {target_type} {target.name}"
            )
        else:
            await interaction.followup.send("❌ No permissions found to reset")

    @perm.command(name="list")
    @app_commands.describe(filter="Optional: Filter by type (user/role)")
    async def list(self, interaction: discord.Interaction, filter: str = None):
        """List all permission entries"""
        await interaction.response.defer()

        if not await self.bot.is_owner(interaction.user):
            await interaction.followup.send("❌ Only bot owners can use this command")
            return

        perms = await permission_manager.repo.get_all_guild_permissions(
            interaction.guild_id
        )

        if filter:
            perms = [p for p in perms if p.target_type == filter]

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

    @perm.command(name="sync")
    @app_commands.describe(
        role="The role to sync permissions from",
    )
    async def sync(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        """Sync Discord role permissions"""
        await interaction.response.defer()

        # Convert Discord permissions to bot permissions
        discord_perms = role.permissions
        permission_updates = {
            perm_name: getattr(discord_perms, perm_name)
            for perm_name in permission_manager.discord_permission_map
            if hasattr(discord_perms, perm_name)
        }

        success = await permission_manager.set_permission(
            interaction.guild_id,
            "role",
            role.id,
            PermissionType.ALLOW,
            **permission_updates,
        )

        if success:
            await interaction.followup.send(
                f"✅ Synced Discord permissions for role {role.name}"
            )
        else:
            await interaction.followup.send("❌ Failed to sync permissions")

    @perm.command(name="check")
    @app_commands.describe(
        user="The user to check permissions for",
        channel="Optional: Check permissions in specific channel",
    )
    async def check(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        channel: Optional[discord.TextChannel] = None,
    ):
        """Check effective permissions for a user"""
        await interaction.response.defer()

        effective_perms = await permission_manager.get_effective_permissions(
            interaction.guild_id, user, channel
        )

        embed = discord.Embed(
            title=f"Effective Permissions for {user.name}",
            color=discord.Color.blue(),
            description=f"Channel: {channel.name if channel else 'Global'}",
        )

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

    def _get_target_type(self, target: TargetType) -> str:
        """Helper method to determine target type"""
        if isinstance(target, Member):
            return "user"
        elif isinstance(target, Role):
            return "role"
        raise ValueError("Invalid target type")


async def setup(bot):
    await bot.add_cog(PermissionsCog(bot))
