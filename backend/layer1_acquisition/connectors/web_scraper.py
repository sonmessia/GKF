"""
Web Scraper Connector
Fetches data from web pages using BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Callable
from .base_connector import BaseConnector, logger


class WebScraperConnector(BaseConnector):
    """
    Connector for scraping web pages.
    Uses BeautifulSoup for HTML parsing.
    """

    def __init__(self, config: Dict):
        """
        config = {
            'urls': ['https://example.com/page1', ...],
            'headers': {} (optional),
            'parser': callable function to extract data from soup
        }
        """
        super().__init__(config)
        self.urls = config.get("urls", [])
        self.headers = config.get("headers", {"User-Agent": "GKF-Crawler/1.0"})
        self.parser: Callable = config.get("parser", self._default_parser)

    def connect(self) -> bool:
        """Validate URLs are accessible"""
        if not self.urls:
            logger.error("No URLs provided")
            return False
        return True

    def fetch(self) -> List[Dict]:
        """Scrape data from web pages"""
        try:
            for url in self.urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, "html.parser")
                    page_data = self.parser(soup, url)

                    if page_data:
                        if isinstance(page_data, list):
                            self.data.extend(page_data)
                        else:
                            self.data.append(page_data)

                    logger.info(f"Scraped data from {url}")

                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    continue

            logger.info(f"Fetched {len(self.data)} records from {len(self.urls)} URLs")
            return self.data

        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return []

    def disconnect(self) -> bool:
        """No persistent connection to close"""
        return True

    def _default_parser(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Default parser - extracts title and basic metadata.
        Override with custom parser in config.
        """
        return {
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "text": soup.get_text()[:500],  # First 500 chars
        }
