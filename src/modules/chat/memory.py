from typing import List, Optional
import time
import json
from src.services.database.client import RedisInterface


class ChatMemory:
    """Manages chat memory using Redis as a circular buffer with expiration."""

    def __init__(
        self, redis: RedisInterface, max_messages: int = 25, expiry_seconds: int = 5400
    ):
        """
        Initialize ChatMemory.

        Args:
            redis: Redis interface
            max_messages: Maximum number of messages to store per user (default: 25)
            expiry_seconds: Message expiration time in seconds (default: 5400 [1.5 hours])
        """
        self.redis = redis
        self.max_messages = max_messages
        self.expiry_seconds = expiry_seconds

    def _get_key(self, user_id: str) -> str:
        """Generate Redis key for user's message history."""
        return f"chat:history:{user_id}"

    async def add_message(
        self, user_id: str, message: str, timestamp: Optional[float] = None
    ) -> None:
        """
        Add a message to the user's chat history.

        Args:
            user_id: Discord user ID
            message: Message content
            timestamp: Message timestamp (defaults to current time)
        """
        key = self._get_key(user_id)
        timestamp = timestamp or time.time()

        message_data = {"content": message, "timestamp": timestamp}

        # Store as JSON
        await self.redis.json_set(key, message_data)
        # Set expiration
        await self.redis.set(key, "", ttl=self.expiry_seconds)

    async def get_history(self, user_id: str) -> List[dict]:
        """
        Retrieve user's chat history.

        Args:
            user_id: Discord user ID

        Returns:
            List of message dictionaries with content and timestamp
        """
        key = self._get_key(user_id)
        messages = await self.redis.json_get(key)

        if not messages:
            return []

        try:
            if isinstance(messages, list):
                return messages[-self.max_messages :]
            return [messages]
        except Exception:
            return []

    async def clear_history(self, user_id: str) -> None:
        """
        Clear user's chat history.

        Args:
            user_id: Discord user ID
        """
        key = self._get_key(user_id)
        await self.redis.delete(key)
