from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Index
from datetime import datetime
from .base import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("idx_user_channel", "user_id", "channel_id"),
        Index("idx_created_at", "created_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.discord_id"))
    channel_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chat_metadata = Column(JSON, default=dict)
