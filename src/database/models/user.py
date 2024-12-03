from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..connection import Base


class DiscordUser(Base):
    """
    Model to store Discord user information
    """

    __tablename__ = "discord_users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    total_messages = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), server_default=func.now())


class UserPreference(Base):
    """
    Model to store user-specific bot preferences
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, nullable=False)
    preference_key = Column(String, nullable=False)
    preference_value = Column(String)
