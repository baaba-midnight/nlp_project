"""
Web Scraper Service
Handles scraping text content from web pages/URLs.

This service can extract text from HTML pages, handling navigation menus,
headers, footers, and extracting main content.
"""

import re
import logging
from typing import List, Optional, Union
from urllib.parse import urlparse, urljoin, urlunparse
import time

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class WebScraperService:
    """Service for scraping text content from web pages."""
    
    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[dict] = None,
        delay_between_requests: float = 1.0
    ):
        """
        Initialize Web Scraper Service.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            headers: Custom headers for requests (default: browser-like headers)
            delay_between_requests: Delay in seconds between requests (default: 1.0)
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests and beautifulsoup4 are required. "
                "Install with: pip install requests beautifulsoup4"
            )
        
        self.timeout = timeout
        self.delay = delay_between_requests
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Common HTML elements to remove (navigation, ads, footers, etc.)
        self.unwanted_tags = [
            'nav', 'header', 'footer', 'aside', 'script', 'style',
            'noscript', 'iframe', 'embed', 'object', 'applet'
        ]
        
        self.unwanted_classes = [
            'nav', 'navigation', 'menu', 'sidebar', 'footer',
            'header', 'advertisement', 'ad', 'ads', 'social',
            'share', 'comment', 'comments', 'related', 'popup'
        ]
        
        self.unwanted_ids = [
            'nav', 'navigation', 'menu', 'sidebar', 'footer',
            'header', 'advertisement', 'ad', 'ads'
        ]
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make HTTP request to URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Response object or None if error
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Respect rate limiting
            time.sleep(self.delay)
            
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract main content from HTML, removing navigation and boilerplate.
        
        Args:
            soup: BeautifulSoup object
            url: Source URL (for context)
            
        Returns:
            Extracted text content
        """
        # Remove unwanted tags
        for tag in self.unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with unwanted classes
        for class_name in self.unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
        
        # Remove elements with unwanted IDs
        for id_name in self.unwanted_ids:
            element = soup.find(id=re.compile(id_name, re.I))
            if element:
                element.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Common main content selectors
        main_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '#content', '.main-content',
            '#main-content', '.post-content', '.entry-content',
            '.article-content', '#article-content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                logger.debug(f"Found main content using selector: {selector}")
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
            if main_content:
                # Remove common boilerplate from body
                for selector in ['header', 'footer', 'nav', '.nav', '#nav']:
                    for element in main_content.select(selector):
                        element.decompose()
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback: get all text
            text = soup.get_text(separator='\n', strip=True)
        
        return text
    
    def _clean_web_text(self, text: str) -> str:
        """
        Clean extracted web text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove empty lines at start/end
        lines = [line.strip() for line in text.split('\n')]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def scrape_url(
        self,
        url: str,
        extract_main_content: bool = True
    ) -> Optional[Document]:
        """
        Scrape text from a single URL.
        
        Args:
            url: URL to scrape
            extract_main_content: Whether to extract only main content (default: True)
            
        Returns:
            Document object with scraped text, or None if error
        """
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else url
            
            # Extract text
            if extract_main_content:
                text = self._extract_main_content(soup, url)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean text
            text = self._clean_web_text(text)
            
            if not text or len(text.strip()) < 50:
                logger.warning(f"Extracted very little text from {url}")
                return None
            
            # Create document
            doc = Document(
                page_content=text,
                metadata={
                    'source': url,
                    'url': url,
                    'title': title,
                    'content_type': 'web',
                    'extraction_method': 'web_scraper'
                }
            )
            
            logger.info(f"Successfully scraped {url} ({len(text)} characters)")
            return doc
            
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {str(e)}")
            return None
    
    def scrape_urls(
        self,
        urls: List[str],
        extract_main_content: bool = True,
        continue_on_error: bool = True
    ) -> List[Document]:
        """
        Scrape text from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            extract_main_content: Whether to extract only main content (default: True)
            continue_on_error: Whether to continue if one URL fails (default: True)
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for url in urls:
            try:
                doc = self.scrape_url(url, extract_main_content=extract_main_content)
                if doc:
                    documents.append(doc)
                elif not continue_on_error:
                    break
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                if not continue_on_error:
                    raise
        
        logger.info(f"Successfully scraped {len(documents)}/{len(urls)} URLs")
        return documents
    
    def scrape_from_file(
        self,
        file_path: str,
        extract_main_content: bool = True
    ) -> List[Document]:
        """
        Scrape URLs listed in a text file (one URL per line).
        
        Args:
            file_path: Path to text file containing URLs
            extract_main_content: Whether to extract only main content (default: True)
            
        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract URLs (skip comments and empty lines)
            urls = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Check if it looks like a URL
                    if line.startswith('http://') or line.startswith('https://'):
                        urls.append(line)
                    elif line.startswith('www.'):
                        urls.append(f'https://{line}')
            
            logger.info(f"Found {len(urls)} URLs in {file_path}")
            return self.scrape_urls(urls, extract_main_content=extract_main_content)
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return []

