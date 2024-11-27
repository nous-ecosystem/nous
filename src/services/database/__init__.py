from typing import Optional, Dict, Any, cast
from .manager import DatabaseManager, DatabaseType, db_manager
from .client import DatabaseClient, CacheableDatabase, VectorDatabase
from .models import Message, Base

__all__ = [
    "DatabaseManager",
    "DatabaseType",
    "DatabaseClient",
    "CacheableDatabase",
    "VectorDatabase",
    "Message",
    "Base",
    "setup_databases",
]


async def setup_databases(
    mysql_config: Optional[Dict[str, Any]] = None,
    redis_config: Optional[Dict[str, Any]] = None,
    lancedb_config: Optional[Dict[str, Any]] = None,
) -> None:
    """Initialize and register database connections.

    Example usage:
        await setup_databases(
            mysql_config={
                "connection_string": "mysql+aiomysql://user:pass@localhost/db"
            },
            redis_config={
                "host": "localhost",
                "port": 6379
            },
            lancedb_config={
                "uri": "data/vectors"
            }
        )

        # Get specific database client
        mysql_client = await db_manager.get_client("mysql")
        redis_client = await db_manager.get_client("redis")
        vector_client = await db_manager.get_client("vectors")

        # Create a new message
        message = await mysql_client.create(Message, {
            "content": "Hello, world!",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"source": "user"},
            "timestamp": time.time()
        })

        # Cache the message
        await redis_client.cache_set(f"message:{message.id}", message)

        # Store message embedding
        await vector_client.add_vectors(
            "message_embeddings",
            vectors=[[0.1, 0.2, 0.3]],
            metadata=[{"message_id": message.id}]
        )

        # Search similar messages
        similar = await vector_client.search_vectors(
            "message_embeddings",
            query_vector=[0.1, 0.2, 0.3],
            limit=5
        )
    """
    # Register MySQL database if config provided
    if mysql_config:
        db_manager.register_database("mysql", DatabaseType.MYSQL, mysql_config)

    # Register Redis database if config provided
    if redis_config:
        db_manager.register_database("redis", DatabaseType.REDIS, redis_config)

    # Register LanceDB database if config provided
    if lancedb_config:
        db_manager.register_database("vectors", DatabaseType.LANCEDB, lancedb_config)

        # Initialize vector collection for embeddings
        client = await db_manager.get_client("vectors")
        if client:
            vector_client = cast(VectorDatabase, client)
            await vector_client.create_collection("message_embeddings", dimension=1536)
