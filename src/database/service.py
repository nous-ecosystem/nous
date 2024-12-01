from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import AsyncSessionFactory, init_db
from src.utils.logging import get_logger

logger = get_logger()


class DatabaseService:
    """Service class for database operations."""

    def __init__(self):
        self.logger = logger

    async def initialize(self):
        """Initialize the database."""
        self.logger.info("Initializing database...")
        await init_db()
        self.logger.info("Database initialized successfully")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with AsyncSessionFactory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database error: {e}")
                raise
            finally:
                await session.close()
