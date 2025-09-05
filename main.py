"""
Main application file for Agriculture Digest Bot
"""
import asyncio
import threading
import logging
import signal
import sys
import os
from aiohttp import web
from telegram_bot import AgricultureDigestBot
from scheduler import DigestScheduler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AgricultureDigestApp:
    """Main application class"""
    
    def __init__(self):
        self.bot = None
        self.scheduler = None
        self.scheduler_thread = None
        self.running = False
        self.web_app = None
        self.web_runner = None
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_bot(self):
        """Start the Telegram bot"""
        try:
            self.bot = AgricultureDigestBot()
            self.bot.setup_handlers()
            
            # Start the bot
            await self.bot.application.initialize()
            await self.bot.application.start()
            await self.bot.application.updater.start_polling()
            
            logger.info("Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            raise
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        try:
            self.scheduler = DigestScheduler()
            self.scheduler.setup_schedule()
            
            # Start scheduler in separate thread
            self.scheduler_thread = threading.Thread(target=self.scheduler.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    async def start_web_server(self):
        """Start web server for health checks"""
        try:
            self.web_app = web.Application()
            
            # Health check endpoint
            async def health_check(request):
                return web.json_response({
                    "status": "healthy",
                    "service": "agriculture-digest-bot",
                    "version": "1.0.0"
                })
            
            self.web_app.router.add_get('/health', health_check)
            self.web_app.router.add_get('/', health_check)
            
            # Get port from environment or use default
            port = int(os.getenv('PORT', 8080))
            
            self.web_runner = web.AppRunner(self.web_app)
            await self.web_runner.setup()
            site = web.TCPSite(self.web_runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"Web server started on port {port}")
            
        except Exception as e:
            logger.error(f"Failed to start web server: {str(e)}")
            raise
    
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
        
        # Scheduler will stop automatically when main thread exits
        logger.info("Application stopped")
    
    async def run(self):
        """Run the application"""
        try:
            self.setup_signal_handlers()
            self.running = True
            
            logger.info("Starting Agriculture Digest Application...")
            
            # Start web server
            await self.start_web_server()
            
            # Start scheduler
            self.start_scheduler()
            
            # Start bot
            await self.start_bot()
            
            logger.info("Application is running. Press Ctrl+C to stop.")
            
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
            await self.stop()
            raise

def main():
    """Main function"""
    try:
        app = AgricultureDigestApp()
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
