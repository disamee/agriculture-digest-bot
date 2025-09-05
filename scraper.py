"""
Web scraping module for agriculture news sources
"""
import requests
import feedparser
import time
import logging
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from config import NEWS_SOURCES, SCRAPING_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    """Main class for scraping agriculture news from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPING_CONFIG['user_agent']
        })
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape news from a single source
        
        Args:
            source: Dictionary containing source configuration
            
        Returns:
            List of article dictionaries
        """
        try:
            if source['type'] == 'rss':
                return self._scrape_rss(source)
            elif source['type'] == 'scrape':
                return self._scrape_html(source)
            elif source['type'] == 'telegram':
                return asyncio.run(self._scrape_telegram(source))
            else:
                logger.warning(f"Unknown source type: {source['type']}")
                return []
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {str(e)}")
            return []
    
    def _scrape_rss(self, source: Dict) -> List[Dict]:
        """Scrape RSS feed"""
        try:
            feed = feedparser.parse(source.get('rss_url', source['url']))
            articles = []
            
            for entry in feed.entries[:SCRAPING_CONFIG.get('max_articles_per_source', 5)]:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'source': source['name']
                }
                articles.append(article)
            
            logger.info(f"Scraped {len(articles)} articles from {source['name']} RSS")
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS for {source['name']}: {str(e)}")
            return []
    
    def _scrape_html(self, source: Dict) -> List[Dict]:
        """Scrape HTML content"""
        try:
            response = self._make_request(source['url'])
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find article containers (common patterns)
            article_selectors = [
                'article',
                '.article',
                '.news-item',
                '.post',
                '.entry',
                '[class*="article"]',
                '[class*="news"]',
                '[class*="post"]'
            ]
            
            article_elements = []
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    article_elements = elements
                    break
            
            if not article_elements:
                # Fallback: look for common link patterns
                article_elements = soup.find_all('a', href=True)
                article_elements = [elem for elem in article_elements 
                                 if any(keyword in elem.get_text().lower() 
                                       for keyword in ['agriculture', 'farm', 'crop', 'livestock', 'food'])]
            
            for element in article_elements[:SCRAPING_CONFIG.get('max_articles_per_source', 5)]:
                article = self._extract_article_data(element, source)
                if article and article['title']:
                    articles.append(article)
            
            logger.info(f"Scraped {len(articles)} articles from {source['name']} HTML")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping HTML for {source['name']}: {str(e)}")
            return []
    
    def _extract_article_data(self, element, source: Dict) -> Optional[Dict]:
        """Extract article data from HTML element"""
        try:
            # Try to find title
            title = self._find_text_by_selectors(element, [
                'h1', 'h2', 'h3', 'h4',
                '.title', '.headline', '.article-title',
                '[class*="title"]', '[class*="headline"]'
            ])
            
            # Try to find link
            link = self._find_link(element, source['url'])
            
            # Try to find summary
            summary = self._find_text_by_selectors(element, [
                'p', '.summary', '.excerpt', '.description',
                '[class*="summary"]', '[class*="excerpt"]'
            ])
            
            if not title and link:
                # If no title found, try to extract from link text
                title = element.get_text().strip()[:100]
            
            if title:
                return {
                    'title': title.strip(),
                    'link': link,
                    'summary': summary.strip() if summary else '',
                    'source': source['name']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting article data: {str(e)}")
            return None
    
    def _find_text_by_selectors(self, element, selectors: List[str]) -> Optional[str]:
        """Find text content using multiple CSS selectors"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    text = found.get_text().strip()
                    if text and len(text) > 10:  # Filter out very short text
                        return text
            except:
                continue
        return None
    
    def _find_link(self, element, base_url: str) -> Optional[str]:
        """Find and normalize link URL"""
        try:
            # Check if element itself is a link
            if element.name == 'a' and element.get('href'):
                return urljoin(base_url, element.get('href'))
            
            # Look for link within element
            link_elem = element.find('a', href=True)
            if link_elem:
                return urljoin(base_url, link_elem.get('href'))
            
            return None
        except:
            return None
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(SCRAPING_CONFIG['max_retries']):
            try:
                response = self.session.get(
                    url, 
                    timeout=SCRAPING_CONFIG['request_timeout']
                )
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < SCRAPING_CONFIG['max_retries'] - 1:
                    time.sleep(SCRAPING_CONFIG['delay_between_requests'])
        
        return None
    
    async def _scrape_telegram(self, source: Dict) -> List[Dict]:
        """Scrape Telegram channel posts"""
        try:
            # Note: This requires Telegram API credentials
            # For now, return empty list - implement when needed
            logger.info(f"Telegram scraping not implemented for {source['name']}")
            return []
            
            # Future implementation would use Telethon:
            # client = TelegramClient('session', api_id, api_hash)
            # await client.start()
            # channel = await client.get_entity(source['channel_username'])
            # messages = await client.get_messages(channel, limit=source.get('max_posts', 10))
            # 
            # articles = []
            # for msg in messages:
            #     if msg.text:
            #         article = {
            #             'title': msg.text[:100] + '...' if len(msg.text) > 100 else msg.text,
            #             'summary': msg.text,
            #             'link': f"https://t.me/{source['channel_username']}/{msg.id}",
            #             'source': source['name'],
            #             'published': msg.date.isoformat() if msg.date else ''
            #         }
            #         articles.append(article)
            # 
            # await client.disconnect()
            # return articles
            
        except Exception as e:
            logger.error(f"Error scraping Telegram {source['name']}: {str(e)}")
            return []
    
    def scrape_all_sources(self) -> List[Dict]:
        """
        Scrape all configured news sources
        
        Returns:
            List of all articles from all sources
        """
        all_articles = []
        
        for source in NEWS_SOURCES:
            logger.info(f"Scraping {source['name']}...")
            articles = self.scrape_source(source)
            all_articles.extend(articles)
            
            # Add delay between sources to be respectful
            time.sleep(SCRAPING_CONFIG['delay_between_requests'])
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles

def main():
    """Test the scraper"""
    scraper = NewsScraper()
    articles = scraper.scrape_all_sources()
    
    print(f"\nScraped {len(articles)} articles:")
    for article in articles[:5]:  # Show first 5
        print(f"- {article['title']} ({article['source']})")
        if article['link']:
            print(f"  Link: {article['link']}")
        print()

if __name__ == "__main__":
    main()
