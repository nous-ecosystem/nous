from src.database.service import CRUDService
from src.database.models.user import User, UserSchema
from typing import Optional
from datetime import datetime


class UserService(CRUDService[User, UserSchema]):
    """Specialized service for User model with additional methods."""

    async def get_by_discord_id(self, session, discord_id: int) -> Optional[User]:
        """Retrieve a user by their Discord ID."""
        return await self.get_by_field(session, "discord_id", discord_id)

    async def upsert_user(
        self, session, discord_id: int, username: str, **kwargs
    ) -> User:
        """
        Upsert a user - create if not exists, update if exists.

        This method demonstrates a common pattern for Discord bots.
        """
        existing_user = await self.get_by_discord_id(session, discord_id)

        if existing_user:
            # Update existing user
            update_data = {
                "username": username,
                "last_seen": datetime.utcnow().isoformat(),
                **kwargs,
            }
            return await self.update(session, existing_user.id, update_data)

        # Create new user
        new_user_data = UserSchema(discord_id=discord_id, username=username, **kwargs)
        return await self.create(session, new_user_data)
