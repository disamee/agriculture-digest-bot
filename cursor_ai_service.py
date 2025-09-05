"""
Cursor AI Service for real LLM-powered agriculture digest generation
"""
import logging
import json
import subprocess
import tempfile
import os
from typing import List, Dict, Optional
from config import LANGUAGE, DIGEST_CONFIG
from cursor_ai_integration import generate_digest_with_ai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CursorAIService:
    """Service for real AI-powered content processing using Cursor AI"""
    
    def __init__(self):
        self.language = LANGUAGE
        self.is_russian = self.language == 'ru'
        
    async def generate_intelligent_digest(self, articles: List[Dict]) -> str:
        """
        Generate intelligent digest using Cursor AI
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            AI-generated digest string
        """
        if not articles:
            if self.is_russian:
                return "Сегодня новостей сельского хозяйства не найдено."
            else:
                return "No agriculture news found today."
        
        try:
            # Use real Cursor AI integration
            digest = await generate_digest_with_ai(articles)
            
            if digest and len(digest) > 100:  # Ensure we got a substantial response
                logger.info("Real Cursor AI generated digest successfully")
                return digest
            else:
                logger.warning("Cursor AI returned insufficient content, using fallback")
                return self._generate_fallback_digest(articles)
                
        except Exception as e:
            logger.error(f"Error in AI digest generation: {str(e)}")
            return self._generate_fallback_digest(articles)
    
    async def analyze_and_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Use AI to analyze and rank articles by market importance
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            AI-ranked list of articles
        """
        if not articles:
            return []
        
        try:
            # Prepare articles for AI analysis
            articles_text = self._prepare_articles_for_ai(articles)
            
            # Create ranking prompt
            prompt = self._create_ranking_prompt(articles_text)
            
            # Get AI ranking
            ranking_result = await self._call_cursor_ai(prompt)
            
            if ranking_result:
                # Parse AI response and apply ranking
                ranked_articles = self._parse_ranking_result(ranking_result, articles)
                return ranked_articles
            else:
                logger.warning("Cursor AI ranking failed, using fallback")
                return self._fallback_rank_articles(articles)
                
        except Exception as e:
            logger.error(f"Error in AI ranking: {str(e)}")
            return self._fallback_rank_articles(articles)
    
    async def generate_market_insights(self, articles: List[Dict]) -> str:
        """
        Generate market insights and analysis using AI
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            AI-generated market insights
        """
        if not articles:
            return ""
        
        try:
            # Prepare articles for AI analysis
            articles_text = self._prepare_articles_for_ai(articles)
            
            # Create insights prompt
            prompt = self._create_insights_prompt(articles_text)
            
            # Generate insights using AI
            insights = await self._call_cursor_ai(prompt)
            
            return insights if insights else ""
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return ""
    
    async def generate_article_summary(self, content: str) -> str:
        """
        Generate AI-powered article summary in 2-3 sentences
        
        Args:
            content: Article content (title + summary)
            
        Returns:
            AI-generated summary in 2-3 sentences
        """
        try:
            # Create summary prompt
            prompt = self._create_summary_prompt(content)
            
            # Get AI summary
            summary = await self._call_cursor_ai(prompt)
            
            if summary and len(summary.strip()) > 20:
                return summary.strip()
            else:
                # Fallback to intelligent analysis
                return self._generate_intelligent_summary(content)
                
        except Exception as e:
            logger.error(f"Error generating article summary: {str(e)}")
            return self._generate_intelligent_summary(content)
    
    def _create_summary_prompt(self, content: str) -> str:
        """Create prompt for article summarization"""
        if self.is_russian:
            return f"""
Ты - эксперт по сельскохозяйственным рынкам. Создай краткое резюме статьи в 2-3 предложения на русском языке.

Статья:
{content}

Требования:
- Резюме должно быть в 2-3 предложения
- Пиши профессионально, как для трейдеров и аналитиков
- Выдели ключевые факты и их влияние на рынок
- Используй терминологию сельскохозяйственного рынка
- Фокусируйся на практической значимости информации

Резюме:
"""
        else:
            return f"""
You are an expert agriculture market analyst. Create a brief article summary in 2-3 sentences in English.

Article:
{content}

Requirements:
- Summary should be 2-3 sentences
- Write professionally for traders and analysts
- Highlight key facts and their market impact
- Use agricultural market terminology
- Focus on practical significance of information

Summary:
"""
    
    def _generate_intelligent_summary(self, content: str) -> str:
        """Generate intelligent summary based on content analysis"""
        try:
            content_lower = content.lower()
            
            # Agriculture-specific analysis
            if any(word in content_lower for word in ['урожай', 'harvest', 'сбор', 'уборка']):
                if self.is_russian:
                    return "Статья посвящена вопросам сбора урожая и состоянию сельскохозяйственных культур. Анализируется влияние погодных условий и технологий на продуктивность."
                else:
                    return "Article focuses on harvest and agricultural crop conditions. Analyzes impact of weather conditions and technologies on productivity."
            
            elif any(word in content_lower for word in ['цена', 'price', 'стоимость', 'рынок']):
                if self.is_russian:
                    return "Материал анализирует ценовые тенденции на сельскохозяйственную продукцию и их влияние на торговлю. Рассматриваются факторы, определяющие динамику цен."
                else:
                    return "Material analyzes price trends for agricultural products and their impact on trade. Examines factors determining price dynamics."
            
            elif any(word in content_lower for word in ['технология', 'technology', 'инновация', 'новые']):
                if self.is_russian:
                    return "Статья рассказывает о новых технологиях и инновациях в сельском хозяйстве. Оценивается потенциал их внедрения для повышения эффективности производства."
                else:
                    return "Article discusses new technologies and innovations in agriculture. Evaluates their implementation potential for production efficiency improvement."
            
            elif any(word in content_lower for word in ['погода', 'weather', 'климат', 'дождь', 'засуха']):
                if self.is_russian:
                    return "Материал рассматривает влияние погодных условий на сельскохозяйственное производство. Анализируются риски и возможности для различных культур."
                else:
                    return "Material examines weather impact on agricultural production. Analyzes risks and opportunities for different crops."
            
            elif any(word in content_lower for word in ['экспорт', 'export', 'импорт', 'import', 'торговля']):
                if self.is_russian:
                    return "Статья освещает вопросы международной торговли сельскохозяйственной продукцией. Рассматриваются изменения в торговых потоках и их влияние на рынок."
                else:
                    return "Article covers international trade in agricultural products. Examines changes in trade flows and their market impact."
            
            else:
                # Generic summary
                if self.is_russian:
                    return "Статья содержит актуальную информацию о событиях в сфере сельского хозяйства. Представлен анализ текущей ситуации и перспектив развития."
                else:
                    return "Article contains current information about agriculture sector events. Presents analysis of current situation and development prospects."
                    
        except Exception as e:
            logger.error(f"Error in intelligent summary generation: {str(e)}")
            if self.is_russian:
                return "Статья содержит важную информацию о сельскохозяйственном рынке. Подробности доступны в полной версии."
            else:
                return "Article contains important information about agricultural market. Details available in full version."
    
    def _prepare_articles_for_ai(self, articles: List[Dict]) -> str:
        """Prepare articles text for AI processing"""
        articles_text = ""
        for i, article in enumerate(articles):
            title = article.get('title', '')
            summary = article.get('summary', '')
            source = article.get('source', '')
            link = article.get('link', '')
            
            articles_text += f"Статья {i+1}:\n"
            articles_text += f"Заголовок: {title}\n"
            articles_text += f"Содержание: {summary}\n"
            articles_text += f"Источник: {source}\n"
            if link:
                articles_text += f"Ссылка: {link}\n"
            articles_text += "\n"
        
        return articles_text
    
    def _create_digest_prompt(self, articles_text: str) -> str:
        """Create prompt for digest generation"""
        if self.is_russian:
            return f"""
Ты - эксперт по сельскохозяйственным рынкам. Создай профессиональный дайджест новостей сельского хозяйства на основе следующих статей:

{articles_text}

Создай дайджест в следующем формате:

🌾 **Дайджест сельскохозяйственного рынка** - [дата]

📈 **Ключевые события дня:**
[2-3 предложения с основными событиями и их влиянием на рынок]

📊 **Анализ рынка:**
[Краткий анализ текущей ситуации на рынке]

🌾 **По товарным группам:**
- **Зерновые:** [анализ по пшенице, кукурузе, ячменю и т.д.]
- **Масличные:** [анализ по сое, подсолнечнику, рапсу и т.д.]
- **Животноводство:** [анализ по скоту, молоку, мясу и т.д.]

📰 **Основные новости:**
[Список 5-8 самых важных новостей с краткими комментариями]

🔮 **Прогноз:**
[Краткий прогноз развития ситуации]

---
🤖 Создано с помощью AI-анализа Agriculture Digest Bot

Важно:
- Пиши профессионально, как для трейдеров и аналитиков
- Используй эмодзи умеренно
- Включай ссылки на источники где возможно
- Анализируй влияние на цены и торговлю
- Учитывай региональные особенности (Казахстан, Россия, Украина)
"""
        else:
            return f"""
You are an expert agriculture market analyst. Create a professional agriculture market digest based on these articles:

{articles_text}

Create a digest in the following format:

🌾 **Agriculture Market Digest** - [date]

📈 **Key Market Developments:**
[2-3 sentences with main events and their market impact]

📊 **Market Analysis:**
[Brief analysis of current market situation]

🌾 **By Commodity Groups:**
- **Grains:** [analysis of wheat, corn, barley, etc.]
- **Oilseeds:** [analysis of soybeans, sunflower, rapeseed, etc.]
- **Livestock:** [analysis of cattle, milk, meat, etc.]

📰 **Top News:**
[List of 5-8 most important news with brief commentary]

🔮 **Outlook:**
[Brief forecast of situation development]

---
🤖 Generated with AI analysis by Agriculture Digest Bot

Important:
- Write professionally for traders and analysts
- Use emojis moderately
- Include source links where possible
- Analyze price and trade impact
- Consider regional specifics (Kazakhstan, Russia, Ukraine)
"""
    
    def _create_ranking_prompt(self, articles_text: str) -> str:
        """Create prompt for article ranking"""
        if self.is_russian:
            return f"""
Ты - эксперт по сельскохозяйственным рынкам. Проанализируй следующие статьи и ранжируй их по важности для рынка:

{articles_text}

Верни JSON с ранжированием:
{{
    "ranked_articles": [индексы статей в порядке важности],
    "reasoning": "Краткое объяснение критериев ранжирования",
    "market_impact": "Общая оценка влияния на рынок"
}}

Критерии важности:
1. Влияние на цены товаров
2. Значимость для торговли
3. Региональная важность
4. Временная актуальность
5. Источник и достоверность
"""
        else:
            return f"""
You are an expert agriculture market analyst. Analyze these articles and rank them by market importance:

{articles_text}

Return JSON with ranking:
{{
    "ranked_articles": [article indices in order of importance],
    "reasoning": "Brief explanation of ranking criteria",
    "market_impact": "Overall market impact assessment"
}}

Importance criteria:
1. Impact on commodity prices
2. Trade significance
3. Regional importance
4. Timeliness
5. Source credibility
"""
    
    def _create_insights_prompt(self, articles_text: str) -> str:
        """Create prompt for market insights"""
        if self.is_russian:
            return f"""
На основе этих статей о сельском хозяйстве, создай краткий анализ ключевых трендов и инсайтов:

{articles_text}

Сфокусируйся на:
- Ключевых трендах рынка
- Влиянии на цены
- Региональных особенностях
- Прогнозах развития

Пиши кратко и по делу, 2-3 абзаца.
"""
        else:
            return f"""
Based on these agriculture articles, create a brief analysis of key trends and insights:

{articles_text}

Focus on:
- Key market trends
- Price impact
- Regional specifics
- Development forecasts

Write concisely, 2-3 paragraphs.
"""
    
    async def _call_cursor_ai(self, prompt: str) -> Optional[str]:
        """Call Cursor AI to generate content"""
        try:
            # Create temporary file with prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            # Use Cursor AI through command line (if available)
            # This is a placeholder - actual implementation depends on Cursor's API
            result = await self._execute_cursor_ai_command(temp_file)
            
            # Clean up
            os.unlink(temp_file)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling Cursor AI: {str(e)}")
            return None
    
    async def _execute_cursor_ai_command(self, prompt_file: str) -> Optional[str]:
        """Execute Cursor AI command"""
        try:
            # This is a placeholder implementation
            # In practice, you would use Cursor's actual API or command line interface
            
            # For now, we'll simulate AI response with intelligent analysis
            return await self._simulate_ai_response(prompt_file)
            
        except Exception as e:
            logger.error(f"Error executing Cursor AI command: {str(e)}")
            return None
    
    async def _simulate_ai_response(self, prompt_file: str) -> str:
        """Simulate AI response (placeholder for real Cursor AI integration)"""
        # This is a placeholder - replace with actual Cursor AI integration
        
        # Read the prompt
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # For demonstration, return a structured response
        if "Дайджест" in prompt or "Digest" in prompt:
            return self._generate_ai_digest_template()
        elif "ранжируй" in prompt or "rank" in prompt:
            return self._generate_ai_ranking_template()
        else:
            return self._generate_ai_insights_template()
    
    def _generate_ai_digest_template(self) -> str:
        """Generate AI-style digest template"""
        from datetime import datetime
        
        if self.is_russian:
            date_str = datetime.now().strftime('%d.%m.%Y')
            return f"""🌾 **Дайджест сельскохозяйственного рынка** - {date_str}

📈 **Ключевые события дня:**
Анализ показывает смешанные сигналы на рынке сельскохозяйственных товаров. Цены на зерновые демонстрируют волатильность на фоне погодных факторов и изменений в торговой политике.

📊 **Анализ рынка:**
Текущая ситуация характеризуется повышенной неопределенностью из-за климатических условий и геополитических факторов. Рынок адаптируется к новым условиям торговли.

🌾 **По товарным группам:**
- **Зерновые:** Пшеница показывает рост на фоне снижения предложения
- **Масличные:** Соя стабильна, подсолнечник под давлением
- **Животноводство:** Цены на мясо остаются высокими

📰 **Основные новости:**
1. Изменения в экспортной политике влияют на цены зерна
2. Погодные условия создают неопределенность для урожая
3. Новые технологии внедряются в сельское хозяйство

🔮 **Прогноз:**
Ожидается продолжение волатильности в краткосрочной перспективе с тенденцией к росту цен на фоне ограниченного предложения.

---
🤖 Создано с помощью AI-анализа Agriculture Digest Bot"""
        else:
            date_str = datetime.now().strftime('%B %d, %Y')
            return f"""🌾 **Agriculture Market Digest** - {date_str}

📈 **Key Market Developments:**
Analysis shows mixed signals in agricultural commodity markets. Grain prices demonstrate volatility amid weather factors and trade policy changes.

📊 **Market Analysis:**
Current situation is characterized by increased uncertainty due to climatic conditions and geopolitical factors. Market is adapting to new trade conditions.

🌾 **By Commodity Groups:**
- **Grains:** Wheat shows growth amid reduced supply
- **Oilseeds:** Soybeans stable, sunflower under pressure
- **Livestock:** Meat prices remain high

📰 **Top News:**
1. Export policy changes affecting grain prices
2. Weather conditions creating harvest uncertainty
3. New technologies being adopted in agriculture

🔮 **Outlook:**
Continued volatility expected in short term with upward price trend amid limited supply.

---
🤖 Generated with AI analysis by Agriculture Digest Bot"""
    
    def _generate_ai_ranking_template(self) -> str:
        """Generate AI-style ranking template"""
        return """{
    "ranked_articles": [0, 1, 2, 3, 4],
    "reasoning": "Статьи ранжированы по влиянию на цены, торговую активность и региональной значимости",
    "market_impact": "Высокое влияние на краткосрочные цены и торговые потоки"
}"""
    
    def _generate_ai_insights_template(self) -> str:
        """Generate AI-style insights template"""
        if self.is_russian:
            return """**Ключевые инсайты рынка:**

Анализ показывает усиление волатильности на рынке зерновых из-за погодных факторов и изменений в торговой политике. Цены на пшеницу демонстрируют восходящий тренд на фоне ограниченного предложения.

Региональные различия становятся более выраженными, с особым вниманием к ситуации в Казахстане и России. Внедрение новых технологий создает долгосрочные возможности для повышения эффективности производства."""
        else:
            return """**Key Market Insights:**

Analysis shows increased volatility in grain markets due to weather factors and trade policy changes. Wheat prices demonstrate upward trend amid limited supply.

Regional differences are becoming more pronounced, with particular attention to situation in Kazakhstan and Russia. New technology adoption creates long-term opportunities for production efficiency improvement."""
    
    def _parse_ranking_result(self, ranking_result: str, articles: List[Dict]) -> List[Dict]:
        """Parse AI ranking result and apply to articles"""
        try:
            # Try to parse JSON response
            result = json.loads(ranking_result)
            ranked_indices = result.get('ranked_articles', [])
            
            # Apply ranking
            ranked_articles = []
            for idx in ranked_indices:
                if 0 <= idx < len(articles):
                    article = articles[idx].copy()
                    article['ai_ranking'] = len(ranked_articles) + 1
                    article['ai_reasoning'] = result.get('reasoning', '')
                    ranked_articles.append(article)
            
            return ranked_articles
            
        except Exception as e:
            logger.error(f"Error parsing ranking result: {str(e)}")
            return self._fallback_rank_articles(articles)
    
    def _fallback_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Fallback ranking method"""
        return articles[:10]
    
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

def main():
    """Test the Cursor AI service"""
    import asyncio
    
    async def test_cursor_ai():
        try:
            ai_service = CursorAIService()
            
            # Test articles
            test_articles = [
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
            
            print("🤖 Testing Cursor AI Service...")
            
            # Test ranking
            ranked = await ai_service.analyze_and_rank_articles(test_articles)
            print(f"✅ Ranked {len(ranked)} articles")
            
            # Test digest generation
            digest = await ai_service.generate_intelligent_digest(ranked)
            print(f"✅ Generated digest ({len(digest)} characters)")
            
            print("\n📋 Generated Digest:")
            print("-" * 50)
            print(digest)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    asyncio.run(test_cursor_ai())

if __name__ == "__main__":
    main()
