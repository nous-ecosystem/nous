from sqlalchemy import Column, String, BigInteger, Boolean
from src.database.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    discord_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
