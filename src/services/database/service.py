from typing import Dict, Optional, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .core.redis import RedisManager
from .models.user import User
from .models.conversation import Conversation
from .init import init_database


class DatabaseService:
    """Unified database service combining SQLAlchemy and Redis"""

    def __init__(
        self,
        db_url: str = "mysql+aiomysql://user:pass@localhost:3306/botdb?charset=utf8mb4",
        redis_url: str = "redis://localhost",
    ):
        self.db_url = db_url
        self.redis = RedisManager(redis_url)
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """Initialize database connections"""
        if not self.engine:
            self.engine, self.async_session = await init_database(self.db_url)

    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        if not self.async_session:
            await self.initialize()
        return self.async_session()

    async def close(self):
        """Close all database connections"""
        if self.engine:
            await self.engine.dispose()
        await self.redis.close()

    # User operations
    async def get_or_create_user(self, discord_id: str, username: str) -> User:
        """Get existing user or create new one"""
        async with await self.get_session() as session:
            query = select(User).where(User.discord_id == discord_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                user = User(discord_id=discord_id, username=username)
                session.add(user)
                await session.commit()

            return user

    # Conversation operations
    async def create_conversation(
        self, user_id: str, channel_id: str, metadata: Dict = None
    ) -> Conversation:
        """Create new conversation"""
        async with await self.get_session() as session:
            conv = Conversation(
                user_id=user_id, channel_id=channel_id, chat_metadata=metadata or {}
            )
            session.add(conv)
            await session.commit()
            return conv

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
