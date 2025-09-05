"""
Configuration file for Agriculture Digest Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '@agriculture_digest')

# LLM Configuration
USE_CURSOR_AI = os.getenv('USE_CURSOR_AI', 'false').lower() == 'true'
USE_OPENAI = os.getenv('USE_OPENAI', 'true').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGUAGE = os.getenv('LANGUAGE', 'ru')  # 'ru' for Russian, 'en' for English

# News Sources Configuration
NEWS_SOURCES = [
    {
        'name': 'Fastmarkets Agriculture',
        'url': 'https://www.fastmarkets.com/agriculture/grains-and-oilseeds/',
        'type': 'scrape',
        'selectors': {
            'title': 'h2, h3, .article-title, .headline',
            'link': 'a[href*="/news/"], a[href*="/analysis/"]',
            'summary': 'p, .article-summary, .excerpt'
        }
    },
    {
        'name': 'Margin.kz',
        'url': 'https://margin.kz/',
        'type': 'scrape',
        'selectors': {
            'title': 'h1, h2, h3, .title, .headline',
            'link': 'a[href*="/news/"], a[href*="/article/"]',
            'summary': 'p, .summary, .excerpt, .description'
        }
    },
    {
        'name': 'APK-Inform',
        'url': 'https://www.apk-inform.com/ru/news',
        'type': 'scrape',
        'selectors': {
            'title': 'h1, h2, h3, .news-title, .article-title',
            'link': 'a[href*="/news/"], a[href*="/ru/news/"]',
            'summary': 'p, .news-summary, .article-summary'
        }
    },
    {
        'name': 'APK News Kazakhstan',
        'url': 'https://apk-news.kz/',
        'type': 'scrape',
        'selectors': {
            'title': 'h1, h2, h3, .title, .headline',
            'link': 'a[href*="/news/"], a[href*="/article/"]',
            'summary': 'p, .summary, .excerpt'
        }
    },
    {
        'name': 'Eldala.kz',
        'url': 'https://eldala.kz/',
        'type': 'scrape',
        'selectors': {
            'title': 'h1, h2, h3, .title, .headline',
            'link': 'a[href*="/news/"], a[href*="/article/"]',
            'summary': 'p, .summary, .excerpt, .description'
        }
    },
    {
        'name': 'Andre Sizov Telegram',
        'url': 'https://t.me/andre_sizov',
        'type': 'telegram',
        'channel_username': 'andre_sizov',
        'max_posts': 10
    },
    {
        'name': 'AMIS Outlook',
        'url': 'https://www.amis-outlook.org/home',
        'type': 'scrape',
        'selectors': {
            'title': 'h1, h2, h3, .title, .headline',
            'link': 'a[href*="/news/"], a[href*="/article/"]',
            'summary': 'p, .summary, .excerpt, .description'
        }
    }
]

# Digest Configuration
DIGEST_CONFIG = {
    'max_articles_per_source': 10,
    'max_total_articles': 8,
    'digest_schedule': '08:00',  # Daily at 8 AM
    'timezone': 'UTC',
    'summary_length': 200,  # characters
    'include_source_links': True,
    'language': LANGUAGE,
    'digest_title_ru': '🌾 Дайджест сельскохозяйственного рынка',
    'digest_title_en': '🌾 Agriculture Market Digest'
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'request_timeout': 30,
    'user_agent': 'Agriculture Digest Bot 1.0',
    'delay_between_requests': 2,  # seconds
    'max_retries': 3
}
