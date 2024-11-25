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

    # Enhanced Redis operations
    async def cache_str_set(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> bool:
        return await self.redis.str_set(key, value, ttl)

    async def cache_str_get(self, key: str, default: str = None) -> Optional[str]:
        return await self.redis.str_get(key, default)

    async def cache_hash_set(self, key: str, mapping: Dict[str, Any]) -> bool:
        return await self.redis.hash_set(key, mapping)

    async def cache_hash_get(self, key: str, field: str) -> Any:
        return await self.redis.hash_get(key, field)

    async def cache_json_set(self, key: str, value: Any, path: str = ".") -> bool:
        return await self.redis.json_set(key, path, value)

    async def cache_json_get(
        self, key: str, path: str = ".", default: Any = None
    ) -> Any:
        return await self.redis.json_get(key, path, default)

    async def create_vector_index(
        self, schema: Dict[str, Any], overwrite: bool = False
    ):
        return await self.redis.create_vector_index(schema, overwrite)

    async def vector_search(
        self,
        index_name: str,
        vector: List[float],
        vector_field: str,
        return_fields: List[str] = None,
        num_results: int = 10,
    ):
        return await self.redis.vector_search(
            index_name, vector, vector_field, return_fields, num_results
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
