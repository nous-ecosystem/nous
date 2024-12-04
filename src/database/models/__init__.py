from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from src.database.manager import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# After BaseModel is defined, then import the models
from .command_hash import CommandHash
from .permission import Permission
from .user import User

__all__ = ["BaseModel", "CommandHash", "Permission", "User"]
