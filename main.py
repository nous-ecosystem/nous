#!/usr/bin/env python3
"""
Main entry point for the Discord bot application.
"""

import asyncio
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import discord
from src.core.client import create_bot_client
from src.injection import container
from src.utils.logging import SingletonLogger


def main():
    """
    Initialize and run the Discord bot.
    """
    # Get logger
    logger = SingletonLogger().get_logger()

    try:
        # Create bot client
        bot = create_bot_client()

        # Log startup information
        logger.info("Initializing Discord bot...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Discord.py version: {discord.__version__}")

        # Run the bot
        bot.run()

    except Exception as e:
        logger.error(f"Fatal error during bot initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
