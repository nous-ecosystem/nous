#!/usr/bin/env python3
"""
Main entry point for the Discord bot application.
"""

import asyncio
import sys
import os
import pathlib

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import discord
from src.core.client import create_bot_client
from src.injection import container
from src.utils.logging import SingletonLogger
from src.database.supabase import SupabaseDatabase
from src.database.models import User  # Import your models here


class DiscordBot:
    """Main Discord bot class that handles initialization and startup."""

    def __init__(self):
        self.logger = SingletonLogger().logger

    async def initialize(self):
        """Separate async initialization method"""
        self.logger.info("Initializing Discord bot...")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Discord.py version: {discord.__version__}")

        try:
            self.logger.info("Initializing database connection...")
            self.db = SupabaseDatabase()

            self.logger.info("Initializing database tables...")
            await self.db.create_table(User, force=True)
            self.logger.info("Database tables created successfully")

            self.client = create_bot_client()
            if self.client is None:
                raise ValueError("Failed to create Discord bot client")

        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {str(e)}")
            raise

    async def start(self):
        """Start the Discord bot."""
        try:
            self.logger.info("Initializing database tables...")
            # Path to a flag file that tracks first-time table creation
            first_run_flag = pathlib.Path(".first_table_creation")

            # Force create tables only if the flag file doesn't exist
            if not first_run_flag.exists():
                self.logger.info("Performing first-time forced table creation...")
                try:
                    await self.db.create_table(User, force=True)

                    # Create the flag file to prevent future forced recreations
                    first_run_flag.touch()
                    self.logger.info("First-time table creation completed successfully")
                except Exception as e:
                    self.logger.error(
                        f"Failed to force create database tables: {str(e)}"
                    )
                    raise
            else:
                await self.db.create_table(User)
                self.logger.info("Database tables ensured")

            token = container.config().discord_token.get_secret_value()
            await self.client.start(token)
        except Exception as e:
            self.logger.error(f"Failed to start bot: {str(e)}")
            raise


async def main():
    """Initialize and run the Discord bot."""
    bot = DiscordBot()
    await bot.initialize()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
