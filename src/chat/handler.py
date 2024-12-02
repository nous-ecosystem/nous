from typing import Optional
from discord import Message, Client, DMChannel

from .message_history import MessageHistory
from .groq_client import GroqClient


class ChatHandler:
    def __init__(
        self,
        client: Client,
        groq_api_key: Optional[str] = None,
        message_history: Optional[MessageHistory] = None,
    ):
        self.client = client
        self.message_history = message_history or MessageHistory()
        self.groq_client = GroqClient(groq_api_key)

        # Register the message handler
        self._register_events()

    def _register_events(self):
        # Store the original event
        original_on_message = self.client.on_message

        @self.client.event
        async def on_message(message: Message):
            # Handle our chat functionality
            await self.handle_message(message)
            # Call the original event handler if it exists
            if original_on_message:
                await original_on_message(message)

    async def handle_message(self, message: Message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author == self.client.user:
            return

        # Always respond in DMs
        if isinstance(message.channel, DMChannel):
            await self._handle_chat(message)
            return

        # Respond if the bot is mentioned or message is a reply to the bot
        is_mentioned = self.client.user in message.mentions
        is_reply = (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author == self.client.user
        )

        if is_mentioned or is_reply:
            await self._handle_chat(message)

    async def _handle_chat(self, message: Message):
        """Process the message and generate an AI response."""
        # Add user's message to history
        self.message_history.add_message(
            channel_id=message.channel.id, content=message.content, role="user"
        )

        # Get conversation history
        conversation = self.message_history.get_conversation_history(message.channel.id)

        # Generate response
        async with message.channel.typing():
            # Run the synchronous Groq call in an executor to prevent blocking
            response = await self.client.loop.run_in_executor(
                None, self.groq_client.generate_response, conversation
            )

        # Add bot's response to history
        self.message_history.add_message(
            channel_id=message.channel.id, content=response, role="assistant"
        )

        # Send the response
        await message.reply(response)

    def clear_channel_history(self, channel_id: int) -> None:
        """Clear the conversation history for a specific channel."""
        self.message_history.clear_channel_history(channel_id)
