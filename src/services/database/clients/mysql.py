from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ..client import DatabaseClient


class MySQLClient(DatabaseClient):
    """MySQL database client implementation using SQLAlchemy."""

    def __init__(self, connection_string: str, **kwargs):
        """Initialize MySQL client.

        Args:
            connection_string: SQLAlchemy connection URL
            **kwargs: Additional connection parameters
        """
        self._connection_string = connection_string
        self._engine = None
        self._session_factory = None
        self._kwargs = kwargs

    async def connect(self) -> None:
        """Establish connection to MySQL database."""
        self._engine = create_async_engine(self._connection_string, **self._kwargs)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        if not self._session_factory:
            raise RuntimeError("Database not connected")
        return self._session_factory()

    async def create(self, model: Any, data: Dict[str, Any]) -> Any:
        """Create a new record."""
        session = await self.get_session()
        async with session as session:
            instance = model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def read(self, model: Any, id: Union[str, int]) -> Optional[Any]:
        """Read a record by ID."""
        session = await self.get_session()
        async with session as session:
            stmt = select(model).where(model.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update(
        self, model: Any, id: Union[str, int], data: Dict[str, Any]
    ) -> Any:
        """Update a record."""
        session = await self.get_session()
        async with session as session:
            stmt = select(model).where(model.id == id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()

            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                await session.commit()
                await session.refresh(instance)

            return instance

    async def delete(self, model: Any, id: Union[str, int]) -> bool:
        """Delete a record."""
        session = await self.get_session()
        async with session as session:
            stmt = select(model).where(model.id == id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()

            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False

    async def query(self, model: Any, filters: Dict[str, Any]) -> List[Any]:
        """Query records with filters."""
        session = await self.get_session()
        async with session as session:
            stmt = select(model)
            for key, value in filters.items():
                stmt = stmt.where(getattr(model, key) == value)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def execute_raw(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw query."""
        session = await self.get_session()
        async with session as session:
            stmt = text(query)
            result = await session.execute(stmt, params or {})
            await session.commit()
            return result
