"""
Scheduling system for automated digest delivery
"""
import asyncio
import schedule
import time
import logging
from datetime import datetime, timezone
import pytz
from telegram_bot import AgricultureDigestBot
from config import DIGEST_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigestScheduler:
    """Scheduler for automated digest delivery"""
    
    def __init__(self):
        self.bot = AgricultureDigestBot()
        self.timezone = pytz.timezone(DIGEST_CONFIG.get('timezone', 'UTC'))
        self.schedule_time = DIGEST_CONFIG.get('digest_schedule', '08:00')
        
    def setup_schedule(self):
        """Setup the daily schedule"""
        try:
            # Schedule daily digest
            schedule.every().day.at(self.schedule_time).do(self.send_scheduled_digest)
            
            logger.info(f"Daily digest scheduled for {self.schedule_time} {self.timezone}")
            
        except Exception as e:
            logger.error(f"Error setting up schedule: {str(e)}")
    
    def send_scheduled_digest(self):
        """Send scheduled digest (wrapper for async function)"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async digest function
            loop.run_until_complete(self._send_digest_async())
            
            # Close the loop
            loop.close()
            
        except Exception as e:
            logger.error(f"Error in scheduled digest: {str(e)}")
    
    async def _send_digest_async(self):
        """Async wrapper for sending digest"""
        try:
            # Create a mock context for the scheduled send
            class MockContext:
                def __init__(self, bot):
                    self.bot = bot
            
            context = MockContext(self.bot.application.bot)
            await self.bot.send_daily_digest(context)
            
        except Exception as e:
            logger.error(f"Error in async digest send: {str(e)}")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Starting digest scheduler...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main function to run the scheduler"""
    try:
        scheduler = DigestScheduler()
        scheduler.setup_schedule()
        scheduler.run_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")

if __name__ == "__main__":
    main()
