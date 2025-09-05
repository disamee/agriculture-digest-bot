"""
Test script for the Agriculture Digest Bot system
"""
import asyncio
import logging
from scraper import NewsScraper
from processor import ContentProcessor
from llm_service import LLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraper():
    """Test the scraper with your specific sources"""
    print("🔍 Testing News Scraper...")
    
    scraper = NewsScraper()
    
    # Test individual sources
    from config import NEWS_SOURCES
    
    for source in NEWS_SOURCES[:3]:  # Test first 3 sources
        print(f"\n📰 Testing {source['name']}...")
        try:
            articles = scraper.scrape_source(source)
            print(f"   Found {len(articles)} articles")
            
            if articles:
                print(f"   Sample article: {articles[0].get('title', 'No title')[:50]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Test all sources
    print(f"\n🌐 Testing all sources...")
    all_articles = scraper.scrape_all_sources()
    print(f"   Total articles found: {len(all_articles)}")
    
    return all_articles

async def test_processor(articles):
    """Test the processor with scraped articles"""
    print("\n🧠 Testing Content Processor...")
    
    processor = ContentProcessor()
    
    if not articles:
        print("   No articles to process")
        return []
    
    # Test filtering
    print("   Filtering relevant articles...")
    relevant = processor.filter_relevant_articles(articles)
    print(f"   Relevant articles: {len(relevant)}")
    
    if not relevant:
        print("   No relevant articles found")
        return []
    
    # Test ranking
    print("   Ranking articles...")
    ranked = await processor.rank_articles(relevant)
    print(f"   Ranked articles: {len(ranked)}")
    
    # Test digest generation
    print("   Generating digest...")
    digest = await processor.format_digest(ranked)
    print(f"   Digest length: {len(digest)} characters")
    
    return ranked, digest

async def test_llm_service():
    """Test the LLM service"""
    print("\n🤖 Testing LLM Service...")
    
    try:
        llm = LLMService()
        print("   LLM service initialized successfully")
        
        # Test with sample articles
        sample_articles = [
            {
                'title': 'Wheat Prices Rise Due to Drought Conditions',
                'summary': 'Global wheat prices have increased by 15% this month due to severe drought conditions in major wheat-producing regions.',
                'source': 'Fastmarkets Agriculture'
            },
            {
                'title': 'New Precision Agriculture Technology Launched',
                'summary': 'A new AI-powered precision agriculture system has been launched to help farmers optimize crop yields.',
                'source': 'APK-Inform'
            }
        ]
        
        print("   Testing article ranking...")
        ranked = await llm.rank_and_filter_articles(sample_articles)
        print(f"   Ranked {len(ranked)} articles")
        
        print("   Testing digest generation...")
        digest = await llm.generate_digest_summary(ranked)
        print(f"   Generated digest: {len(digest)} characters")
        
        return True
        
    except Exception as e:
        print(f"   LLM service error: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🌾 Agriculture Digest Bot - System Test")
    print("=" * 50)
    
    # Test LLM service first
    llm_available = await test_llm_service()
    
    # Test scraper
    articles = await test_scraper()
    
    # Test processor
    if articles:
        ranked_articles, digest = await test_processor(articles)
        
        # Show sample digest
        if digest:
            print("\n📋 Sample Digest Preview:")
            print("-" * 30)
            print(digest[:500] + "..." if len(digest) > 500 else digest)
    
    print("\n✅ System test completed!")
    
    if llm_available:
        print("🤖 LLM-powered features are available")
    else:
        print("⚠️  LLM features not available - using fallback methods")
    
    print("\n📝 Next steps:")
    print("1. Set up your .env file with API keys")
    print("2. Run 'python main.py' to start the bot")
    print("3. Test with '/digest' command in Telegram")

if __name__ == "__main__":
    asyncio.run(main())
