from typing import Any, Dict, List, Optional, Union
import lancedb
import numpy as np
import pandas as pd

from ..client import VectorDatabase


class LanceDBClient(VectorDatabase):
    """LanceDB client implementation for vector operations."""

    def __init__(
        self,
        uri: str = "data/vectors",
        **kwargs,
    ):
        """Initialize LanceDB client.

        Args:
            uri: Path to LanceDB database
            **kwargs: Additional connection parameters
        """
        self._uri = uri
        self._kwargs = kwargs
        self._db = None

    async def connect(self) -> None:
        """Establish connection to LanceDB."""
        self._db = lancedb.connect(self._uri, **self._kwargs)

    async def disconnect(self) -> None:
        """Close the LanceDB connection."""
        # LanceDB handles connection cleanup automatically
        self._db = None

    async def get_session(self) -> Any:
        """Get LanceDB connection."""
        if not self._db:
            raise RuntimeError("LanceDB not connected")
        return self._db

    async def create(self, model: Any, data: Dict[str, Any]) -> Any:
        """Create a new record in LanceDB."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        db = await self.get_session()
        table = db.create_table(
            model.__name__,
            data=pd.DataFrame([data]),
            mode="overwrite" if db.table_exists(model.__name__) else "create",
        )
        return data

    async def read(self, model: Any, id: Union[str, int]) -> Optional[Any]:
        """Read a record from LanceDB."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        db = await self.get_session()
        if not db.table_exists(model.__name__):
            return None

        table = db.open_table(model.__name__)
        result = table.search().where(f"id = '{id}'").to_pandas()
        return result.to_dict("records")[0] if not result.empty else None

    async def update(
        self, model: Any, id: Union[str, int], data: Dict[str, Any]
    ) -> Any:
        """Update a record in LanceDB."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        db = await self.get_session()
        if not db.table_exists(model.__name__):
            return None

        # Read existing data
        existing = await self.read(model, id)
        if not existing:
            return None

        # Update data
        updated = {**existing, **data}
        table = db.open_table(model.__name__)

        # Delete old record and insert updated one
        table.delete(f"id = '{id}'")
        table.add(pd.DataFrame([updated]))

        return updated

    async def delete(self, model: Any, id: Union[str, int]) -> bool:
        """Delete a record from LanceDB."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        db = await self.get_session()
        if not db.table_exists(model.__name__):
            return False

        table = db.open_table(model.__name__)
        deleted = table.delete(f"id = '{id}'")
        return deleted > 0

    async def query(self, model: Any, filters: Dict[str, Any]) -> List[Any]:
        """Query records from LanceDB."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        db = await self.get_session()
        if not db.table_exists(model.__name__):
            return []

        table = db.open_table(model.__name__)
        query = table.search()

        # Apply filters
        for key, value in filters.items():
            if isinstance(value, str):
                query = query.where(f"{key} = '{value}'")
            else:
                query = query.where(f"{key} = {value}")

        result = query.to_pandas()
        return result.to_dict("records")

    async def execute_raw(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw query in LanceDB."""
        db = await self.get_session()
        # LanceDB doesn't support raw SQL queries
        # This is a simplified implementation that returns table data
        if params and "table" in params:
            table = db.open_table(params["table"])
            return table.to_pandas()
        return None

    async def create_collection(self, name: str, dimension: int) -> None:
        """Create a vector collection."""
        db = await self.get_session()
        schema = {
            "vector": f"vector[f32]({dimension})",
            "metadata": "string",
        }
        if not db.table_exists(name):
            db.create_table(name, schema=schema)

    async def add_vectors(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """Add vectors to a collection."""
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")

        db = await self.get_session()
        if not db.table_exists(collection):
            raise ValueError(f"Collection {collection} does not exist")

        table = db.open_table(collection)
        data = {"vector": vectors, "metadata": [str(m) for m in metadata]}
        table.add(pd.DataFrame(data))

    async def search_vectors(
        self, collection: str, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        db = await self.get_session()
        if not db.table_exists(collection):
            raise ValueError(f"Collection {collection} does not exist")

        table = db.open_table(collection)
        results = table.search(query_vector).limit(limit).to_pandas()

        return [
            {
                "vector": row["vector"],
                "metadata": eval(row["metadata"]),
                "distance": row["_distance"],
            }
            for _, row in results.iterrows()
        ]
