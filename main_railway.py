#!/usr/bin/env python3
"""
Railway-optimized main application file for Agriculture Digest Bot
"""
import asyncio
import logging
import os
import sys
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RailwayApp:
    """Railway-optimized application class"""
    
    def __init__(self):
        self.web_app = None
        self.web_runner = None
        self.bot = None
        self.running = False
    
    async def start_web_server(self):
        """Start web server for health checks"""
        try:
            self.web_app = web.Application()
            
            # Health check endpoint
            async def health_check(request):
                return web.json_response({
                    "status": "healthy",
                    "service": "agriculture-digest-bot",
                    "version": "1.0.0",
                    "bot_token_configured": bool(os.getenv('TELEGRAM_BOT_TOKEN')),
                    "channel_configured": bool(os.getenv('TELEGRAM_CHANNEL_ID'))
                })
            
            # Root endpoint
            async def root(request):
                return web.json_response({
                    "message": "Agriculture Digest Bot is running",
                    "health_check": "/health",
                    "status": "operational"
                })
            
            self.web_app.router.add_get('/health', health_check)
            self.web_app.router.add_get('/', root)
            
            # Get port from environment
            port = int(os.getenv('PORT', 8080))
            
            self.web_runner = web.AppRunner(self.web_app)
            await self.web_runner.setup()
            site = web.TCPSite(self.web_runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"Web server started on port {port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web server: {str(e)}")
            return False
    
    async def start_bot(self):
        """Start the Telegram bot"""
        try:
            # Check if bot token is configured
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                logger.warning("TELEGRAM_BOT_TOKEN not configured, bot will not start")
                return False
            
            # Import bot components with error handling
            try:
                from telegram_bot import AgricultureDigestBot
                from scheduler import DigestScheduler
            except ImportError as e:
                logger.error(f"Failed to import bot components: {str(e)}")
                return False
            
            # Initialize bot
            self.bot = AgricultureDigestBot()
            self.bot.setup_handlers()
            
            # Start the bot
            await self.bot.application.initialize()
            await self.bot.application.start()
            await self.bot.application.updater.start_polling()
            
            # Start scheduler (optional, don't fail if it doesn't work)
            try:
                scheduler = DigestScheduler()
                scheduler.setup_schedule()
                logger.info("Scheduler started successfully")
            except Exception as e:
                logger.warning(f"Scheduler failed to start: {str(e)}")
            
            logger.info("Telegram bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            return False
    
    async def stop(self):
        """Stop the application"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping Agriculture Digest App...")
        
        # Stop web server
        if self.web_runner:
            try:
                await self.web_runner.cleanup()
                logger.info("Web server stopped")
            except Exception as e:
                logger.error(f"Error stopping web server: {str(e)}")
        
        # Stop bot
        if self.bot and self.bot.application:
            try:
                await self.bot.application.updater.stop()
                await self.bot.application.stop()
                await self.bot.application.shutdown()
                logger.info("Bot stopped")
            except Exception as e:
                logger.error(f"Error stopping bot: {str(e)}")
        
        logger.info("Application stopped")
    
    async def run(self):
        """Run the application"""
        try:
            self.running = True
            
            logger.info("Starting Agriculture Digest Application...")
            logger.info(f"Environment: PORT={os.getenv('PORT', '8080')}")
            logger.info(f"Bot token configured: {bool(os.getenv('TELEGRAM_BOT_TOKEN'))}")
            logger.info(f"Channel configured: {bool(os.getenv('TELEGRAM_CHANNEL_ID'))}")
            
            # Start web server first (required for Railway health checks)
            logger.info("Starting web server...")
            web_started = await self.start_web_server()
            if not web_started:
                logger.error("Failed to start web server, exiting")
                sys.exit(1)
            
            logger.info("Web server started successfully")
            
            # Try to start bot (optional for health checks)
            logger.info("Attempting to start bot...")
            bot_started = await self.start_bot()
            if bot_started:
                logger.info("Bot started successfully")
            else:
                logger.warning("Bot failed to start, but web server is running")
            
            logger.info("Application is running. Health check available at /health")
            logger.info("Press Ctrl+C to stop the application")
            
            # Keep the application running
            try:
                while self.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            finally:
                await self.stop()
                
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            await self.stop()
            sys.exit(1)

def main():
    """Main function"""
    try:
        app = RailwayApp()
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
