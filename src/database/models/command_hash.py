from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from src.database.models import BaseModel


class CommandHash(BaseModel):
    __tablename__ = "command_hashes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    guild_id = Column(
        String(20), nullable=False
    )  # Using String for guild_id to support 'global'
    command_hash = Column(String(64), nullable=False)  # SHA-256 hash is 64 characters

    class Config:
        unique_together = (("guild_id", "command_hash"),)
