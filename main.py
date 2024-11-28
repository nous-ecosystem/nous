#!/usr/bin/env python3
"""
Main entry point for the Discord bot.
Run this file to start the bot: python main.py
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Wire the container to inject dependencies
from src.containers import container

container.wire(modules=["src.bot", "src.core.client"])

if __name__ == "__main__":
    # Run the bot
    from src.bot import main

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown initiated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
