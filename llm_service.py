"""
LLM Service for AI-powered agriculture digest generation using Cursor AI
"""
import logging
import json
import re
from typing import List, Dict, Optional, Tuple
from config import USE_CURSOR_AI, LANGUAGE, DIGEST_CONFIG
from cursor_ai_service import CursorAIService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for AI-powered content processing using Cursor AI"""
    
    def __init__(self):
        self.use_cursor_ai = USE_CURSOR_AI
        self.language = LANGUAGE
        self.is_russian = self.language == 'ru'
        
        # Initialize Cursor AI service
        if self.use_cursor_ai:
            try:
                self.cursor_ai = CursorAIService()
                logger.info("Cursor AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cursor AI: {str(e)}")
                self.cursor_ai = None
                self.use_cursor_ai = False
        else:
            self.cursor_ai = None
            logger.warning("Cursor AI is disabled, using fallback methods")
    
    async def rank_and_filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Use real AI to intelligently rank and filter agriculture articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            AI-ranked and filtered list of articles
        """
        if not articles:
            return []
        
        if self.use_cursor_ai and self.cursor_ai:
            try:
                # Use real Cursor AI for ranking
                ranked_articles = await self.cursor_ai.analyze_and_rank_articles(articles)
                logger.info(f"Cursor AI ranked {len(ranked_articles)} articles from {len(articles)} total")
                return ranked_articles
                
            except Exception as e:
                logger.error(f"Error in Cursor AI ranking: {str(e)}")
                return self._fallback_rank_articles(articles)
        else:
            # Use fallback ranking
            return self._fallback_rank_articles(articles)
    
    def _intelligent_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Intelligent ranking algorithm for agriculture articles"""
        def calculate_importance_score(article):
            score = 0
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            source = article.get('source', '').lower()
            
            # High-impact keywords (Russian and English)
            high_impact_keywords = [
                'цена', 'price', 'рост', 'rise', 'падение', 'fall', 'кризис', 'crisis',
                'экспорт', 'export', 'импорт', 'import', 'торговля', 'trade',
                'засуха', 'drought', 'наводнение', 'flood', 'погода', 'weather',
                'политика', 'policy', 'закон', 'law', 'регулирование', 'regulation'
            ]
            
            # Commodity keywords
            commodity_keywords = [
                'пшеница', 'wheat', 'кукуруза', 'corn', 'соя', 'soybean', 'рис', 'rice',
                'ячмень', 'barley', 'рожь', 'rye', 'овес', 'oats', 'хлопок', 'cotton'
            ]
            
            # Source credibility
            source_scores = {
                'fastmarkets': 5,
                'apk': 4,
                'margin': 4,
                'eldala': 3,
                'amis': 3
            }
            
            # Calculate scores
            for keyword in high_impact_keywords:
                if keyword in title:
                    score += 3
                if keyword in summary:
                    score += 2
            
            for keyword in commodity_keywords:
                if keyword in title:
                    score += 2
                if keyword in summary:
                    score += 1
            
            # Source credibility
            for source_key, source_score in source_scores.items():
                if source_key in source:
                    score += source_score
                    break
            
            # Length bonus
            if len(summary) > 100:
                score += 1
            
            # Recency bonus (if published date available)
            if article.get('published'):
                score += 1
            
            return score
        
        # Sort by importance score
        ranked_articles = sorted(articles, key=calculate_importance_score, reverse=True)
        
        # Limit to max articles
        max_articles = DIGEST_CONFIG.get('max_total_articles', 15)
        return ranked_articles[:max_articles]
    
    def _fallback_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Simple fallback ranking"""
        return articles[:10]
    
    async def generate_digest_summary(self, articles: List[Dict]) -> str:
        """
        Generate an AI-powered digest summary in Russian
        
        Args:
            articles: List of ranked articles
            
        Returns:
            Formatted digest summary
        """
        if not articles:
            if self.is_russian:
                return "Сегодня новостей сельского хозяйства не найдено."
            else:
                return "No agriculture news found today."
        
        if self.use_cursor_ai and self.cursor_ai:
            try:
                # Use real Cursor AI for digest generation
                digest = await self.cursor_ai.generate_intelligent_digest(articles)
                logger.info("Cursor AI generated digest successfully")
                return digest
                
            except Exception as e:
                logger.error(f"Error in Cursor AI digest generation: {str(e)}")
                return self._generate_fallback_digest(articles)
        else:
            # Use fallback digest generation
            return self._generate_fallback_digest(articles)
    
    def _generate_intelligent_digest(self, articles: List[Dict]) -> str:
        """Generate intelligent digest with market analysis"""
        from datetime import datetime
        
        # Get digest title
        if self.is_russian:
            title = DIGEST_CONFIG.get('digest_title_ru', '🌾 Дайджест сельскохозяйственного рынка')
        else:
            title = DIGEST_CONFIG.get('digest_title_en', '🌾 Agriculture Market Digest')
        
        # Create header
        date_str = datetime.now().strftime('%d.%m.%Y')
        if self.is_russian:
            header = f"{title} - {date_str}\n\n"
            header += f"📊 **{len(articles)} статей** из {len(set(article['source'] for article in articles))} источников\n\n"
        else:
            header = f"{title} - {date_str}\n\n"
            header += f"📊 **{len(articles)} articles** from {len(set(article['source'] for article in articles))} sources\n\n"
        
        # Analyze articles for key themes
        themes = self._analyze_market_themes(articles)
        
        # Generate executive summary
        if self.is_russian:
            summary = "📈 **Ключевые события дня:**\n"
        else:
            summary = "📈 **Key Market Developments:**\n"
        
        summary += self._generate_executive_summary(articles, themes)
        summary += "\n"
        
        # Group articles by importance
        top_articles = articles[:8]  # Top 8 articles
        
        # Add articles with links
        if self.is_russian:
            summary += "📰 **Основные новости:**\n\n"
        else:
            summary += "📰 **Top News:**\n\n"
        
        for i, article in enumerate(top_articles, 1):
            title = article.get('title', 'Без заголовка')
            source = article.get('source', 'Неизвестный источник')
            link = article.get('link', '')
            
            # Truncate long titles
            if len(title) > 80:
                title = title[:77] + "..."
            
            summary += f"**{i}. {title}**\n"
            summary += f"📰 Источник: {source}\n"
            
            if link and DIGEST_CONFIG.get('include_source_links', True):
                summary += f"🔗 [Читать полностью]({link})\n"
            
            summary += "\n"
        
        # Add footer
        if self.is_russian:
            footer = "\n---\n🤖 Создано ботом Agriculture Digest\n📅 Обновляется ежедневно"
        else:
            footer = "\n---\n🤖 Generated by Agriculture Digest Bot\n📅 Updated daily"
        
        return header + summary + footer
    
    def _analyze_market_themes(self, articles: List[Dict]) -> Dict[str, int]:
        """Analyze articles to identify key market themes"""
        themes = {
            'prices': 0,
            'weather': 0,
            'trade': 0,
            'policy': 0,
            'technology': 0,
            'supply_demand': 0
        }
        
        theme_keywords = {
            'prices': ['цена', 'price', 'рост', 'rise', 'падение', 'fall', 'стоимость', 'cost'],
            'weather': ['погода', 'weather', 'засуха', 'drought', 'дождь', 'rain', 'климат', 'climate'],
            'trade': ['торговля', 'trade', 'экспорт', 'export', 'импорт', 'import', 'поставки', 'supply'],
            'policy': ['политика', 'policy', 'закон', 'law', 'регулирование', 'regulation', 'правительство', 'government'],
            'technology': ['технология', 'technology', 'цифровизация', 'digital', 'ии', 'ai', 'автоматизация', 'automation'],
            'supply_demand': ['спрос', 'demand', 'предложение', 'supply', 'урожай', 'harvest', 'производство', 'production']
        }
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            for theme, keywords in theme_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        themes[theme] += 1
                        break
        
        return themes
    
    def _generate_executive_summary(self, articles: List[Dict], themes: Dict[str, int]) -> str:
        """Generate executive summary based on themes"""
        if self.is_russian:
            summary_parts = []
            
            if themes['prices'] > 0:
                summary_parts.append("• Динамика цен на сельхозпродукцию")
            if themes['weather'] > 0:
                summary_parts.append("• Влияние погодных условий на рынок")
            if themes['trade'] > 0:
                summary_parts.append("• Изменения в торговых потоках")
            if themes['policy'] > 0:
                summary_parts.append("• Новые регулятивные меры")
            if themes['technology'] > 0:
                summary_parts.append("• Внедрение новых технологий")
            
            if not summary_parts:
                summary_parts.append("• Общие тенденции сельскохозяйственного рынка")
            
            return "\n".join(summary_parts[:3])  # Top 3 themes
        else:
            summary_parts = []
            
            if themes['prices'] > 0:
                summary_parts.append("• Agricultural commodity price movements")
            if themes['weather'] > 0:
                summary_parts.append("• Weather impact on markets")
            if themes['trade'] > 0:
                summary_parts.append("• Trade flow changes")
            if themes['policy'] > 0:
                summary_parts.append("• New regulatory measures")
            if themes['technology'] > 0:
                summary_parts.append("• Technology adoption")
            
            if not summary_parts:
                summary_parts.append("• General agricultural market trends")
            
            return "\n".join(summary_parts[:3])  # Top 3 themes
    
    async def summarize_article(self, article: Dict) -> str:
        """
        Generate AI-powered article summary in 2-3 sentences
        
        Args:
            article: Article dictionary
            
        Returns:
            AI-generated summary in 2-3 sentences
        """
        try:
            title = article.get('title', '')
            content = article.get('summary', '')
            
            # If we have Cursor AI available, use it for intelligent summarization
            if self.use_cursor_ai and self.cursor_ai:
                try:
                    # Prepare content for AI processing
                    full_content = f"Заголовок: {title}\n\nСодержание: {content}"
                    
                    # Use Cursor AI to generate summary
                    ai_summary = await self.cursor_ai.generate_article_summary(full_content)
                    if ai_summary and len(ai_summary.strip()) > 10:
                        return ai_summary.strip()
                        
                except Exception as e:
                    logger.error(f"Cursor AI summarization failed: {str(e)}")
            
            # Fallback to intelligent summarization
            return self._generate_intelligent_summary(title, content)
            
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return self._generate_fallback_summary(article)
    
    def _generate_intelligent_summary(self, title: str, content: str) -> str:
        """
        Generate intelligent summary based on content analysis
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Intelligent summary in 2-3 sentences
        """
        try:
            # Combine title and content for analysis
            full_text = f"{title} {content}".lower()
            
            # Agriculture-specific keyword analysis
            if any(word in full_text for word in ['урожай', 'harvest', 'сбор', 'уборка']):
                if self.is_russian:
                    return f"Статья посвящена вопросам сбора урожая и состоянию сельскохозяйственных культур. {self._extract_key_info(content)}"
                else:
                    return f"Article focuses on harvest and agricultural crop conditions. {self._extract_key_info(content)}"
            
            elif any(word in full_text for word in ['цена', 'price', 'стоимость', 'рынок']):
                if self.is_russian:
                    return f"Материал анализирует ценовые тенденции на сельскохозяйственную продукцию. {self._extract_key_info(content)}"
                else:
                    return f"Material analyzes price trends for agricultural products. {self._extract_key_info(content)}"
            
            elif any(word in full_text for word in ['технология', 'technology', 'инновация', 'новые']):
                if self.is_russian:
                    return f"Статья рассказывает о новых технологиях и инновациях в сельском хозяйстве. {self._extract_key_info(content)}"
                else:
                    return f"Article discusses new technologies and innovations in agriculture. {self._extract_key_info(content)}"
            
            elif any(word in full_text for word in ['погода', 'weather', 'климат', 'дождь', 'засуха']):
                if self.is_russian:
                    return f"Материал рассматривает влияние погодных условий на сельскохозяйственное производство. {self._extract_key_info(content)}"
                else:
                    return f"Material examines weather impact on agricultural production. {self._extract_key_info(content)}"
            
            elif any(word in full_text for word in ['экспорт', 'export', 'импорт', 'import', 'торговля']):
                if self.is_russian:
                    return f"Статья освещает вопросы международной торговли сельскохозяйственной продукцией. {self._extract_key_info(content)}"
                else:
                    return f"Article covers international trade in agricultural products. {self._extract_key_info(content)}"
            
            else:
                # Generic summary
                if self.is_russian:
                    return f"Статья содержит актуальную информацию о событиях в сфере сельского хозяйства. {self._extract_key_info(content)}"
                else:
                    return f"Article contains current information about agriculture sector events. {self._extract_key_info(content)}"
                    
        except Exception as e:
            logger.error(f"Error in intelligent summary generation: {str(e)}")
            return self._generate_fallback_summary({'title': title, 'summary': content})
    
    def _extract_key_info(self, content: str) -> str:
        """
        Extract key information from content for summary
        
        Args:
            content: Article content
            
        Returns:
            Key information string
        """
        try:
            if not content or len(content) < 20:
                if self.is_russian:
                    return "Подробности доступны в полной статье."
                else:
                    return "Details available in the full article."
            
            # Extract first meaningful sentence or phrase
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 100:
                    return sentence + "."
            
            # If no good sentence found, truncate content
            if len(content) > 80:
                return content[:80] + "..."
            else:
                return content
                
        except Exception as e:
            logger.error(f"Error extracting key info: {str(e)}")
            if self.is_russian:
                return "Подробности доступны в полной статье."
            else:
                return "Details available in the full article."
    
    def _generate_fallback_summary(self, article: Dict) -> str:
        """
        Generate fallback summary when AI is not available
        
        Args:
            article: Article dictionary
            
        Returns:
            Fallback summary
        """
        title = article.get('title', '')
        content = article.get('summary', '')
        
        if content and len(content) > 30:
            # Use content if available
            if len(content) > 100:
                return content[:100] + "..."
            return content
        elif title and len(title) > 10:
            # Use title as summary
            if self.is_russian:
                return f"Статья о: {title}"
            else:
                return f"Article about: {title}"
        else:
            if self.is_russian:
                return "Информация о сельскохозяйственных событиях."
            else:
                return "Information about agricultural events."
    
    async def categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Intelligently categorize articles
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with categories as keys and article lists as values
        """
        if not articles:
            return {}
        
        try:
            return self._intelligent_categorization(articles)
            
        except Exception as e:
            logger.error(f"Error categorizing articles: {str(e)}")
            return self._fallback_categorization(articles)
    
    def _intelligent_categorization(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Intelligent categorization algorithm"""
        if self.is_russian:
            categories = {
                'Зерновые и масличные': [],
                'Животноводство': [],
                'Технологии': [],
                'Рынок и торговля': [],
                'Политика и регулирование': [],
                'Погода и экология': [],
                'Региональные рынки': [],
                'Другое': []
            }
        else:
            categories = {
                'Grains & Oilseeds': [],
                'Livestock & Dairy': [],
                'Technology & Innovation': [],
                'Market & Trade': [],
                'Policy & Regulation': [],
                'Weather & Environment': [],
                'Regional Markets': [],
                'Other': []
            }
        
        # Define category keywords
        if self.is_russian:
            category_keywords = {
                'Зерновые и масличные': ['пшеница', 'кукуруза', 'соя', 'рис', 'ячмень', 'рожь', 'овес', 'подсолнечник', 'рапс'],
                'Животноводство': ['скот', 'свиньи', 'птица', 'молоко', 'мясо', 'животноводство', 'крупный рогатый скот'],
                'Технологии': ['технология', 'цифровизация', 'ии', 'автоматизация', 'робот', 'дрон', 'сенсор'],
                'Рынок и торговля': ['цена', 'торговля', 'экспорт', 'импорт', 'рынок', 'биржа', 'фьючерс'],
                'Политика и регулирование': ['политика', 'закон', 'регулирование', 'правительство', 'субсидия', 'налог'],
                'Погода и экология': ['погода', 'засуха', 'дождь', 'климат', 'экология', 'устойчивость', 'углерод'],
                'Региональные рынки': ['казахстан', 'россия', 'украина', 'беларусь', 'узбекистан', 'регион']
            }
        else:
            category_keywords = {
                'Grains & Oilseeds': ['wheat', 'corn', 'soybean', 'rice', 'barley', 'rye', 'oats', 'sunflower', 'rapeseed'],
                'Livestock & Dairy': ['cattle', 'pigs', 'poultry', 'milk', 'meat', 'livestock', 'dairy'],
                'Technology & Innovation': ['technology', 'digital', 'ai', 'automation', 'robot', 'drone', 'sensor'],
                'Market & Trade': ['price', 'trade', 'export', 'import', 'market', 'exchange', 'futures'],
                'Policy & Regulation': ['policy', 'law', 'regulation', 'government', 'subsidy', 'tax'],
                'Weather & Environment': ['weather', 'drought', 'rain', 'climate', 'environment', 'sustainability', 'carbon'],
                'Regional Markets': ['kazakhstan', 'russia', 'ukraine', 'belarus', 'uzbekistan', 'region']
            }
        
        # Categorize articles
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        categories[category].append(article)
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                if self.is_russian:
                    categories['Другое'].append(article)
                else:
                    categories['Other'].append(article)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _prepare_articles_for_llm(self, articles: List[Dict]) -> str:
        """Prepare articles text for processing"""
        articles_text = ""
        for i, article in enumerate(articles):
            title = article.get('title', '')
            summary = article.get('summary', '')
            source = article.get('source', '')
            
            articles_text += f"Article {i}:\n"
            articles_text += f"Title: {title}\n"
            articles_text += f"Summary: {summary}\n"
            articles_text += f"Source: {source}\n\n"
        
        return articles_text
    
    def _get_current_date(self) -> str:
        """Get current date string"""
        from datetime import datetime
        if self.is_russian:
            return datetime.now().strftime('%d.%m.%Y')
        else:
            return datetime.now().strftime('%B %d, %Y')
    
    def _generate_fallback_digest(self, articles: List[Dict]) -> str:
        """Generate fallback digest if AI fails"""
        from datetime import datetime
        
        if self.is_russian:
            title = "🌾 Дайджест сельскохозяйственного рынка"
            date_str = datetime.now().strftime('%d.%m.%Y')
            header = f"{title} - {date_str}\n\n"
            header += f"📊 **{len(articles)} статей** из источников новостей сельского хозяйства\n\n"
            
            digest = header
            
            for i, article in enumerate(articles[:10], 1):
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
            
            for i, article in enumerate(articles[:10], 1):
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
    
    def _fallback_categorization(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Fallback categorization method"""
        if self.is_russian:
            categories = {
                'Новости сельского хозяйства': articles[:5],
                'Обновления рынка': articles[5:10] if len(articles) > 5 else []
            }
        else:
            categories = {
                'Agriculture News': articles[:5],
                'Market Updates': articles[5:10] if len(articles) > 5 else []
            }
        return {k: v for k, v in categories.items() if v}

def main():
    """Test the LLM service"""
    import asyncio
    
    async def test_llm():
        try:
            llm = LLMService()
            
            # Test articles
            test_articles = [
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
            
            # Test ranking
            ranked = await llm.rank_and_filter_articles(test_articles)
            print(f"Ranked {len(ranked)} articles")
            
            # Test digest generation
            digest = await llm.generate_digest_summary(ranked)
            print("\nGenerated Digest:")
            print(digest)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    asyncio.run(test_llm())

if __name__ == "__main__":
    main()
