from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from .base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default=dict)
