from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod


class RedisInterface(ABC):
    """Interface for Redis operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to Redis."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the Redis connection."""
        pass

    @abstractmethod
    async def json_set(self, key: str, value: Any) -> bool:
        """Set a JSON value."""
        pass

    @abstractmethod
    async def json_get(self, key: str) -> Optional[Any]:
        """Get a JSON value."""
        pass

    @abstractmethod
    async def json_delete(self, key: str) -> bool:
        """Delete a JSON value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a string value."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a string value."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value."""
        pass


class VectorInterface(ABC):
    """Interface for vector operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to vector database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the vector database connection."""
        pass

    @abstractmethod
    async def create_collection(self, name: str, dimension: int) -> None:
        """Create a vector collection."""
        pass

    @abstractmethod
    async def add_vectors(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """Add vectors to a collection."""
        pass

    @abstractmethod
    async def search_vectors(
        self, collection: str, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass
