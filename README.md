# Agriculture Digest Bot

A Telegram bot that automatically scrapes agriculture market news from multiple sources and generates daily digests for subscribers.

## Features

- 🌾 **Automated News Scraping**: Monitors multiple agriculture news sources
- 🤖 **Real AI-Powered Processing**: Uses Cursor AI for intelligent article ranking and digest generation
- 🇷🇺 **Russian Language Support**: Generates digests in Russian with localized content
- 📊 **Smart Filtering**: Filters articles for agriculture relevance
- 🏷️ **Topic Organization**: Groups articles by categories (Зерновые, Животноводство, Технологии, etc.)
- 📱 **Telegram Integration**: Sends formatted digests to Telegram channels
- ⏰ **Scheduled Delivery**: Daily automated digest delivery
- 🔗 **Source Links**: Includes direct links to full articles
- 📈 **Intelligent Ranking**: Real AI-powered article prioritization based on market impact
- 🧠 **Advanced Summarization**: AI-generated summaries with market insights and analysis

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │───▶│   Web Scraper   │───▶│   Processor     │
│                 │    │                 │    │                 │
│ • Fastmarkets   │    │ • RSS Feeds     │    │ • Filtering     │
│ • Margin.kz     │    │ • HTML Scraping │    │ • AI Ranking    │
│ • APK-Inform    │    │ • Telegram      │    │ • AI Summaries  │
│ • Andre Sizov   │    │ • Error Handling│    │ • Categorization│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   LLM Service   │◀───│   OpenAI GPT-4o │              │
│                 │    │                 │              │
│ • Article Rank  │    │ • Market Analysis│             │
│ • Summarization │    │ • Digest Gen    │              │
│ • Categorization│    │ • Intelligence  │              │
└─────────────────┘    └─────────────────┘              │
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   Telegram Bot  │◀───│   Scheduler     │◀─────────────┘
│                 │    │                 │
│ • Commands      │    │ • Daily Timer   │
│ • Channel Posts │    │ • Error Recovery│
│ • User Interface│    │ • Logging       │
└─────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram Channel (optional, for automated posting)
- Cursor IDE (for AI-powered features)

### Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**:
   ```bash
   cp env_example.txt .env
   ```

4. **Configure your bot**:
   Edit `.env` file with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHANNEL_ID=@your_channel_username
   LANGUAGE=ru
   USE_CURSOR_AI=true
   ```

5. **Customize news sources** (optional):
   Edit `config.py` to add or modify news sources.

## Usage

### Running the Bot

**Option 1: Full Application (Recommended)**
```bash
python main.py
```
This runs both the Telegram bot and the scheduler for automated digests.

**Option 2: Bot Only**
```bash
python telegram_bot.py
```
This runs only the Telegram bot without automated scheduling.

**Option 3: Test Scraper**
```bash
python scraper.py
```
This tests the web scraping functionality.

**Option 4: Test Processor**
```bash
python processor.py
```
This tests the content processing and digest formatting.

**Option 5: Test System**
```bash
python test_system.py
```
This tests the complete system including AI integration.

**Option 6: Test Russian System**
```bash
python test_russian_system.py
```
This tests the system with Russian language support.

**Option 7: Test Cursor AI Integration**
```bash
python test_cursor_ai.py
```
This tests the real Cursor AI integration for digest generation.

### Bot Commands

- `/start` - Welcome message and bot introduction
- `/digest` - Manually generate and send current digest
- `/help` - Show help information
- `/status` - Show bot status and configuration

### Setting Up a Telegram Channel

1. Create a new Telegram channel
2. Add your bot as an administrator
3. Get the channel username (e.g., `@agriculture_digest`)
4. Update `TELEGRAM_CHANNEL_ID` in your `.env` file

## Configuration

### News Sources

Edit `config.py` to customize news sources:

```python
NEWS_SOURCES = [
    {
        'name': 'Your Source Name',
        'url': 'https://example.com/news',
        'type': 'scrape',  # or 'rss'
        'rss_url': 'https://example.com/rss.xml',  # for RSS sources
        'selectors': {
            'title': 'h2.article-title',
            'link': 'a.article-link',
            'summary': 'div.article-summary'
        }
    }
]
```

### Digest Settings

```python
DIGEST_CONFIG = {
    'max_articles_per_source': 5,
    'max_total_articles': 15,
    'digest_schedule': '08:00',  # Daily at 8 AM
    'timezone': 'UTC',
    'summary_length': 200,
    'include_source_links': True
}
```

## Adding Custom News Sources

### Method 1: RSS Feeds (Recommended)

If a website provides RSS feeds:

```python
{
    'name': 'Source Name',
    'url': 'https://example.com',
    'type': 'rss',
    'rss_url': 'https://example.com/rss.xml'
}
```

### Method 2: HTML Scraping

For websites without RSS:

```python
{
    'name': 'Source Name',
    'url': 'https://example.com/news',
    'type': 'scrape',
    'selectors': {
        'title': 'h2.article-title',      # CSS selector for article titles
        'link': 'a.article-link',         # CSS selector for article links
        'summary': 'div.article-summary'  # CSS selector for summaries
    }
}
```

## Deployment

### Local Development

1. Run the bot locally for testing
2. Use `/digest` command to test functionality
3. Check logs for any errors

### Production Deployment

**Option 1: VPS/Server**
1. Set up a Linux server (Ubuntu recommended)
2. Install Python and dependencies
3. Use `systemd` or `supervisor` to run the bot as a service
4. Set up log rotation

**Option 2: Cloud Platforms**
- **Heroku**: Use Procfile and environment variables
- **DigitalOcean App Platform**: Deploy as Python app
- **AWS EC2**: Set up EC2 instance with auto-scaling

**Option 3: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Monitoring

- Check logs regularly for errors
- Monitor bot uptime
- Verify digest delivery
- Test news source availability

## Troubleshooting

### Common Issues

**Bot not responding:**
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Verify bot is added to channel as admin
- Check internet connection

**No articles found:**
- Verify news source URLs are accessible
- Check if website structure changed
- Test individual sources with `scraper.py`

**Digest not sending:**
- Check scheduler configuration
- Verify channel ID format
- Check bot permissions in channel

**Scraping errors:**
- Some websites may block automated requests
- Add delays between requests
- Use different User-Agent strings
- Consider using proxy services

### Logs

The bot logs important events. Check logs for:
- Scraping errors
- Telegram API errors
- Scheduler issues
- Content processing problems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components
4. Create an issue with detailed information

## Future Enhancements

- [ ] Machine learning for better article ranking
- [ ] Multiple language support
- [ ] Custom user preferences
- [ ] Web dashboard for configuration
- [ ] Email digest option
- [ ] Social media integration
- [ ] Advanced analytics and reporting
