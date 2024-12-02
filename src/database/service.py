from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar, Generic, Type, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.base import BaseDBModel, BaseSchema
from src.database.config import AsyncSessionFactory, init_db
from src.utils.logging import get_logger

logger = get_logger()

ModelType = TypeVar("ModelType", bound=BaseDBModel)
SchemaType = TypeVar("SchemaType", bound=BaseSchema)


class CRUDService(Generic[ModelType, SchemaType]):
    """Generic CRUD service for database models."""

    def __init__(self, model: Type[ModelType], schema: Type[SchemaType]):
        self.model = model
        self.schema = schema
        self.logger = logger

    async def create(self, session: AsyncSession, data: SchemaType) -> ModelType:
        """Create a new database record."""
        try:
            db_obj = self.model(**data.model_dump(exclude_unset=True))
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            await session.rollback()
            raise

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """Retrieve a record by its ID."""
        query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(
        self, session: AsyncSession, field: str, value: Any
    ) -> Optional[ModelType]:
        """Retrieve a record by a specific field."""
        query = select(self.model).where(getattr(self.model, field) == value)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, session: AsyncSession, id: int, data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update an existing record."""
        try:
            db_obj = await self.get_by_id(session, id)
            if not db_obj:
                return None

            for key, value in data.items():
                setattr(db_obj, key, value)

            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.logger.error(f"Error updating {self.model.__name__}: {e}")
            await session.rollback()
            raise

    async def delete(self, session: AsyncSession, id: int) -> bool:
        """Delete a record by ID."""
        try:
            db_obj = await self.get_by_id(session, id)
            if not db_obj:
                return False

            await session.delete(db_obj)
            await session.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting {self.model.__name__}: {e}")
            await session.rollback()
            raise


class DatabaseService:
    """Service class for database operations."""

    def __init__(self):
        self.logger = logger

    async def initialize(self):
        """Initialize the database."""
        self.logger.info("Initializing database...")
        await init_db()
        self.logger.info("Database initialized successfully")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with AsyncSessionFactory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database error: {e}")
                raise
            finally:
                await session.close()
