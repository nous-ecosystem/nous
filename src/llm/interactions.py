from src.llm.providers.groq import GroqProvider
from src.llm.memory.short_term import ShortTermMemory
import discord
from typing import Dict, List


class InteractionHandler:
    def __init__(self) -> None:
        self.llm: GroqProvider = GroqProvider()
        self.memories: Dict[
            str, ShortTermMemory
        ] = {}  # Dict to store ShortTermMemory instances per channel

    def get_memory(self, channel_id: str) -> ShortTermMemory:
        if channel_id not in self.memories:
            self.memories[channel_id] = ShortTermMemory()
        return self.memories[channel_id]

    async def handle_message(self, message: discord.Message) -> str:
        memory: ShortTermMemory = self.get_memory(str(message.channel.id))

        # Add user message to memory
        memory.add_message("user", message.content)

        # Get conversation history
        messages: List[dict[str, str]] = memory.get_conversation_history()

        # Add system prompt if this is the start of a conversation
        if len(messages) <= 1:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant in a Discord chat. Be concise, friendly, and helpful.",
                },
            )

        # Get response from LLM
        response: str = await self.llm.chat_completion(messages=messages)

        # Add assistant's response to memory
        memory.add_message("assistant", response)

        return response


# Create a singleton instance
handler: InteractionHandler = InteractionHandler()
