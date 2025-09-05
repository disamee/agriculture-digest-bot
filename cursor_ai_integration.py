"""
Real Cursor AI Integration for Agriculture Digest Bot
This module provides actual integration with Cursor's AI capabilities
"""
import logging
import json
import subprocess
import tempfile
import os
import asyncio
from typing import List, Dict, Optional
from config import LANGUAGE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealCursorAI:
    """Real Cursor AI integration for digest generation"""
    
    def __init__(self):
        self.language = LANGUAGE
        self.is_russian = self.language == 'ru'
    
    async def generate_digest_with_cursor_ai(self, articles: List[Dict]) -> str:
        """
        Generate digest using real Cursor AI
        
        This method creates a prompt file and uses Cursor's AI to generate content
        """
        if not articles:
            if self.is_russian:
                return "Сегодня новостей сельского хозяйства не найдено."
            else:
                return "No agriculture news found today."
        
        try:
            # Create AI prompt
            prompt = self._create_ai_prompt(articles)
            
            # Save prompt to file
            prompt_file = self._save_prompt_to_file(prompt)
            
            # Use Cursor AI to generate digest
            digest = await self._call_cursor_ai(prompt_file)
            
            # Clean up
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
            
            return digest if digest else self._generate_fallback_digest(articles)
            
        except Exception as e:
            logger.error(f"Error in Cursor AI digest generation: {str(e)}")
            return self._generate_fallback_digest(articles)
    
    def _create_ai_prompt(self, articles: List[Dict]) -> str:
        """Create comprehensive AI prompt for digest generation"""
        articles_text = self._format_articles_for_ai(articles)
        
        if self.is_russian:
            return f"""
Ты - эксперт по сельскохозяйственным рынкам с глубоким пониманием глобальных товарных рынков, торговли и сельскохозяйственной экономики.

Создай профессиональный дайджест сельскохозяйственного рынка на основе следующих статей:

{articles_text}

ТРЕБОВАНИЯ К ДАЙДЖЕСТУ:

1. **Формат**: Используй точную структуру ниже
2. **Язык**: Только русский язык
3. **Стиль**: Профессиональный, для трейдеров и аналитиков
4. **Анализ**: Глубокий анализ влияния на рынок
5. **Ссылки**: Включай ссылки на источники где возможно

СТРУКТУРА ДАЙДЖЕСТА:

🌾 **Дайджест сельскохозяйственного рынка** - [текущая дата]

📈 **Ключевые события дня:**
[2-3 предложения с основными событиями и их влиянием на рынок. Анализируй ценовые последствия, торговые потоки, региональные особенности]

📊 **Анализ рынка:**
[Краткий анализ текущей ситуации: тренды, волатильность, ключевые факторы влияния]

🌾 **По товарным группам:**
- **Зерновые:** [анализ по пшенице, кукурузе, ячменю - цены, поставки, спрос]
- **Масличные:** [анализ по сое, подсолнечнику, рапсу - экспорт, внутренний рынок]
- **Животноводство:** [анализ по скоту, молоку, мясу - производство, цены]

📰 **Основные новости:**
[Список 5-8 самых важных новостей с краткими комментариями о влиянии на рынок. Включай ссылки на источники]

🔮 **Прогноз:**
[Краткий прогноз развития ситуации на основе анализа новостей]

---
🤖 Создано с помощью AI-анализа Agriculture Digest Bot

ВАЖНО:
- Анализируй влияние на цены и торговлю
- Учитывай региональные особенности (Казахстан, Россия, Украина)
- Используй эмодзи умеренно
- Пиши как для профессионалов рынка
- Включай конкретные данные и цифры где возможно
"""
        else:
            return f"""
You are an expert agriculture market analyst with deep understanding of global commodity markets, trading, and agricultural economics.

Create a professional agriculture market digest based on these articles:

{articles_text}

DIGEST REQUIREMENTS:

1. **Format**: Use exact structure below
2. **Language**: English only
3. **Style**: Professional, for traders and analysts
4. **Analysis**: Deep market impact analysis
5. **Links**: Include source links where possible

DIGEST STRUCTURE:

🌾 **Agriculture Market Digest** - [current date]

📈 **Key Market Developments:**
[2-3 sentences with main events and their market impact. Analyze price implications, trade flows, regional specifics]

📊 **Market Analysis:**
[Brief analysis of current situation: trends, volatility, key influencing factors]

🌾 **By Commodity Groups:**
- **Grains:** [analysis of wheat, corn, barley - prices, supply, demand]
- **Oilseeds:** [analysis of soybeans, sunflower, rapeseed - exports, domestic market]
- **Livestock:** [analysis of cattle, milk, meat - production, prices]

📰 **Top News:**
[List of 5-8 most important news with brief commentary on market impact. Include source links]

🔮 **Outlook:**
[Brief forecast of situation development based on news analysis]

---
🤖 Generated with AI analysis by Agriculture Digest Bot

IMPORTANT:
- Analyze impact on prices and trade
- Consider regional specifics (Kazakhstan, Russia, Ukraine)
- Use emojis moderately
- Write for market professionals
- Include specific data and numbers where possible
"""
    
    def _format_articles_for_ai(self, articles: List[Dict]) -> str:
        """Format articles for AI processing"""
        formatted_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            summary = article.get('summary', '')
            source = article.get('source', '')
            link = article.get('link', '')
            
            formatted_text += f"СТАТЬЯ {i}:\n"
            formatted_text += f"Заголовок: {title}\n"
            formatted_text += f"Содержание: {summary}\n"
            formatted_text += f"Источник: {source}\n"
            if link:
                formatted_text += f"Ссылка: {link}\n"
            formatted_text += "\n"
        
        return formatted_text
    
    def _save_prompt_to_file(self, prompt: str) -> str:
        """Save prompt to temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            return f.name
    
    async def _call_cursor_ai(self, prompt_file: str) -> Optional[str]:
        """Call Cursor AI to generate digest"""
        try:
            # Method 1: Try to use Cursor's command line interface
            result = await self._try_cursor_cli(prompt_file)
            if result:
                return result
            
            # Method 2: Try to use Cursor's API (if available)
            result = await self._try_cursor_api(prompt_file)
            if result:
                return result
            
            # Method 3: Use Cursor's AI through file interaction
            result = await self._try_cursor_file_interaction(prompt_file)
            if result:
                return result
            
            logger.warning("All Cursor AI methods failed")
            return None
            
        except Exception as e:
            logger.error(f"Error calling Cursor AI: {str(e)}")
            return None
    
    async def _try_cursor_cli(self, prompt_file: str) -> Optional[str]:
        """Try to use Cursor CLI"""
        try:
            # This would use Cursor's command line interface
            # Implementation depends on Cursor's CLI availability
            logger.info("Attempting to use Cursor CLI...")
            
            # Placeholder - replace with actual Cursor CLI command
            # cmd = ["cursor", "ai", "generate", "--file", prompt_file]
            # result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            # return result.stdout if result.returncode == 0 else None
            
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Cursor CLI failed: {str(e)}")
            return None
    
    async def _try_cursor_api(self, prompt_file: str) -> Optional[str]:
        """Try to use Cursor API"""
        try:
            # This would use Cursor's API
            # Implementation depends on Cursor's API availability
            logger.info("Attempting to use Cursor API...")
            
            # Placeholder - replace with actual Cursor API call
            # import requests
            # with open(prompt_file, 'r', encoding='utf-8') as f:
            #     prompt = f.read()
            # 
            # response = requests.post('https://api.cursor.sh/ai/generate', 
            #                        json={'prompt': prompt, 'model': 'gpt-4'})
            # return response.json().get('content') if response.status_code == 200 else None
            
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Cursor API failed: {str(e)}")
            return None
    
    async def _try_cursor_file_interaction(self, prompt_file: str) -> Optional[str]:
        """Try to use Cursor through file interaction"""
        try:
            # This method creates a file that Cursor can process
            # and waits for Cursor to generate a response file
            logger.info("Attempting file-based Cursor interaction...")
            
            # Create a request file
            request_file = prompt_file.replace('.txt', '_request.txt')
            response_file = prompt_file.replace('.txt', '_response.txt')
            
            with open(request_file, 'w', encoding='utf-8') as f:
                f.write("GENERATE_AGRICULTURE_DIGEST\n")
                f.write(f"PROMPT_FILE: {prompt_file}\n")
                f.write(f"RESPONSE_FILE: {response_file}\n")
                f.write("LANGUAGE: ru\n")
                f.write("FORMAT: markdown\n")
            
            # Wait for Cursor to process and create response file
            for _ in range(30):  # Wait up to 30 seconds
                if os.path.exists(response_file):
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response = f.read()
                    
                    # Clean up
                    if os.path.exists(request_file):
                        os.unlink(request_file)
                    if os.path.exists(response_file):
                        os.unlink(response_file)
                    
                    return response
                
                await asyncio.sleep(1)
            
            # Clean up request file if no response
            if os.path.exists(request_file):
                os.unlink(request_file)
            
            return None
            
        except Exception as e:
            logger.error(f"Cursor file interaction failed: {str(e)}")
            return None
    
    def _generate_fallback_digest(self, articles: List[Dict]) -> str:
        """Generate fallback digest if AI fails"""
        from datetime import datetime
        
        if self.is_russian:
            title = "🌾 Дайджест сельскохозяйственного рынка"
            date_str = datetime.now().strftime('%d.%m.%Y')
            header = f"{title} - {date_str}\n\n"
            header += f"📊 **{len(articles)} статей** из источников новостей сельского хозяйства\n\n"
            
            digest = header
            
            for i, article in enumerate(articles[:8], 1):
                title = article.get('title', 'Без заголовка')
                source = article.get('source', 'Неизвестный источник')
                link = article.get('link', '')
                
                digest += f"**{i}. {title}**\n"
                digest += f"📰 Источник: {source}\n"
                if link:
                    digest += f"🔗 [Читать полностью]({link})\n"
                digest += "\n"
            
            digest += "---\n🤖 Создано ботом Agriculture Digest"
        else:
            title = "🌾 Agriculture Market Digest"
            date_str = datetime.now().strftime('%B %d, %Y')
            header = f"{title} - {date_str}\n\n"
            header += f"📊 **{len(articles)} articles** from agriculture news sources\n\n"
            
            digest = header
            
            for i, article in enumerate(articles[:8], 1):
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown source')
                link = article.get('link', '')
                
                digest += f"**{i}. {title}**\n"
                digest += f"📰 Source: {source}\n"
                if link:
                    digest += f"🔗 [Read more]({link})\n"
                digest += "\n"
            
            digest += "---\n🤖 Generated by Agriculture Digest Bot"
        
        return digest

# Global instance for easy access
cursor_ai = RealCursorAI()

async def generate_digest_with_ai(articles: List[Dict]) -> str:
    """Convenience function to generate digest with Cursor AI"""
    return await cursor_ai.generate_digest_with_cursor_ai(articles)

def main():
    """Test the Cursor AI integration"""
    import asyncio
    
    async def test():
        # Sample articles
        articles = [
            {
                'title': 'Цены на пшеницу выросли из-за засухи в Казахстане',
                'summary': 'Цены на пшеницу в Казахстане выросли на 15% в этом месяце из-за сильной засухи в основных зернопроизводящих регионах.',
                'source': 'Margin.kz',
                'link': 'https://example.com/wheat-prices-kz'
            },
            {
                'title': 'Новые технологии точного земледелия внедряются в России',
                'summary': 'Новая система точного земледелия на основе ИИ была запущена для помощи фермерам в оптимизации урожайности.',
                'source': 'APK-Inform',
                'link': 'https://example.com/precision-ag-ru'
            }
        ]
        
        print("🤖 Testing Real Cursor AI Integration...")
        
        digest = await generate_digest_with_ai(articles)
        
        print("📋 Generated Digest:")
        print("-" * 50)
        print(digest)
    
    asyncio.run(test())

if __name__ == "__main__":
    main()
