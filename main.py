#!/usr/bin/env python
"""
Entry point for Contest Tracker Bot

Run this script to start the bot:
    python main.py
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot import ContestBot

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Contest Tracker Bot...")
    
    try:
        bot = ContestBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
