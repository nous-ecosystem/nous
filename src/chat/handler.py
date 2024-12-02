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
            print(f"Processing DM: {message.content[:50]}...")
            await self._handle_chat(message)
            return

        # Enhanced mention and reply detection
        is_mentioned = self.client.user.id in [user.id for user in message.mentions]
        is_reply = (
            message.reference
            and message.reference.resolved
            and message.reference.resolved.author.id == self.client.user.id
        )

        # Only process and log if it's a relevant interaction
        if is_mentioned or is_reply:
            print(f"Processing mention/reply: {message.content[:50]}...")
            await self._handle_chat(message)

    async def _handle_chat(self, message: Message):
        """Process the message and generate an AI response."""
        try:
            # Add user's message to history first
            self.message_history.add_message(
                channel_id=message.channel.id, content=message.content, role="user"
            )

            # Get conversation history
            conversation = self.message_history.get_conversation_history(
                message.channel.id,
                capabilities=[
                    "Deep understanding of chan culture and imageboards",
                    "Witty banter and clever comebacks",
                    "Recognition of common baits and trolling attempts",
                    "Ability to maintain frame while handling edgy content",
                    "Based takes without being cringe",
                ],
                special_instructions="Stay based and authentic while maintaining your own frame. Don't get baited into controversial topics.",
            )

            # Generate response
            async with message.channel.typing():
                response = await self.client.loop.run_in_executor(
                    None, self.groq_client.generate_response, conversation
                )

                if isinstance(response, str) and response.strip():
                    total_tokens = self._estimate_token_count(response)
                    self.message_history.add_message(
                        channel_id=message.channel.id,
                        content=response,
                        role="assistant",
                        total_tokens=total_tokens,
                    )

                    await message.reply(response)
                else:
                    print(f"Error: Invalid response generated")
                    await message.reply("I'm having trouble generating a response.")

        except Exception as e:
            print(f"Error in chat handler: {str(e)}")
            import traceback

            traceback.print_exc()
            await message.reply(
                "I apologize, but I encountered an error while processing your message."
            )

    def _estimate_token_count(self, message: str) -> int:
        """Estimate the number of tokens in a message."""
        return len(message) // 4 + 1

    def clear_channel_history(self, channel_id: int) -> None:
        """Clear the conversation history for a specific channel."""
        self.message_history.clear_channel_history(channel_id)
