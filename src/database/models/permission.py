from sqlalchemy import Column, String, BigInteger, Boolean, Integer, Enum
from src.database.models import BaseModel
from src.config import Config
import enum
import discord


class PermissionType(enum.Enum):
    ALLOW = "allow"
    DENY = "deny"


class Permission(BaseModel):
    __tablename__ = "permissions"

    # Target can be: "user", "role", or "channel"
    target_type = Column(String(10), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    permission_type = Column(Enum(PermissionType), default=PermissionType.ALLOW)

    # Bot-specific Permissions
    can_use_bot = Column(Boolean, default=None)
    can_manage_permissions = Column(Boolean, default=None)
    can_use_admin_commands = Column(Boolean, default=None)
    max_requests_per_day = Column(Integer, default=None)

    # Discord Permission Flags
    view_channel = Column(Boolean, default=None)
    manage_channels = Column(Boolean, default=None)
    manage_roles = Column(Boolean, default=None)
    manage_messages = Column(Boolean, default=None)
    send_messages = Column(Boolean, default=None)
    send_messages_in_threads = Column(Boolean, default=None)
    create_public_threads = Column(Boolean, default=None)
    create_private_threads = Column(Boolean, default=None)
    attach_files = Column(Boolean, default=None)
    add_reactions = Column(Boolean, default=None)
    use_external_emojis = Column(Boolean, default=None)
    use_external_stickers = Column(Boolean, default=None)
    mention_everyone = Column(Boolean, default=None)
    manage_webhooks = Column(Boolean, default=None)
    moderate_members = Column(Boolean, default=None)

    class Config:
        unique_together = (("target_type", "target_id", "guild_id", "permission_type"),)

    def is_owner(self, user_id):
        config = Config()
        owner_id = int(config.DISCORD_OWNER_ID)
        user_id = int(user_id)
        print(f"Checking owner: User ID {user_id} vs Owner ID {owner_id}")
        return user_id == owner_id
