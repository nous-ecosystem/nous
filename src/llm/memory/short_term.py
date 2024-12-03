from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Deque, List


@dataclass
class MessageEntry:
    role: str
    content: str
    timestamp: datetime


class ShortTermMemory:
    def __init__(self, max_messages: int = 25, expiry_minutes: int = 45) -> None:
        self.messages: Deque[MessageEntry] = deque(maxlen=max_messages)
        self.expiry_minutes: int = expiry_minutes

    def add_message(self, role: str, content: str) -> None:
        self.cleanup_expired()
        self.messages.append(MessageEntry(role, content, datetime.now()))

    def get_conversation_history(self) -> List[dict[str, str]]:
        self.cleanup_expired()
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def cleanup_expired(self) -> None:
        expiry_time: datetime = datetime.now() - timedelta(minutes=self.expiry_minutes)
        while self.messages and self.messages[0].timestamp < expiry_time:
            self.messages.popleft()

    def clear(self) -> None:
        self.messages.clear()
