from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    """Example model for storing chat messages with vector embeddings."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    embedding = Column(JSON)  # Store vector embeddings
    metadata = Column(JSON)  # Additional metadata
    timestamp = Column(Float, nullable=False)
