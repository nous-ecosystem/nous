from src.database.models.permission import Permission
from src.database.repositories import BaseRepository
from sqlalchemy import select
from typing import List, Optional


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self):
        super().__init__(Permission)

    async def get_permissions(
        self, target_type: str, target_id: int, guild_id: int
    ) -> Optional[Permission]:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(
                    self.model.target_type == target_type,
                    self.model.target_id == target_id,
                    self.model.guild_id == guild_id,
                )
            )
            return result.scalar_one_or_none()

    async def get_all_guild_permissions(self, guild_id: int) -> List[Permission]:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.guild_id == guild_id)
            )
            return result.scalars().all()

    async def delete_by_target(
        self, target_type: str, target_id: int, guild_id: int
    ) -> bool:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(
                    self.model.target_type == target_type,
                    self.model.target_id == target_id,
                    self.model.guild_id == guild_id,
                )
            )
            instance = result.scalar_one_or_none()
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False
