from typing import Optional, List, Dict
import discord
from discord.permissions import Permissions
from src.database.repositories.permission_repository import PermissionRepository
from src.database.models.permission import Permission, PermissionType


class PermissionManager:
    def __init__(self):
        self.repo = PermissionRepository()

        # Map Discord permission names to our database columns
        self.discord_permission_map = {
            "view_channel": "view_channel",
            "manage_channels": "manage_channels",
            "manage_roles": "manage_roles",
            "manage_messages": "manage_messages",
            "send_messages": "send_messages",
            "send_messages_in_threads": "send_messages_in_threads",
            "create_public_threads": "create_public_threads",
            "create_private_threads": "create_private_threads",
            "attach_files": "attach_files",
            "add_reactions": "add_reactions",
            "use_external_emojis": "use_external_emojis",
            "use_external_stickers": "use_external_stickers",
            "mention_everyone": "mention_everyone",
            "manage_webhooks": "manage_webhooks",
            "moderate_members": "moderate_members",
        }

    async def check_permission(
        self,
        guild_id: int,
        user: discord.Member,
        permission_name: str,
        channel: Optional[discord.TextChannel] = None,
    ) -> bool:
        """
        Check if a user has a specific permission, considering both bot and Discord permissions
        """
        # First check Discord's native permissions
        if channel and permission_name in self.discord_permission_map:
            channel_perms = channel.permissions_for(user)
            if getattr(channel_perms, permission_name):
                return True

        # Get user's roles sorted by position (highest first)
        roles = sorted(user.roles, key=lambda r: r.position, reverse=True)

        # Check custom bot permissions
        # User-specific permissions
        user_perms = await self.repo.get_permissions("user", user.id, guild_id)
        if user_perms and getattr(user_perms, permission_name) is not None:
            if user_perms.permission_type == PermissionType.DENY:
                return False
            return getattr(user_perms, permission_name)

        # Role permissions (check each role in order of hierarchy)
        for role in roles:
            role_perms = await self.repo.get_permissions("role", role.id, guild_id)
            if role_perms and getattr(role_perms, permission_name) is not None:
                if role_perms.permission_type == PermissionType.DENY:
                    return False
                return getattr(role_perms, permission_name)

        # Channel-specific permissions if provided
        if channel:
            channel_perms = await self.repo.get_permissions(
                "channel", channel.id, guild_id
            )
            if channel_perms and getattr(channel_perms, permission_name) is not None:
                if channel_perms.permission_type == PermissionType.DENY:
                    return False
                return getattr(channel_perms, permission_name)

        # Default values for bot-specific permissions
        default_values = {
            "can_use_bot": True,
            "can_manage_permissions": False,
            "can_use_admin_commands": False,
            "max_requests_per_day": 100,
        }

        return default_values.get(permission_name, False)

    async def get_effective_permissions(
        self,
        guild_id: int,
        user: discord.Member,
        channel: Optional[discord.TextChannel] = None,
    ) -> Dict[str, bool]:
        """
        Get all effective permissions for a user in a specific context
        """
        effective_perms = {}

        # Check Discord native permissions
        if channel:
            discord_perms = channel.permissions_for(user)
            for perm_name in self.discord_permission_map:
                effective_perms[perm_name] = getattr(discord_perms, perm_name)

        # Check bot-specific permissions
        for perm_name in [
            "can_use_bot",
            "can_manage_permissions",
            "can_use_admin_commands",
            "max_requests_per_day",
        ]:
            effective_perms[perm_name] = await self.check_permission(
                guild_id, user, perm_name, channel
            )

        return effective_perms

    async def set_permission(
        self,
        guild_id: int,
        target_type: str,
        target_id: int,
        permission_type: PermissionType = PermissionType.ALLOW,
        **permissions,
    ) -> bool:
        """Set permissions for a target"""
        existing = await self.repo.get_permissions(target_type, target_id, guild_id)

        if existing:
            return (
                await self.repo.update(
                    existing.id, permission_type=permission_type, **permissions
                )
                is not None
            )
        else:
            return (
                await self.repo.create(
                    target_type=target_type,
                    target_id=target_id,
                    guild_id=guild_id,
                    permission_type=permission_type,
                    **permissions,
                )
                is not None
            )


permission_manager = PermissionManager()
