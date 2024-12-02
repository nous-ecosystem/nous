from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass
class Message:
    content: str
    role: str
    timestamp: datetime


class MessageHistory:
    def __init__(
        self, max_messages: int = 25, expiry_time: timedelta = timedelta(hours=1)
    ):
        self.max_messages = max_messages
        self.expiry_time = expiry_time
        self.conversations: Dict[int, deque[Message]] = {}  # channel_id -> messages

    def add_message(self, channel_id: int, content: str, role: str = "user") -> None:
        """Add a message to the history for a specific channel."""
        if channel_id not in self.conversations:
            self.conversations[channel_id] = deque(maxlen=self.max_messages)

        self.conversations[channel_id].append(
            Message(content=content, role=role, timestamp=datetime.now())
        )
        self._cleanup_expired(channel_id)

    def get_conversation_history(self, channel_id: int) -> list[dict]:
        """Get the conversation history for a channel in Groq-compatible format."""
        self._cleanup_expired(channel_id)

        # Start with a system message
        history = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant in a Discord chat. Provide clear, concise, and friendly responses.",
            }
        ]

        if channel_id in self.conversations:
            history.extend(
                [
                    {"role": msg.role, "content": msg.content}
                    for msg in self.conversations[channel_id]
                ]
            )

        return history

    def _cleanup_expired(self, channel_id: int) -> None:
        """Remove expired messages from the conversation."""
        if channel_id not in self.conversations:
            return

        current_time = datetime.now()
        while (
            self.conversations[channel_id]
            and current_time - self.conversations[channel_id][0].timestamp
            > self.expiry_time
        ):
            self.conversations[channel_id].popleft()

    def clear_channel_history(self, channel_id: int) -> None:
        """Clear the conversation history for a specific channel."""
        if channel_id in self.conversations:
            self.conversations[channel_id].clear()
