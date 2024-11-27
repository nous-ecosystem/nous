from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session


class DatabaseClient(ABC):
    """Abstract base class for database operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def get_session(self) -> Session:
        """Get a database session."""
        pass

    @abstractmethod
    async def create(self, model: Any, data: Dict[str, Any]) -> Any:
        """Create a new record."""
        pass

    @abstractmethod
    async def read(self, model: Any, id: Union[str, int]) -> Optional[Any]:
        """Read a record by ID."""
        pass

    @abstractmethod
    async def update(
        self, model: Any, id: Union[str, int], data: Dict[str, Any]
    ) -> Any:
        """Update a record."""
        pass

    @abstractmethod
    async def delete(self, model: Any, id: Union[str, int]) -> bool:
        """Delete a record."""
        pass

    @abstractmethod
    async def query(self, model: Any, filters: Dict[str, Any]) -> List[Any]:
        """Query records with filters."""
        pass

    @abstractmethod
    async def execute_raw(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw query."""
        pass


class CacheableDatabase(DatabaseClient):
    """Extension for databases that support caching."""

    @abstractmethod
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cache value."""
        pass

    @abstractmethod
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value."""
        pass

    @abstractmethod
    async def cache_delete(self, key: str) -> None:
        """Delete a cached value."""
        pass


class VectorDatabase(DatabaseClient):
    """Extension for vector database operations."""

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
