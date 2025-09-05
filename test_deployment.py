#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    print("🔧 Testing environment configuration...")
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHANNEL_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_imports():
    """Test all required imports"""
    print("📦 Testing imports...")
    
    try:
        import requests
        import bs4
        import feedparser
        import telethon
        import aiohttp
        from telegram_bot import AgricultureDigestBot
        from scheduler import DigestScheduler
        from processor import ContentProcessor
        from scraper import NewsScraper
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_bot_initialization():
    """Test bot initialization"""
    print("🤖 Testing bot initialization...")
    
    try:
        from telegram_bot import AgricultureDigestBot
        bot = AgricultureDigestBot()
        print("✅ Bot initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

async def test_web_server():
    """Test web server setup"""
    print("🌐 Testing web server setup...")
    
    try:
        from aiohttp import web
        
        app = web.Application()
        
        async def health_check(request):
            return web.json_response({"status": "healthy"})
        
        app.router.add_get('/health', health_check)
        print("✅ Web server setup successful")
        return True
    except Exception as e:
        print(f"❌ Web server setup error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Agriculture Digest Bot - Deployment Test")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Bot Initialization", test_bot_initialization),
        ("Web Server", test_web_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("-" * 30)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Push code to GitHub")
        print("2. Deploy to Railway")
        print("3. Test bot in Telegram")
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
