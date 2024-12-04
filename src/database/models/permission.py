from sqlalchemy import Column, String, BigInteger, Boolean, Integer, Enum
from src.database.models import BaseModel
import enum


class PermissionType(enum.Enum):
    ALLOW = "allow"
    DENY = "deny"


class Permission(BaseModel):
    __tablename__ = "permissions"

    target_type = Column(String(10), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    permission_type = Column(Enum(PermissionType), default=PermissionType.ALLOW)

    admin_perms = Column(Boolean, default=None)
    bot_usage = Column(Boolean, default=None)
    message_perms = Column(Boolean, default=None)
    channel_perms = Column(Boolean, default=None)
    moderation_perms = Column(Boolean, default=None)

    max_requests_per_day = Column(Integer, default=None)

    class Config:
        unique_together = (("target_type", "target_id", "guild_id"),)
