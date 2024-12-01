from datetime import datetime
from typing import Any, Dict, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, Integer


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create a type variable for our models
ModelType = TypeVar("ModelType", bound=Base)


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class BaseDBModel(Base):
    """Abstract base model with common fields and functionality."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PydanticConfig:
    """Pydantic configuration for ORM mode."""

    from_attributes = True
    arbitrary_types_allowed = True


class BaseSchema(BaseModel):
    """Base Pydantic model for all schemas."""

    class Config(PydanticConfig):
        pass
