from dependency_injector import containers, providers
from src.utils.logging import LoggerContainer
from src.core.config import get_settings


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration provider
    config = providers.Singleton(get_settings)

    # Logger provider
    logger = providers.Container(LoggerContainer)


# Create a single container instance
container = Container()

# Usage:
# from src.injection import container
# config = container.config()
# logger = container.logger.logger().get_logger()
