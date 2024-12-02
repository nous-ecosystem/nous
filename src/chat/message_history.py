from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
from .prompt_manager import PromptManager


@dataclass
class Message:
    content: str
    role: str
    timestamp: datetime


class MessageHistory:
    def __init__(
        self,
        expiry_time: timedelta = timedelta(hours=3),
        prompt_manager: Optional[PromptManager] = None,
    ):
        self.expiry_time = expiry_time
        self.conversations: Dict[int, deque[Message]] = {}  # channel_id -> messages
        self.prompt_manager = prompt_manager or PromptManager()

    def _estimate_token_count(self, message: str) -> int:
        """Estimate the number of tokens in a message."""
        return len(message) // 4 + 1

    def add_message(
        self,
        channel_id: int,
        content: str,
        role: str = "user",
        total_tokens: Optional[int] = 0,
    ) -> None:
        """Add a message to the history for a specific channel."""
        if channel_id not in self.conversations:
            self.conversations[channel_id] = deque(maxlen=20)

        # Reset history if total tokens exceed 6000
        if total_tokens > 6000:
            self.conversations[channel_id].clear()

        self.conversations[channel_id].append(
            Message(content=content, role=role, timestamp=datetime.now())
        )
        self._cleanup_expired(channel_id)

    def get_conversation_history(
        self,
        channel_id: int,
        capabilities: Optional[list[str]] = None,
        special_instructions: Optional[str] = None,
    ) -> list[dict]:
        """Get the conversation history for a channel in Groq-compatible format."""
        self._cleanup_expired(channel_id)

        # Get the system prompt from the prompt manager
        system_prompt = self.prompt_manager.get_system_prompt(
            bot_name="Nous",
            capabilities=capabilities
            or [
                "Deep knowledge of Discord culture and memes",
                "Always aware of ongoing conversations",
                "Dry humor with occasional self-awareness about being too online",
                "Actually helpful despite the sleep deprivation",
                "Perpetually available for chat",
            ],
            special_instructions=special_instructions
            or "Be the reliable friend who's always online but keep it chill.",
        )

        history = [{"role": "system", "content": system_prompt}]

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
