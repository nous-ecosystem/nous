import logging
import asyncio

logger = logging.getLogger(__name__)


class MockDatabaseService:
    """Mock database service for testing purposes."""

    async def initialize(self):
        """Simulate database initialization."""
        logger.debug("Mock database initializing...")
        # Simulate some initialization work
        await asyncio.sleep(0.1)
        logger.debug("Mock database initialized.")
        return True

    async def close(self):
        """Simulate closing the database connection."""
        logger.debug("Mock database closing...")
        # Simulate some cleanup work
        await asyncio.sleep(0.1)
        logger.debug("Mock database connection closed.")
