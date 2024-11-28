# chat/chat.py

import discord
from discord.ext import commands
from typing import Optional, Dict, List, cast
from dependency_injector.wiring import inject, Provider
import logging

from src.services.llm import LLMManager, LLMProvider
from src.services.database.manager import DatabaseManager
from src.services.database.client import RedisInterface
from .memory import ChatMemory


class ChatCog(commands.Cog):
    """Discord chat module for conversational interactions."""

    def __init__(
        self,
        bot: commands.Bot,
        llm_manager: LLMManager,
        db_manager: DatabaseManager,
        config: Dict,
    ):
        """
        Initialize ChatCog.

        Args:
            bot: Discord bot instance
            llm_manager: LLM service manager
            db_manager: Database service manager
            config: Configuration dictionary
        """
        self.bot = bot
        self.llm_manager = llm_manager
        self.db_manager = db_manager
        self.config = config
        self.memory: Optional[ChatMemory] = None
        self._provider: Optional[LLMProvider] = None
        self.logger = logging.getLogger("chat_cog")

    async def setup(self) -> None:
        """Set up the chat cog by initializing Redis memory."""
        self.logger.info("Setting up ChatCog...")
        if self.memory is None:
            try:
                self.logger.info("Initializing Redis client...")
                redis_client = await self.db_manager.get_redis()
                self.memory = ChatMemory(redis_client)
                self.logger.info("Redis client initialized successfully")

                self.logger.info("Getting xAI provider...")
                self._provider = self.llm_manager.get_provider("xai")
                if self._provider is None:
                    self.logger.error("Failed to get xAI provider")
                else:
                    self.logger.info("xAI provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Error during setup: {str(e)}")
                raise

    async def handle_direct_message(self, message: discord.Message) -> None:
        """Handle direct messages."""
        self.logger.info(f"Handling DM from {message.author}: {message.content}")
        await self.handle_message(message)

    async def handle_mention(self, message: discord.Message) -> None:
        """Handle mentions in servers."""
        self.logger.info(
            f"Handling mention from {message.author} in {message.guild}: {message.content}"
        )
        await self.handle_message(message)

    async def handle_message(self, message: discord.Message) -> None:
        """
        Handle incoming messages.

        Args:
            message: Discord message
        """
        self.logger.info(f"Processing message from {message.author}: {message.content}")

        should_respond = await self.should_respond(message)
        self.logger.info(f"Should respond: {should_respond}")
        if not should_respond:
            return

        try:
            await self._ensure_setup()
            memory = cast(ChatMemory, self.memory)

            async with message.channel.typing():
                # Get conversation history
                history = await memory.get_history(str(message.author.id))
                self.logger.info(
                    f"Got history for {message.author}: {len(history)} messages"
                )

                # Generate response
                response = await self.generate_response(message, history)
                self.logger.info(f"Generated response: {response[:100]}...")

                # Store messages in memory
                await memory.add_message(str(message.author.id), message.content)
                await memory.add_message(str(message.author.id), response)

                # Send response
                await message.reply(response)
                self.logger.info("Response sent successfully")
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}", exc_info=True)
            await message.reply(
                "I apologize, but I encountered an error while processing your message."
            )

    async def _ensure_setup(self) -> None:
        """Ensure cog is properly set up."""
        if self.memory is None or self._provider is None:
            await self.setup()
        if self.memory is None or self._provider is None:
            raise RuntimeError("Failed to initialize chat systems")

    async def should_respond(self, message: discord.Message) -> bool:
        """
        Determine if the bot should respond to a message.

        Args:
            message: Discord message

        Returns:
            bool: True if bot should respond
        """
        # Always respond in DMs
        if isinstance(message.channel, discord.DMChannel):
            return True

        # Check for mention or reply
        is_mentioned = self.bot.user in message.mentions

        # Safely check reply reference
        is_reply = False
        if message.reference and message.reference.resolved:
            referenced_msg = message.reference.resolved
            if isinstance(referenced_msg, discord.Message) and referenced_msg.author:
                is_reply = referenced_msg.author.id == self.bot.user.id

        return bool(is_mentioned or is_reply)

    async def generate_response(
        self, message: discord.Message, history: List[dict]
    ) -> str:
        """
        Generate response using xAI.

        Args:
            message: Discord message
            history: Chat history

        Returns:
            str: Generated response
        """
        await self._ensure_setup()
        provider = cast(LLMProvider, self._provider)

        # Format history for context
        context = "\n".join(
            [
                f"User: {msg['content']}"
                if i % 2 == 0
                else f"Assistant: {msg['content']}"
                for i, msg in enumerate(history)
            ]
        )

        # Generate response using xAI
        try:
            response = await provider.generate(
                prompt=message.content, context=context if context else None
            )
            return response
        except Exception as e:
            # Log the error and return a fallback message
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
