from dependency_injector import containers, providers
from src.utils.logging import LoggerResolver
from src.core.config import Config
from src.services.database.mock_service import MockDatabaseService
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    wiring_config = containers.WiringConfiguration(packages=["src.core"])

    # Configuration
    config = providers.Singleton(Config)

    # Logger
    logger = providers.Singleton(
        LoggerResolver.get_logger,
        log_level=config.provided.logging.level,
        log_dir=config.provided.logging.directory,
    )

    # Database
    database = providers.Singleton(MockDatabaseService)

    def __init__(self):
        super().__init__()
        self._db_instance: Optional[MockDatabaseService] = None

    async def initialize(self) -> None:
        """Initialize container resources."""
        logger.debug("Initializing container resources...")
        try:
            # Get and store database instance
            self._db_instance = self.database()
            if hasattr(self._db_instance, "initialize"):
                await self._db_instance.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize container resources: {e}")
            raise

    async def shutdown_resources(self) -> None:
        """Cleanup container resources."""
        logger.debug("Shutting down container resources...")
        try:
            # Cleanup database if initialized
            if self._db_instance and hasattr(self._db_instance, "close"):
                await self._db_instance.close()
        except Exception as e:
            logger.error(f"Error during container resource shutdown: {e}")
            raise
