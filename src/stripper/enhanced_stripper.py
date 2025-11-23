"""
Enhanced Media Stripper Module - Step 4 of refactoring
Extract media from websites using Selenium with robots.txt compliance
"""

import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Check robots.txt compliance"""
    
    def __init__(self):
        self.cache = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Check if URL can be fetched according to robots.txt"""
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            if domain not in self.cache:
                rp = RobotFileParser()
                robots_url = f"{domain}/robots.txt"
                rp.set_url(robots_url)
                rp.read()
                self.cache[domain] = rp
            else:
                rp = self.cache[domain]
            
            return rp.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Assume allowed if can't check


class EnhancedMediaStripper:
    """
    Extract media URLs from websites with:
    - Selenium for JavaScript-heavy sites
    - robots.txt compliance
    - Fallback to BeautifulSoup
    - Rate limiting
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.robots_checker = RobotsChecker()
        self.driver = None
        self.last_request_time = {}
    
    def _get_driver(self):
        """Get or create Selenium WebDriver"""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
        return self.driver
    
    def extract_media_urls(self, url: str, 
                          respect_robots_txt: bool = True) -> List[Dict[str, str]]:
        """
        Extract media URLs from webpage
        
        Args:
            url: Website URL to extract from
            respect_robots_txt: Check robots.txt before fetching
        
        Returns:
            List of media URLs with metadata
        """
        # Check robots.txt
        if respect_robots_txt:
            if not self.robots_checker.can_fetch(url):
                logger.warning(f"URL blocked by robots.txt: {url}")
                return []
        
        # Apply rate limiting
        self._apply_rate_limit(url)
        
        media_urls = []
        
        try:
            # Try JavaScript extraction first (Selenium)
            logger.info(f"Attempting Selenium extraction for {url}")
            selenium_urls = self._extract_with_selenium(url)
            if selenium_urls:
                media_urls.extend(selenium_urls)
                return media_urls
        except Exception as e:
            logger.warning(f"Selenium extraction failed: {e}")
        
        try:
            # Fallback to BeautifulSoup for static content
            logger.info(f"Attempting BeautifulSoup extraction for {url}")
            bs_urls = self._extract_with_beautifulsoup(url)
            media_urls.extend(bs_urls)
        except Exception as e:
            logger.error(f"Both extraction methods failed for {url}: {e}")
        
        return media_urls
    
    def _extract_with_selenium(self, url: str) -> List[Dict[str, str]]:
        """Extract media using Selenium (for JavaScript-heavy sites)"""
        driver = self._get_driver()
        driver.get(url)
        
        # Wait for dynamic content
        try:
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "video"))
            )
        except:
            pass
        
        # Extract video/audio sources
        sources = []
        
        # Look for <video> tags
        videos = driver.find_elements(By.TAG_NAME, "video")
        for video in videos:
            srcs = video.find_elements(By.TAG_NAME, "source")
            for src in srcs:
                media_url = src.get_attribute("src")
                if media_url:
                    sources.append({
                        "url": media_url,
                        "type": src.get_attribute("type") or "video",
                        "source": "video_tag"
                    })
        
        # Look for <audio> tags
        audios = driver.find_elements(By.TAG_NAME, "audio")
        for audio in audios:
            srcs = audio.find_elements(By.TAG_NAME, "source")
            for src in srcs:
                media_url = src.get_attribute("src")
                if media_url:
                    sources.append({
                        "url": media_url,
                        "type": src.get_attribute("type") or "audio",
                        "source": "audio_tag"
                    })
        
        # Look for <iframe> tags that might contain video
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and ('youtube' in src or 'vimeo' in src or 'twitch' in src):
                sources.append({
                    "url": src,
                    "type": "iframe",
                    "source": "embedded_video"
                })
        
        return sources
    
    def _extract_with_beautifulsoup(self, url: str) -> List[Dict[str, str]]:
        """Extract media using BeautifulSoup (for static content)"""
        response = requests.get(url, timeout=self.timeout)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        sources = []
        
        # Find all media URLs
        for tag in soup.find_all(['video', 'audio', 'source', 'iframe']):
            if tag.name == 'source':
                src = tag.get('src')
                if src:
                    sources.append({
                        "url": src,
                        "type": tag.get('type', 'media'),
                        "source": "source_tag"
                    })
            
            elif tag.name == 'iframe':
                src = tag.get('src')
                if src and any(x in src for x in ['youtube', 'vimeo', 'twitch']):
                    sources.append({
                        "url": src,
                        "type": "iframe",
                        "source": "embedded_video"
                    })
            
            elif tag.name in ['video', 'audio']:
                src = tag.get('src')
                if src:
                    sources.append({
                        "url": src,
                        "type": tag.name,
                        "source": f"{tag.name}_tag"
                    })
        
        return sources
    
    def _apply_rate_limit(self, url: str, delay: float = 1.0) -> None:
        """Apply rate limiting to avoid overwhelming servers"""
        domain = urlparse(url).netloc
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < delay:
                time.sleep(delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def close(self) -> None:
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
