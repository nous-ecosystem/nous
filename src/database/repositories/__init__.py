from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.manager import DatabaseManager
from src.database.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.db = DatabaseManager()

    async def create(self, **kwargs) -> T:
        async with self.db.get_session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def get_by_id(self, id: int) -> Optional[T]:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[T]:
        async with self.db.get_session() as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()

    async def update(self, id: int, **kwargs) -> Optional[T]:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            instance = result.scalar_one_or_none()
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                await session.refresh(instance)
            return instance

    async def delete(self, id: int) -> bool:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            instance = result.scalar_one_or_none()
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
