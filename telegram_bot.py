"""
Telegram bot for Agriculture Digest
"""
import logging
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

from scraper import NewsScraper
from processor import ContentProcessor
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, DIGEST_CONFIG

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AgricultureDigestBot:
    """Main bot class for Agriculture Digest"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.channel_id = TELEGRAM_CHANNEL_ID
        self.scraper = NewsScraper()
        self.processor = ContentProcessor()
        self.application = None
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🌾 **Добро пожаловать в бот Agriculture Digest!**

Этот бот предоставляет ежедневные новости и аналитику сельскохозяйственного рынка.

**Доступные команды:**
/start - Показать приветственное сообщение
/digest - Создать и отправить текущий дайджест
/help - Показать справку
/status - Показать статус бота

**Возможности:**
• Ежедневная автоматическая доставка дайджестов
• Курируемые новости сельского хозяйства из множества источников
• Организация по темам
• Прямые ссылки на полные статьи

Бот автоматически отправляет ежедневные дайджесты в настроенный канал.
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📖 **Справка по боту Agriculture Digest**

**Команды:**
• `/start` - Приветственное сообщение и введение в бота
• `/digest` - Вручную создать и отправить текущий дайджест
• `/help` - Показать эту справку
• `/status` - Показать статус и конфигурацию бота

**Как это работает:**
1. Бот собирает новости сельского хозяйства из настроенных источников
2. Фильтрует и ранжирует статьи по релевантности
3. Группирует статьи по темам (Урожай, Животноводство, Технологии и т.д.)
4. Создает форматированный дайджест с резюме и ссылками
5. Отправляет дайджест в Telegram канал

**Источники:** Бот отслеживает множество источников новостей сельского хозяйства.

**Расписание:** Ежедневные дайджесты отправляются автоматически в 8:00 UTC.

Для поддержки или предложений обратитесь к администратору бота.
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get bot info
            bot_info = await context.bot.get_me()
            
            status_message = f"""
🤖 **Статус бота**

**Информация о боте:**
• Имя: {bot_info.first_name}
• Имя пользователя: @{bot_info.username}
• ID: {bot_info.id}

**Конфигурация:**
• Канал: {self.channel_id}
• Расписание: {DIGEST_CONFIG.get('digest_schedule', 'Не установлено')}
• Макс. статей: {DIGEST_CONFIG.get('max_total_articles', 'Не установлено')}
• Часовой пояс: {DIGEST_CONFIG.get('timezone', 'Не установлено')}

**Последнее обновление:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Статус:** ✅ Активен и отслеживает источники новостей сельского хозяйства
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting bot status: {str(e)}")
            await update.message.reply_text("❌ Error retrieving bot status")
    
    async def digest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /digest command - manually generate digest"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Создаю дайджест сельскохозяйственного рынка...")
            
            # Generate digest
            digest = await self.generate_digest()
            
            if digest:
                # Delete processing message
                await processing_msg.delete()
                
                # Send digest
                await update.message.reply_text(digest, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                await processing_msg.edit_text("❌ Не удалось создать дайджест. Попробуйте позже.")
                
        except Exception as e:
            logger.error(f"Error generating digest: {str(e)}")
            await update.message.reply_text("❌ Ошибка при создании дайджеста. Попробуйте позже.")
    
    async def generate_digest(self) -> str:
        """
        Generate agriculture digest
        
        Returns:
            Formatted digest string
        """
        try:
            logger.info("Starting digest generation...")
            
            # Scrape articles from all sources
            articles = self.scraper.scrape_all_sources()
            
            if not articles:
                return "📰 Сегодня статьи из источников не найдены."
            
            # Rank articles directly (OpenAI will handle filtering and selection)
            ranked_articles = await self.processor.rank_articles(articles)
            
            if not ranked_articles:
                return "🌾 Сегодня не найдено статей, связанных с сельским хозяйством."
            
            # Format digest
            digest = await self.processor.format_digest(ranked_articles)
            
            logger.info(f"Generated digest with {len(ranked_articles)} articles")
            return digest
            
        except Exception as e:
            logger.error(f"Error in generate_digest: {str(e)}")
            return None
    
    async def send_daily_digest(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily digest to channel"""
        try:
            logger.info("Sending daily digest...")
            
            # Generate digest
            digest = await self.generate_digest()
            
            if digest:
                # Send to channel
                await context.bot.send_message(
                    chat_id=self.channel_id,
                    text=digest,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("Daily digest sent successfully")
            else:
                logger.warning("Failed to generate digest for daily send")
                
        except TelegramError as e:
            logger.error(f"Telegram error sending daily digest: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending daily digest: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
    
    def setup_handlers(self):
        """Setup command handlers"""
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("digest", self.digest_command))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
    
    async def run_bot(self):
        """Run the bot"""
        if not self.application:
            self.setup_handlers()
        
        logger.info("Starting Agriculture Digest Bot...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

def main():
    """Main function to run the bot"""
    try:
        bot = AgricultureDigestBot()
        asyncio.run(bot.run_bot())
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")

if __name__ == "__main__":
    main()
