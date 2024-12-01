from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, BigInteger
from pydantic import Field

from src.database.base import BaseDBModel, BaseSchema, TimestampMixin


class User(BaseDBModel, TimestampMixin):
    """User model for storing Discord user data."""

    __tablename__ = "users"

    discord_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(length=32), nullable=False)
    discriminator = Column(String(length=4), nullable=True)
    last_seen = Column(String, nullable=True)


class UserSchema(BaseSchema):
    """Pydantic schema for User model."""

    id: Optional[int] = None
    discord_id: int
    username: str
    discriminator: Optional[str] = None
    last_seen: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
