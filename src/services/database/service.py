from typing import Dict, Optional, Any, List
from .core.session import SQLAlchemySession
from .core.redis import RedisManager
from .models.user import User
from .models.conversation import Conversation


class DatabaseService:
    """Unified database service combining SQLAlchemy and Redis"""

    def __init__(
        self, sqlite_path: str = "data/db/bot.db", redis_url: str = "redis://localhost"
    ):
        self.sql = SQLAlchemySession(sqlite_path)
        self.redis = RedisManager(redis_url)

    async def close(self):
        """Close all database connections"""
        await self.redis.close()

    # User operations
    async def get_or_create_user(self, discord_id: str, username: str) -> User:
        """Get existing user or create new one"""
        session = self.sql.get_session()
        try:
            user = session.query(User).filter_by(discord_id=discord_id).first()
            if not user:
                user = User(discord_id=discord_id, username=username)
                session.add(user)
                session.commit()
            return user
        finally:
            session.close()

    # Conversation operations
    async def create_conversation(
        self, user_id: str, channel_id: str, metadata: Dict = None
    ) -> Conversation:
        """Create new conversation"""
        session = self.sql.get_session()
        try:
            conv = Conversation(
                user_id=user_id, channel_id=channel_id, chat_metadata=metadata or {}
            )
            session.add(conv)
            session.commit()
            return conv
        finally:
            session.close()

    # Redis operations
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return await self.redis.set(key, value, ttl)

    async def cache_get(self, key: str, default: Any = None) -> Any:
        return await self.redis.get(key, default)

    async def cache_delete(self, key: str) -> bool:
        return await self.redis.delete(key)

    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        session = self.sql.get_session()
        try:
            return session.query(Conversation).filter_by(id=conversation_id).first()
        finally:
            session.close()

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        session = self.sql.get_session()
        try:
            return session.query(Conversation).filter_by(user_id=user_id).all()
        finally:
            session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
