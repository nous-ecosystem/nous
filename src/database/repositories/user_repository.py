from sqlalchemy.future import select
from sqlalchemy import update
from ..connection import AsyncSessionLocal
from ..models.user import DiscordUser, UserPreference
from ..utils import get_session


class UserRepository:
    @classmethod
    async def create_user(cls, discord_id: str, username: str):
        async with get_session() as session:
            user = DiscordUser(discord_id=discord_id, username=username)
            session.add(user)
            return user

    @classmethod
    async def get_user(cls, discord_id: str):
        async with get_session() as session:
            result = await session.execute(
                select(DiscordUser).where(DiscordUser.discord_id == discord_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def increment_message_count(cls, discord_id: str):
        async with get_session() as session:
            await session.execute(
                update(DiscordUser)
                .where(DiscordUser.discord_id == discord_id)
                .values(total_messages=DiscordUser.total_messages + 1)
            )
