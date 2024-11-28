from typing import Any, Dict, List, Optional
import lancedb
import pandas as pd
import os

from ..client import VectorInterface


class LanceDBClient(VectorInterface):
    """LanceDB client implementation for vector operations."""

    def __init__(self, uri: str = "data/vectors", **kwargs):
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
        try:
            # Ensure database directory exists
            os.makedirs(self._uri, exist_ok=True)

            # Connect to database
            self._db = lancedb.connect(self._uri)

            # Test connection with a simple operation
            tables = self._db.table_names()
            if not tables:
                # Create a test table if none exist
                test_df = pd.DataFrame({"id": [1], "vector": [[0.0]]})
                self._db.create_table("_test", data=test_df)
                self._db.drop_table("_test")
        except Exception as e:
            self._db = None
            raise RuntimeError(f"Failed to connect to LanceDB: {str(e)}")

    async def disconnect(self) -> None:
        """Close the LanceDB connection."""
        # LanceDB handles connection cleanup automatically
        self._db = None

    def _get_db(self) -> Any:
        """Get LanceDB connection."""
        if not self._db:
            raise RuntimeError("LanceDB not connected")
        return self._db

    async def create_collection(self, name: str, dimension: int) -> None:
        """Create a vector collection."""
        db = self._get_db()
        # Create an empty DataFrame with the correct schema
        empty_df = pd.DataFrame(
            {
                "vector": [[0.0] * dimension],  # Initialize with zeros
                "metadata": ["{}"],  # Empty metadata
            }
        )
        db.create_table(name, data=empty_df, mode="overwrite")

    async def add_vectors(
        self,
        collection: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """Add vectors to a collection."""
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")

        db = self._get_db()
        try:
            table = db.open_table(collection)
            data = {"vector": vectors, "metadata": [str(m) for m in metadata]}
            table.add(pd.DataFrame(data))
        except Exception as e:
            raise ValueError(
                f"Failed to add vectors to collection {collection}: {str(e)}"
            )

    async def search_vectors(
        self, collection: str, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        db = self._get_db()
        try:
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
        except Exception as e:
            raise ValueError(
                f"Failed to search vectors in collection {collection}: {str(e)}"
            )
