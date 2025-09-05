#!/usr/bin/env python3
"""
Test script for web server functionality
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_web_server():
    """Test the web server endpoints"""
    print("🧪 Testing web server functionality...")
    
    # Test local web server
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get('http://localhost:8080/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Health endpoint working")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Bot token configured: {data.get('bot_token_configured')}")
                    print(f"   Channel configured: {data.get('channel_configured')}")
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
            
            # Test root endpoint
            async with session.get('http://localhost:8080/') as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Root endpoint working")
                    print(f"   Message: {data.get('message')}")
                else:
                    print(f"❌ Root endpoint failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 Web Server Test")
    print("=" * 30)
    
    # Check environment variables
    print("🔧 Environment check:")
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    print(f"   Bot token: {'✅ Set' if bot_token else '❌ Missing'}")
    print(f"   Channel ID: {'✅ Set' if channel_id else '❌ Missing'}")
    print(f"   Port: {os.getenv('PORT', '8080')}")
    
    print("\n🌐 Web server test:")
    success = await test_web_server()
    
    if success:
        print("\n🎉 Web server test passed!")
    else:
        print("\n⚠️ Web server test failed!")

if __name__ == "__main__":
    asyncio.run(main())
