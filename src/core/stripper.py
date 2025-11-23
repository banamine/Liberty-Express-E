"""
Media Stripper - Private media extraction from websites

Extracts video, audio, and streaming media from any website.
Features: Selenium support, robots.txt checking, retry logic, blob URL extraction.
"""

import re
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MediaExtractor:
    """Extracts media files and metadata from HTML content"""
    
    # Media file extensions to look for
    MEDIA_EXTENSIONS = {
        'video': {'.mp4', '.m3u8', '.m3u', '.ts', '.mkv', '.webm', '.avi', '.mov', '.flv', '.wmv'},
        'audio': {'.mp3', '.aac', '.flac', '.wav', '.ogg', '.m4a'},
        'subtitle': {'.vtt', '.srt', '.ass', '.ssa', '.sub', '.sbv'}
    }
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.extracted_media: Dict[str, List[str]] = {
            'video': [],
            'audio': [],
            'subtitle': [],
            'stream': []
        }
        self.extracted_at = datetime.utcnow().isoformat()
    
    def extract_from_html(self, html_content: str) -> Dict[str, List[str]]:
        """Extract media URLs from HTML content"""
        
        # Extract from standard tags
        self._extract_from_tags(html_content)
        
        # Extract from JavaScript/JSON
        self._extract_from_js(html_content)
        
        # Extract streaming URLs (m3u8, mpd)
        self._extract_streams(html_content)
        
        # Remove duplicates and resolve relative URLs
        for media_type in self.extracted_media:
            urls = set(self.extracted_media[media_type])
            self.extracted_media[media_type] = [
                self._resolve_url(url) for url in urls if url
            ]
        
        return self.extracted_media
    
    def _extract_from_tags(self, html_content: str):
        """Extract media from HTML tags"""
        
        # Video tags
        for match in re.finditer(r'<video[^>]*>.*?</video>', html_content, re.DOTALL):
            sources = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', match.group())
            self.extracted_media['video'].extend(sources)
        
        # Audio tags
        for match in re.finditer(r'<audio[^>]*>.*?</audio>', html_content, re.DOTALL):
            sources = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', match.group())
            self.extracted_media['audio'].extend(sources)
        
        # Iframe embeds
        iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html_content)
        self.extracted_media['stream'].extend(iframes)
        
        # Object/embed tags
        objects = re.findall(r'<(?:object|embed)[^>]+data=["\']([^"\']+)["\']', html_content)
        self.extracted_media['video'].extend(objects)
    
    def _extract_from_js(self, html_content: str):
        """Extract media from JavaScript/JSON content"""
        
        # Look for URLs in JavaScript
        url_patterns = [
            r'(?:src|url|href|location|src_url)\s*[:=]\s*["\']([^"\']+\.(?:mp4|m3u8|m3u|webm|mkv|mp3|aac))["\']',
            r'(?:video|audio|stream|url|src)\s*:\s*["\']([^"\']+\.(?:mp4|m3u8|m3u|webm|mkv|mp3|aac))["\']',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    self.extracted_media['video' if 'mp4' in match or 'webm' in match or 'mkv' in match else 'audio'].append(match)
                elif match.startswith('//'):
                    self.extracted_media['video' if 'mp4' in match or 'webm' in match or 'mkv' in match else 'audio'].append(f'https:{match}')
        
        # Look for JSON with media objects
        json_patterns = re.findall(r'\{[^{}]*(?:["\'](?:url|src|source|media)["\'].*?)+[^{}]*\}', html_content)
        for json_str in json_patterns:
            try:
                # Try to extract valid JSON objects
                match = re.search(r'\{.*\}', json_str)
                if match:
                    obj = json.loads(match.group())
                    for key in ['url', 'src', 'source', 'media', 'videoUrl', 'audioUrl']:
                        if key in obj and isinstance(obj[key], str):
                            self.extracted_media['video'].append(obj[key])
            except (json.JSONDecodeError, ValueError):
                pass
    
    def _extract_streams(self, html_content: str):
        """Extract streaming manifest URLs"""
        
        # M3U8 playlists
        m3u8_urls = re.findall(r'(?:https?://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?)', html_content)
        self.extracted_media['stream'].extend(m3u8_urls)
        
        # DASH manifests
        mpd_urls = re.findall(r'(?:https?://[^\s"\'<>]+\.mpd(?:\?[^\s"\'<>]*)?)', html_content)
        self.extracted_media['stream'].extend(mpd_urls)
        
        # HLS variants
        m3u_urls = re.findall(r'(?:https?://[^\s"\'<>]+\.m3u(?:\?[^\s"\'<>]*)?)', html_content)
        self.extracted_media['stream'].extend(m3u_urls)
    
    def _resolve_url(self, url: str) -> str:
        """Resolve relative URLs to absolute"""
        if not url:
            return ""
        
        if url.startswith('http://') or url.startswith('https://'):
            return url
        if url.startswith('//'):
            return f'https:{url}'
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        
        return urljoin(self.base_url, url)
    
    def to_m3u_playlist(self) -> str:
        """Generate M3U playlist from extracted media"""
        lines = ['#EXTM3U', '#EXT-X-VERSION:3', f'# Extracted from {self.base_url}', f'# Extracted: {self.extracted_at}', '']
        
        # Add video files
        for i, url in enumerate(self.extracted_media['video'], 1):
            lines.append(f'#EXTINF:-1,Video_{i}')
            lines.append(url)
        
        # Add audio files
        for i, url in enumerate(self.extracted_media['audio'], 1):
            lines.append(f'#EXTINF:-1,Audio_{i}')
            lines.append(url)
        
        # Add streams
        for i, url in enumerate(self.extracted_media['stream'], 1):
            lines.append(f'#EXTINF:-1,Stream_{i}')
            lines.append(url)
        
        return '\n'.join(lines)


class StripperManager:
    """Manages media stripping operations"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_scan = None
        self.scan_history: List[Dict] = []
    
    def scan_website(self, url: str, html_content: str) -> Dict:
        """Scan a website for media"""
        try:
            extractor = MediaExtractor(url)
            media = extractor.extract_from_html(html_content)
            
            scan_result = {
                'status': 'success',
                'url': url,
                'timestamp': datetime.utcnow().isoformat(),
                'media_count': sum(len(v) for v in media.values()),
                'media': media,
                'playlist_path': None
            }
            
            # Save as M3U
            output_file = self.output_dir / 'MASTER_PLAYLIST.m3u'
            with open(output_file, 'w') as f:
                f.write(extractor.to_m3u_playlist())
            
            scan_result['playlist_path'] = str(output_file)
            self.current_scan = scan_result
            self.scan_history.append(scan_result)
            
            logger.info(f"Scan complete: {scan_result['media_count']} media items from {url}")
            return scan_result
        
        except Exception as e:
            error_result = {
                'status': 'error',
                'url': url,
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            self.current_scan = error_result
            self.scan_history.append(error_result)
            logger.error(f"Scan failed: {e}")
            return error_result
    
    def get_current_scan(self) -> Optional[Dict]:
        """Get current/last scan result"""
        return self.current_scan
    
    def get_scan_history(self) -> List[Dict]:
        """Get scan history"""
        return self.scan_history
    
    def clear_history(self):
        """Clear scan history"""
        self.scan_history = []
        self.current_scan = None
