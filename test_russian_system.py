"""
Test script for the Russian Agriculture Digest Bot system
"""
import asyncio
import logging
from scraper import NewsScraper
from processor import ContentProcessor
from llm_service import LLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_russian_digest():
    """Test the system with Russian language support"""
    print("🌾 Тестирование системы Agriculture Digest Bot на русском языке")
    print("=" * 60)
    
    # Test LLM service
    print("\n🤖 Тестирование AI сервиса...")
    try:
        llm = LLMService()
        print("   ✅ AI сервис инициализирован успешно")
        print(f"   📝 Язык: {'Русский' if llm.is_russian else 'English'}")
    except Exception as e:
        print(f"   ❌ Ошибка AI сервиса: {str(e)}")
    
    # Test processor
    print("\n🧠 Тестирование процессора контента...")
    try:
        processor = ContentProcessor()
        print("   ✅ Процессор инициализирован успешно")
        print(f"   📝 Язык: {'Русский' if processor.is_russian else 'English'}")
    except Exception as e:
        print(f"   ❌ Ошибка процессора: {str(e)}")
    
    # Sample articles for testing
    sample_articles = [
        {
            'title': 'Цены на пшеницу выросли из-за засухи в Казахстане',
            'summary': 'Цены на пшеницу в Казахстане выросли на 15% в этом месяце из-за сильной засухи в основных зернопроизводящих регионах.',
            'link': 'https://example.com/wheat-prices-kz',
            'source': 'Margin.kz'
        },
        {
            'title': 'Новые технологии точного земледелия внедряются в России',
            'summary': 'Новая система точного земледелия на основе ИИ была запущена для помощи фермерам в оптимизации урожайности.',
            'link': 'https://example.com/precision-ag-ru',
            'source': 'APK-Inform'
        },
        {
            'title': 'Экспорт зерна из России увеличился на 20%',
            'summary': 'Экспорт зерновых культур из России в текущем сезоне увеличился на 20% по сравнению с прошлым годом.',
            'link': 'https://example.com/grain-export-ru',
            'source': 'Fastmarkets Agriculture'
        }
    ]
    
    print(f"\n📰 Тестирование с {len(sample_articles)} образцами статей...")
    
    # Test filtering
    print("   🔍 Фильтрация релевантных статей...")
    relevant = processor.filter_relevant_articles(sample_articles)
    print(f"   ✅ Найдено {len(relevant)} релевантных статей")
    
    if not relevant:
        print("   ⚠️  Нет релевантных статей для тестирования")
        return
    
    # Test ranking
    print("   📊 Ранжирование статей...")
    ranked = await processor.rank_articles(relevant)
    print(f"   ✅ Отранжировано {len(ranked)} статей")
    
    # Test digest generation
    print("   📋 Генерация дайджеста...")
    digest = await processor.format_digest(ranked)
    print(f"   ✅ Дайджест сгенерирован ({len(digest)} символов)")
    
    # Show sample digest
    print("\n📋 Пример дайджеста:")
    print("-" * 50)
    print(digest[:800] + "..." if len(digest) > 800 else digest)
    
    # Test categorization
    print("\n🏷️  Тестирование категоризации...")
    categories = await processor.group_articles_by_topic(ranked)
    print(f"   ✅ Создано {len(categories)} категорий:")
    for category, articles in categories.items():
        print(f"      • {category}: {len(articles)} статей")
    
    print("\n✅ Тестирование завершено успешно!")
    
    # Show configuration
    print("\n⚙️  Конфигурация:")
    print(f"   🌐 Язык: {processor.language}")
    print(f"   🤖 AI включен: {processor.use_llm}")
    print(f"   📊 Максимум статей: {len(ranked)}")
    print(f"   🔗 Ссылки включены: {processor.llm_service.use_cursor_ai}")

async def test_scraper_sources():
    """Test scraping from your specific sources"""
    print("\n🔍 Тестирование скрапинга источников...")
    
    scraper = NewsScraper()
    
    # Test a few sources
    from config import NEWS_SOURCES
    
    for source in NEWS_SOURCES[:2]:  # Test first 2 sources
        print(f"\n📰 Тестирование {source['name']}...")
        try:
            articles = scraper.scrape_source(source)
            print(f"   ✅ Найдено {len(articles)} статей")
            
            if articles:
                print(f"   📝 Пример: {articles[0].get('title', 'Без заголовка')[:50]}...")
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Запуск тестирования системы Agriculture Digest Bot")
    
    # Test Russian digest generation
    asyncio.run(test_russian_digest())
    
    # Test scraping (optional, can be slow)
    # asyncio.run(test_scraper_sources())
    
    print("\n📝 Следующие шаги:")
    print("1. Настройте файл .env с токеном бота")
    print("2. Запустите 'python main.py' для старта бота")
    print("3. Протестируйте командой '/digest' в Telegram")

if __name__ == "__main__":
    main()
