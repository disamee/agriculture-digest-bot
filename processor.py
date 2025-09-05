"""
Content processing and summarization module
"""
import re
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import DIGEST_CONFIG, LANGUAGE
from llm_service import LLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentProcessor:
    """Process and summarize agriculture news content"""
    
    def __init__(self):
        self.language = LANGUAGE
        self.is_russian = self.language == 'ru'
        
        # Agriculture keywords in both Russian and English
        if self.is_russian:
            self.agriculture_keywords = [
                'сельское хозяйство', 'фермерство', 'урожай', 'скот', 'молочное', 'птицеводство',
                'пшеница', 'кукуруза', 'соя', 'рис', 'хлопок', 'сахар', 'кофе',
                'удобрение', 'пестицид', 'орошение', 'сбор урожая', 'посадка',
                'продовольственная безопасность', 'устойчивое земледелие', 'органическое', 'точное земледелие',
                'агротех', 'сельхозтехника', 'трактор', 'семена', 'зерно', 'корм',
                'товар', 'рыночная цена', 'экспорт', 'импорт', 'торговля',
                'agriculture', 'farming', 'crop', 'livestock', 'dairy', 'poultry',
                'wheat', 'corn', 'soybean', 'rice', 'cotton', 'sugar', 'coffee'
            ]
        else:
            self.agriculture_keywords = [
                'agriculture', 'farming', 'crop', 'livestock', 'dairy', 'poultry',
                'wheat', 'corn', 'soybean', 'rice', 'cotton', 'sugar', 'coffee',
                'fertilizer', 'pesticide', 'irrigation', 'harvest', 'planting',
                'food security', 'sustainable farming', 'organic', 'precision agriculture',
                'agtech', 'farm equipment', 'tractor', 'seed', 'grain', 'feed',
                'commodity', 'market price', 'export', 'import', 'trade'
            ]
        
        # Initialize LLM service
        try:
            self.llm_service = LLMService()
            self.use_llm = True
            logger.info("LLM service initialized successfully")
        except Exception as e:
            logger.warning(f"LLM service not available: {str(e)}")
            self.llm_service = None
            self.use_llm = False
    
    def filter_relevant_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles to keep only agriculture-related content
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Filtered list of relevant articles
        """
        relevant_articles = []
        
        for article in articles:
            if self._is_agriculture_related(article):
                relevant_articles.append(article)
        
        logger.info(f"Filtered {len(relevant_articles)} relevant articles from {len(articles)} total")
        return relevant_articles
    
    def _is_agriculture_related(self, article: Dict) -> bool:
        """Check if article is agriculture-related"""
        text_to_check = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Check for agriculture keywords
        keyword_count = sum(1 for keyword in self.agriculture_keywords 
                          if keyword in text_to_check)
        
        # Article is relevant if it contains at least 2 agriculture keywords
        # or if title contains at least 1 agriculture keyword
        title_keywords = sum(1 for keyword in self.agriculture_keywords 
                           if keyword in article.get('title', '').lower())
        
        return keyword_count >= 2 or title_keywords >= 1
    
    async def rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Rank articles by relevance and recency using LLM or fallback method
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Ranked list of articles
        """
        if self.use_llm and self.llm_service:
            try:
                logger.info("Using LLM for article ranking")
                return await self.llm_service.rank_and_filter_articles(articles)
            except Exception as e:
                logger.error(f"LLM ranking failed: {str(e)}")
        
        # Fallback to traditional ranking
        logger.info("Using fallback ranking method")
        return self._fallback_rank_articles(articles)
    
    def _fallback_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Fallback ranking method when LLM is not available"""
        def calculate_score(article):
            score = 0
            
            # Title relevance score
            title = article.get('title', '').lower()
            title_keywords = sum(1 for keyword in self.agriculture_keywords 
                               if keyword in title)
            score += title_keywords * 3
            
            # Summary relevance score
            summary = article.get('summary', '').lower()
            summary_keywords = sum(1 for keyword in self.agriculture_keywords 
                                 if keyword in summary)
            score += summary_keywords * 2
            
            # Length bonus (longer articles might be more substantial)
            if len(article.get('summary', '')) > 100:
                score += 1
            
            # Source credibility (you can customize this based on your preferences)
            source = article.get('source', '').lower()
            if 'fastmarkets' in source:
                score += 3
            elif 'apk' in source or 'margin' in source:
                score += 2
            elif 'usda' in source:
                score += 2
            elif 'reuters' in source or 'bloomberg' in source:
                score += 1
            
            return score
        
        # Sort by score (highest first)
        ranked_articles = sorted(articles, key=calculate_score, reverse=True)
        
        # Limit to max articles
        max_articles = DIGEST_CONFIG.get('max_total_articles', 15)
        return ranked_articles[:max_articles]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    async def summarize_article(self, article: Dict) -> str:
        """
        Create a summary of an article using LLM or fallback method
        
        Args:
            article: Article dictionary
            
        Returns:
            Summarized text
        """
        if self.use_llm and self.llm_service:
            try:
                return await self.llm_service.summarize_article(article)
            except Exception as e:
                logger.error(f"LLM summarization failed: {str(e)}")
        
        # Fallback to simple summarization
        return self._fallback_summarize_article(article)
    
    def _fallback_summarize_article(self, article: Dict) -> str:
        """No fallback - only AI should generate summaries"""
        # Return empty string - no hard-coded fallbacks
        return ""
    
    async def group_articles_by_topic(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group articles by topic/category using LLM or fallback method
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with topics as keys and article lists as values
        """
        if self.use_llm and self.llm_service:
            try:
                return await self.llm_service.categorize_articles(articles)
            except Exception as e:
                logger.error(f"LLM categorization failed: {str(e)}")
        
        # Fallback to traditional categorization
        return self._fallback_group_articles_by_topic(articles)
    
    def _fallback_group_articles_by_topic(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Fallback categorization method when LLM is not available"""
        topics = {
            'Crops & Commodities': [],
            'Livestock & Dairy': [],
            'Technology & Innovation': [],
            'Market & Trade': [],
            'Policy & Regulation': [],
            'Weather & Environment': [],
            'Other': []
        }
        
        for article in articles:
            topic = self._categorize_article(article)
            topics[topic].append(article)
        
        # Remove empty topics
        topics = {k: v for k, v in topics.items() if v}
        
        return topics
    
    def _categorize_article(self, article: Dict) -> str:
        """Categorize article into topic"""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Crop-related keywords
        crop_keywords = ['crop', 'wheat', 'corn', 'soybean', 'rice', 'cotton', 'sugar', 'coffee', 'grain', 'seed', 'harvest', 'planting']
        if any(keyword in text for keyword in crop_keywords):
            return 'Crops & Commodities'
        
        # Livestock keywords
        livestock_keywords = ['livestock', 'cattle', 'pig', 'poultry', 'chicken', 'dairy', 'milk', 'beef', 'pork', 'sheep', 'goat']
        if any(keyword in text for keyword in livestock_keywords):
            return 'Livestock & Dairy'
        
        # Technology keywords
        tech_keywords = ['technology', 'agtech', 'precision', 'drone', 'ai', 'artificial intelligence', 'automation', 'digital', 'smart farming']
        if any(keyword in text for keyword in tech_keywords):
            return 'Technology & Innovation'
        
        # Market keywords
        market_keywords = ['market', 'price', 'commodity', 'trade', 'export', 'import', 'futures', 'trading', 'supply', 'demand']
        if any(keyword in text for keyword in market_keywords):
            return 'Market & Trade'
        
        # Policy keywords
        policy_keywords = ['policy', 'regulation', 'government', 'subsidy', 'law', 'bill', 'congress', 'senate', 'fda', 'usda']
        if any(keyword in text for keyword in policy_keywords):
            return 'Policy & Regulation'
        
        # Weather keywords
        weather_keywords = ['weather', 'climate', 'drought', 'flood', 'rain', 'temperature', 'environment', 'sustainability', 'carbon']
        if any(keyword in text for keyword in weather_keywords):
            return 'Weather & Environment'
        
        return 'Other'
    
    async def format_digest(self, articles: List[Dict]) -> str:
        """
        Format articles into a digest message using LLM or fallback method
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Formatted digest string
        """
        if not articles:
            return "No agriculture news found today."
        
        if self.use_llm and self.llm_service:
            try:
                logger.info("Using LLM for digest generation")
                return await self.llm_service.generate_digest_summary(articles)
            except Exception as e:
                logger.error(f"LLM digest generation failed: {str(e)}")
        
        # Fallback to traditional digest formatting
        return await self._fallback_format_digest(articles)
    
    async def _fallback_format_digest(self, articles: List[Dict]) -> str:
        """Fallback digest formatting when LLM is not available"""
        # Create digest header
        if self.is_russian:
            title = DIGEST_CONFIG.get('digest_title_ru', '🌾 Дайджест сельскохозяйственного рынка')
            date_str = datetime.now().strftime('%d.%m.%Y')
            digest = f"{title} - {date_str}\n\n"
            digest += f"📊 **{len(articles)} статей** из {len(set(article['source'] for article in articles))} источников\n\n"
        else:
            title = DIGEST_CONFIG.get('digest_title_en', '🌾 Agriculture Market Digest')
            date_str = datetime.now().strftime('%B %d, %Y')
            digest = f"{title} - {date_str}\n\n"
            digest += f"📊 **{len(articles)} articles** from {len(set(article['source'] for article in articles))} sources\n\n"
        
        # Add articles in simple list format
        for i, article in enumerate(articles[:8], 1):  # Max 8 articles
            title = article.get('title', 'Без заголовка')
            summary = await self.summarize_article(article)
            
            # Add title
            digest += f"**{i}. {title}**\n"
            
            # Add description/summary
            if summary and len(summary) > 20:
                digest += f"{summary}\n"
            else:
                # If no AI summary, skip description
                if self.is_russian:
                    digest += "Описание недоступно (требуется ИИ).\n"
                else:
                    digest += "Description unavailable (AI required).\n"
            
            # Add link only
            if DIGEST_CONFIG.get('include_source_links', True) and article.get('link'):
                if self.is_russian:
                    digest += f"🔗 [Читать полностью]({article['link']})\n"
                else:
                    digest += f"🔗 [Read more]({article['link']})\n"
            
            digest += "\n"
        
        # Add footer
        digest += "---\n"
        if self.is_russian:
            digest += "🤖 Создано ботом Agriculture Digest\n"
            digest += "📅 Обновляется ежедневно с последними новостями сельскохозяйственного рынка"
        else:
            digest += "🤖 Generated by Agriculture Digest Bot\n"
            digest += "📅 Updated daily with the latest agriculture market news"
        
        return digest

async def main():
    """Test the processor"""
    processor = ContentProcessor()
    
    # Sample articles for testing
    sample_articles = [
        {
            'title': 'Wheat Prices Rise Due to Drought Conditions',
            'summary': 'Global wheat prices have increased by 15% this month due to severe drought conditions in major wheat-producing regions.',
            'link': 'https://example.com/wheat-prices',
            'source': 'Fastmarkets Agriculture'
        },
        {
            'title': 'New Precision Agriculture Technology Launched',
            'summary': 'A new AI-powered precision agriculture system has been launched to help farmers optimize crop yields.',
            'link': 'https://example.com/precision-ag',
            'source': 'APK-Inform'
        }
    ]
    
    # Test filtering
    relevant = processor.filter_relevant_articles(sample_articles)
    print(f"Relevant articles: {len(relevant)}")
    
    # Test ranking
    ranked = await processor.rank_articles(relevant)
    print(f"Ranked articles: {len(ranked)}")
    
    # Test digest formatting
    digest = await processor.format_digest(ranked)
    print("\nGenerated Digest:")
    print(digest)

if __name__ == "__main__":
    asyncio.run(main())
