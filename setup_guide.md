# Agriculture Digest Bot - Setup Guide

This guide will walk you through setting up your Agriculture Digest Bot step by step.

## Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send `/newbot`** command
4. **Choose a name** for your bot (e.g., "Agriculture Digest Bot")
5. **Choose a username** (e.g., "agriculture_digest_bot")
6. **Save the token** that BotFather gives you (you'll need this later)

## Step 2: Create a Telegram Channel (Optional)

1. **Open Telegram** and click "New Channel"
2. **Choose a name** (e.g., "Agriculture Market Digest")
3. **Choose a username** (e.g., "agriculture_digest")
4. **Add your bot** as an administrator:
   - Go to channel settings
   - Click "Administrators"
   - Click "Add Admin"
   - Search for your bot username
   - Give it permission to "Post Messages"

## Step 3: Install Python Dependencies

Make sure you have Python 3.8+ installed, then run:

```bash
pip install -r requirements.txt
```

## Step 4: Configure the Bot

1. **Copy the environment file**:
   ```bash
   cp env_example.txt .env
   ```

2. **Edit the `.env` file** with your bot token and channel:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHANNEL_ID=@agriculture_digest
   ```

## Step 5: Test the Bot

1. **Run the bot**:
   ```bash
   python main.py
   ```

2. **Test manually**:
   - Find your bot on Telegram
   - Send `/start` command
   - Send `/digest` command to generate a test digest

## Step 6: Add Your News Sources

Edit `config.py` to add your agriculture news sources:

```python
NEWS_SOURCES = [
    {
        'name': 'Your Agriculture News Site',
        'url': 'https://your-agriculture-site.com/news',
        'type': 'scrape',  # or 'rss' if they have RSS
        'selectors': {
            'title': 'h2.article-title',
            'link': 'a.article-link',
            'summary': 'div.article-summary'
        }
    }
]
```

### Finding CSS Selectors

To find the right CSS selectors for a website:

1. **Open the website** in your browser
2. **Right-click** on an article title
3. **Select "Inspect Element"**
4. **Look for the HTML structure**:
   ```html
   <h2 class="article-title">Article Title</h2>
   <a href="/article-link" class="article-link">Read More</a>
   <div class="article-summary">Summary text...</div>
   ```
5. **Use the class names** as selectors

## Step 7: Customize Settings

Edit `config.py` to customize:

- **Digest schedule**: Change `digest_schedule` to your preferred time
- **Article limits**: Adjust `max_articles_per_source` and `max_total_articles`
- **Summary length**: Modify `summary_length`
- **Timezone**: Change `timezone` to your local timezone

## Step 8: Deploy (Production)

### Option A: Local Server

1. **Set up a VPS** (DigitalOcean, AWS, etc.)
2. **Install Python** and dependencies
3. **Upload your bot files**
4. **Run with screen/tmux**:
   ```bash
   screen -S agriculture-bot
   python main.py
   # Press Ctrl+A, then D to detach
   ```

### Option B: Cloud Platform

**Heroku:**
1. Create `Procfile`:
   ```
   worker: python main.py
   ```
2. Deploy with Heroku CLI

**Docker:**
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

## Step 9: Monitor and Maintain

1. **Check logs** regularly for errors
2. **Test the bot** weekly with `/digest` command
3. **Update news sources** if websites change
4. **Monitor bot uptime**

## Troubleshooting

### Bot Not Responding
- Check if token is correct
- Verify bot is added to channel as admin
- Check internet connection

### No Articles Found
- Test individual sources: `python scraper.py`
- Check if website structure changed
- Verify URLs are accessible

### Digest Not Sending
- Check channel ID format (should start with @)
- Verify bot permissions in channel
- Check scheduler configuration

## Example News Sources

Here are some popular agriculture news sources you can add:

```python
NEWS_SOURCES = [
    {
        'name': 'USDA News',
        'url': 'https://www.usda.gov/news',
        'type': 'rss',
        'rss_url': 'https://www.usda.gov/rss/news.xml'
    },
    {
        'name': 'AgWeb',
        'url': 'https://www.agweb.com/news',
        'type': 'scrape',
        'selectors': {
            'title': 'h3.article-title',
            'link': 'a.article-link',
            'summary': 'p.article-excerpt'
        }
    },
    {
        'name': 'Farm Progress',
        'url': 'https://www.farmprogress.com/news',
        'type': 'scrape',
        'selectors': {
            'title': 'h2.headline',
            'link': 'a.headline-link',
            'summary': 'div.article-summary'
        }
    }
]
```

## Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Test components individually**:
   - `python scraper.py` - Test scraping
   - `python processor.py` - Test processing
   - `python telegram_bot.py` - Test bot only
3. **Verify configuration** in `config.py`
4. **Check environment variables** in `.env`

## Next Steps

Once your bot is running:

1. **Share your channel** with agriculture professionals
2. **Monitor performance** and adjust settings
3. **Add more news sources** as needed
4. **Consider adding features** like user preferences or analytics

Your Agriculture Digest Bot is now ready to provide daily agriculture market insights!
