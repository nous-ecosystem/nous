from src.database.models.user import User
from src.database.repositories import BaseRepository
from sqlalchemy.future import select


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_discord_id(self, discord_id: int):
        async with self.db.get_session() as session:
            result = await session.execute(
                select(self.model).filter(self.model.discord_id == discord_id)
            )
            return result.scalar_one_or_none()
