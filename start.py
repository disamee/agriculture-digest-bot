#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    try:
        logger.info("Starting Agriculture Digest Bot...")
        
        # Check environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        logger.info(f"Bot token configured: {bool(bot_token)}")
        logger.info(f"Channel ID configured: {bool(channel_id)}")
        logger.info(f"Port: {os.getenv('PORT', '8080')}")
        
        # Import and run the Railway app
        from main_railway import RailwayApp
        import asyncio
        
        app = RailwayApp()
        asyncio.run(app.run())
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
