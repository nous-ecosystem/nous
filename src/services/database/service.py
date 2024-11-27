from dependency_injector import containers, providers
from .manager import DatabaseManager, DatabaseType
from . import setup_databases


class DatabaseContainer(containers.DeclarativeContainer):
    """Dependency Injection container for database services."""

    # Config dependencies
    config = providers.DependencyProvider()

    # Database manager singleton
    db_manager = providers.Singleton(DatabaseManager)

    # Database setup using config
    db_setup = providers.Resource(
        setup_databases,
        mysql_config=providers.Factory(
            lambda config: {
                "connection_string": f"mysql+aiomysql://{config.database.user}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.name}"
            },
            config=config,
        ),
        redis_config=providers.Factory(
            lambda config: {
                "host": config.redis.host,
                "port": config.redis.port,
                "password": config.redis.password,
            },
            config=config,
        ),
        # LanceDB config - using a local file-based storage
        lancedb_config=providers.Factory(lambda: {"uri": "data/vectors"}),
    )
