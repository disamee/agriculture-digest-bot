# 🚀 Railway Deployment Guide

## Deploy Agriculture Digest Bot to Railway

### Prerequisites
- Railway account (free tier available)
- GitHub repository with your bot code
- Telegram bot token (already configured)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

### Step 2: Deploy to Railway

1. **Go to Railway.app** and sign in with GitHub
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your repository** (`agriculture digest`)
4. **Railway will automatically detect** the Python project

### Step 3: Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab and add:

```
TELEGRAM_BOT_TOKEN=8087636672:AAFlXUS3BEjUxVzQMFzZjnYRzEyNa8wXWLQ
TELEGRAM_CHANNEL_ID=@st_grain_digest_bot
LANGUAGE=ru
USE_CURSOR_AI=true
PORT=8080
```

### Step 4: Deploy

1. **Click "Deploy"** - Railway will automatically:
   - Install Python dependencies from `requirements.txt`
   - Start the bot using `python main.py`
   - Expose health check endpoint at `/health`

### Step 5: Verify Deployment

1. **Check the logs** in Railway dashboard
2. **Test the health endpoint:** `https://your-app.railway.app/health`
3. **Test your bot** in Telegram with `/start` and `/digest`

### Railway Configuration Files

- **`railway.json`** - Railway deployment configuration
- **`Procfile`** - Process definition
- **`runtime.txt`** - Python version specification
- **`requirements.txt`** - Python dependencies

### Monitoring

- **Logs:** Available in Railway dashboard
- **Health checks:** Automatic monitoring via `/health` endpoint
- **Restart policy:** Automatic restart on failure

### Cost

- **Free tier:** 500 hours/month
- **Hobby plan:** $5/month for unlimited usage

### Troubleshooting

1. **Bot not responding:**
   - Check logs in Railway dashboard
   - Verify environment variables are set
   - Ensure bot token is correct

2. **Health check failing:**
   - Check if port 8080 is accessible
   - Verify web server is starting correctly

3. **Dependencies issues:**
   - Check `requirements.txt` is complete
   - Verify Python version in `runtime.txt`

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather | Yes |
| `TELEGRAM_CHANNEL_ID` | Your channel username | Yes |
| `LANGUAGE` | Language for digest (ru/en) | No (default: ru) |
| `USE_CURSOR_AI` | Enable AI processing | No (default: true) |
| `PORT` | Web server port | No (default: 8080) |

### Next Steps

1. **Set up webhook** (optional) for better performance
2. **Configure custom domain** (optional)
3. **Set up monitoring** and alerts
4. **Scale resources** as needed

Your bot will now run 24/7 on Railway! 🎉
