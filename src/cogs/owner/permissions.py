import discord
from discord import app_commands
from discord.ext import commands
from src.database.models.permission import PermissionType
from src.utils.permissions import permission_manager
from typing import Optional, Union
from discord.abc import GuildChannel
from discord import Member, Role, TextChannel, VoiceChannel, CategoryChannel
from src.config import Config
from src.utils.logger import logger

# Define separate Union types
ChannelType = Union[TextChannel, VoiceChannel, CategoryChannel]
MemberRoleType = Union[Member, Role]


class PermissionsView(discord.ui.View):
    def __init__(
        self,
        cog,
        interaction: discord.Interaction,
        target: MemberRoleType,
    ):
        super().__init__(timeout=180)  # 3 minutes timeout
        self.cog = cog
        self.interaction = interaction
        self.target = target
        self.permissions = [
            ("admin_perms", "Admin Permissions"),
            ("bot_usage", "Bot Usage"),
            ("message_perms", "Message Permissions"),
            ("channel_perms", "Channel Permissions"),
            ("moderation_perms", "Moderation Permissions"),
            ("max_requests_per_day", "Daily Request Limit"),
        ]
        self.add_item(PermissionSelect(self.permissions))

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


class PermissionSelect(discord.ui.Select):
    def __init__(self, permissions):
        options = [
            discord.SelectOption(
                label=display_name,
                value=perm_name,
                description=f"Toggle {display_name}",
            )
            for perm_name, display_name in permissions
        ]
        super().__init__(
            placeholder="Select a permission to toggle...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        permission = self.values[0]

        if permission == "max_requests_per_day":
            # Handle numeric input separately
            modal = RequestLimitModal()
            await interaction.response.send_modal(modal)
            return

        # Toggle boolean permission
        try:
            current_perms = await permission_manager.repo.get_permissions(
                target_type=self.view.cog._get_target_type(self.view.target),
                target_id=self.view.target.id,
                guild_id=interaction.guild_id,
            )

            new_value = not getattr(current_perms, permission, False)

            await permission_manager.set_permission(
                interaction.guild_id,
                self.view.cog._get_target_type(self.view.target),
                self.view.target.id,
                permission,
                new_value,
            )

            # Update UI with new permission state
            embed = discord.Embed(
                title="Permission Updated",
                description=f"{'✅' if new_value else '❌'} **{permission.replace('_', ' ').title()}**",
                color=discord.Color.green() if new_value else discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to update permission: {str(e)}")
            await interaction.response.send_message(
                "An error occurred while updating the permission. Please try again.",
                ephemeral=True,
            )


class RequestLimitModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set Daily Request Limit")
        self.limit = discord.ui.TextInput(
            label="Daily Request Limit",
            placeholder="Enter number (0 for unlimited)",
            required=True,
        )
        self.add_item(self.limit)


class PermissionsCog(commands.Cog, name="Permissions"):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    async def is_owner(self, interaction: discord.Interaction) -> bool:
        """Check if the user is the bot owner"""
        user_id = interaction.user.id
        owner_id = int(self.config.DISCORD_OWNER_ID)
        logger.info(f"Checking owner status - User ID: {user_id}, Owner ID: {owner_id}")
        is_owner = user_id == owner_id
        logger.info(f"Is owner check result: {is_owner}")
        return is_owner

    @app_commands.command(name="perms")
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

        if not await self.is_owner(interaction):
            logger.warning(
                f"Access denied for user {interaction.user.id} ({interaction.user.name})"
            )
            embed = discord.Embed(
                title="Access Denied",
                description="❌ Only bot owners can use this command.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
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
        target_emoji = (
            "👤"
            if isinstance(target, Member)
            else "🏷️"
            if isinstance(target, Role)
            else "#️⃣"
        )
        embed.add_field(
            name="Target",
            value=f"{target_emoji} **{target.name}** (`{target_type}`)",
            inline=False,
        )

        # Add current permissions status if any exist
        if current_perms:
            status_list = []
            for perm in self.permissions:
                value = getattr(current_perms, perm, False)
                emoji = "✅" if value else "❌"
                status_list.append(f"{emoji} {perm.replace('_', ' ').title()}")

            embed.add_field(
                name="Current Permissions",
                value="\n".join(status_list[:5]) + "\n...",
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
        # Open the permissions management GUI for the user
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
        # Open the permissions management GUI for the role
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
        # Open the permissions management GUI for the channel
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
