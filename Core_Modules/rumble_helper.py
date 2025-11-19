#!/usr/bin/env python3
"""
Rumble Helper Service - URL parsing, channel mapping, and embed URL generation
Integrates with rumble_channels.json database for pub code lookup
"""

import re
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


class RumbleHelper:
    """Helper class for Rumble video and channel URL processing"""
    
    def __init__(self, channels_db_path: Optional[str] = None):
        """
        Initialize Rumble helper with channel database
        
        Args:
            channels_db_path: Path to rumble_channels.json (defaults to src/data/rumble_channels.json)
        """
        if channels_db_path is None:
            # Default to src/data/rumble_channels.json
            default_path = Path(__file__).parent.parent / "data" / "rumble_channels.json"
            channels_db_path = str(default_path)
        
        self.channels_db_path = channels_db_path
        self.channels = {}
        self.handle_to_pub = {}
        self.load_channels_database()
    
    def load_channels_database(self) -> bool:
        """
        Load Rumble channels from JSON database
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(self.channels_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Index channels by handle for quick lookup
            for channel in data.get('channels', []):
                handle = channel.get('handle')
                if handle:
                    self.channels[handle.lower()] = channel
                    self.handle_to_pub[handle.lower()] = channel.get('pub_code', '')
            
            print(f"Loaded {len(self.channels)} Rumble channels from database")
            return True
            
        except Exception as e:
            print(f"Warning: Could not load Rumble channels database: {e}")
            return False
    
    def is_rumble_url(self, url: str) -> bool:
        """
        Check if URL is a Rumble video or channel URL
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if Rumble URL, False otherwise
        """
        if not url:
            return False
        
        url_lower = url.lower()
        return 'rumble.com' in url_lower
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various Rumble URL formats
        
        Supported formats:
        - https://rumble.com/v{VIDEO_ID}-{title}.html
        - https://rumble.com/embed/v{VIDEO_ID}/
        - https://rumble.com/embed/v{VIDEO_ID}/?pub={PUB}
        
        Args:
            url: Rumble URL
            
        Returns:
            str: Video ID with 'v' prefix (e.g., 'v66u9v0') or None if not found
        """
        if not url:
            return None
        
        # Pattern 1: /v{VIDEO_ID}-{title}.html or /v{VIDEO_ID}/
        # Capture the full ID including the 'v' prefix
        pattern_v = r'/(v[a-z0-9]+)[-/]'
        match_v = re.search(pattern_v, url, re.IGNORECASE)
        if match_v:
            return match_v.group(1)
        
        # Pattern 2: /embed/v{VIDEO_ID}/
        # Capture the full ID including the 'v' prefix
        pattern_embed = r'/embed/(v[a-z0-9]+)/?'
        match_embed = re.search(pattern_embed, url, re.IGNORECASE)
        if match_embed:
            return match_embed.group(1)
        
        # Pattern 3: Just the video ID if provided directly (with v prefix)
        if re.match(r'^v[a-z0-9]+$', url, re.IGNORECASE):
            return url
        
        return None
    
    def extract_channel_handle(self, url: str) -> Optional[str]:
        """
        Extract channel handle from Rumble channel URL
        
        Format: https://rumble.com/c/{HANDLE}
        
        Args:
            url: Rumble channel URL
            
        Returns:
            str: Channel handle or None if not found
        """
        if not url:
            return None
        
        # Pattern: /c/{HANDLE} or /c/{HANDLE}/
        pattern = r'/c/([a-zA-Z0-9_-]+)/?'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        return None
    
    def extract_pub_code(self, url: str) -> Optional[str]:
        """
        Extract pub code from Rumble embed URL
        
        Format: ?pub={PUB_CODE}
        
        Args:
            url: Rumble embed URL
            
        Returns:
            str: Publisher code or None if not found
        """
        if not url:
            return None
        
        # Pattern: ?pub={PUB_CODE} or &pub={PUB_CODE}
        pattern = r'[?&]pub=([a-zA-Z0-9]+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        return None
    
    def get_pub_code_by_handle(self, handle: str) -> Optional[str]:
        """
        Look up pub code for a channel handle from database
        
        Args:
            handle: Channel handle (e.g., "RedPill78")
            
        Returns:
            str: Publisher code or None if not found
        """
        if not handle:
            return None
        
        return self.handle_to_pub.get(handle.lower())
    
    def get_channel_info(self, handle: str) -> Optional[Dict[str, Any]]:
        """
        Get full channel information from database
        
        Args:
            handle: Channel handle
            
        Returns:
            dict: Channel data or None if not found
        """
        if not handle:
            return None
        
        return self.channels.get(handle.lower())
    
    def generate_embed_url(self, video_id: str, pub_code: Optional[str] = None) -> str:
        """
        Generate Rumble embed URL from video ID and optional pub code
        
        Args:
            video_id: Video ID
            pub_code: Optional publisher code for monetization tracking
            
        Returns:
            str: Embed URL
        """
        if not video_id:
            return ""
        
        base_url = f"https://rumble.com/embed/{video_id}/"
        
        if pub_code:
            return f"{base_url}?pub={pub_code}"
        
        return base_url
    
    def normalize_url(self, url: str, handle: Optional[str] = None) -> Tuple[str, Dict[str, str]]:
        """
        Normalize Rumble URL to embed format with metadata
        
        Args:
            url: Rumble video or embed URL
            handle: Optional channel handle for pub code lookup
            
        Returns:
            tuple: (embed_url, metadata_dict)
        """
        if not url or not self.is_rumble_url(url):
            return url, {}
        
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return url, {}
        
        # Try to get pub code from URL first
        pub_code = self.extract_pub_code(url)
        
        # If no pub code in URL, try to get from handle
        if not pub_code and handle:
            pub_code = self.get_pub_code_by_handle(handle)
        
        # If no pub code from handle, try to extract channel handle from URL
        if not pub_code:
            extracted_handle = self.extract_channel_handle(url)
            if extracted_handle:
                pub_code = self.get_pub_code_by_handle(extracted_handle)
                handle = extracted_handle
        
        # Generate embed URL
        embed_url = self.generate_embed_url(video_id, pub_code)
        
        # Build metadata
        metadata = {
            'video_id': video_id,
            'provider': 'Rumble',
            'embed_url': embed_url
        }
        
        if pub_code:
            metadata['pub_code'] = pub_code
        
        if handle:
            metadata['channel_handle'] = handle
            channel_info = self.get_channel_info(handle)
            if channel_info:
                metadata['channel_name'] = channel_info.get('name', '')
                metadata['category'] = channel_info.get('category', '')
        
        return embed_url, metadata
    
    def fetch_oembed_metadata(self, url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Fetch video metadata from Rumble oEmbed API
        
        API Endpoint: https://rumble.com/api/Media/oembed.json?url={video_url}
        
        Args:
            url: Rumble video URL
            timeout: Request timeout in seconds
            
        Returns:
            dict: oEmbed metadata or None if failed
        """
        if not url or not self.is_rumble_url(url):
            return None
        
        try:
            # Rumble oEmbed API endpoint
            oembed_url = f"https://rumble.com/api/Media/oembed.json?url={url}"
            
            response = requests.get(oembed_url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract useful metadata
            metadata = {
                'title': data.get('title', ''),
                'author_name': data.get('author_name', ''),
                'author_url': data.get('author_url', ''),
                'thumbnail_url': data.get('thumbnail_url', ''),
                'width': data.get('width', 0),
                'height': data.get('height', 0),
                'html': data.get('html', ''),
                'provider_name': data.get('provider_name', 'Rumble'),
                'provider_url': data.get('provider_url', 'https://rumble.com')
            }
            
            return metadata
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch Rumble oEmbed metadata: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON from Rumble oEmbed API: {e}")
            return None
    
    def enrich_channel_data(self, url: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrich channel data with all available metadata
        Combines URL parsing, database lookup, and oEmbed API
        
        Args:
            url: Rumble video or channel URL
            title: Optional title override
            
        Returns:
            dict: Enriched channel data with all metadata
        """
        # Start with normalized URL and basic metadata
        embed_url, metadata = self.normalize_url(url)
        
        # Fetch oEmbed metadata
        oembed_data = self.fetch_oembed_metadata(url)
        if oembed_data:
            # Use oEmbed title if no title provided
            if not title:
                title = oembed_data.get('title', '')
            
            # Add oEmbed metadata
            metadata.update({
                'thumbnail_url': oembed_data.get('thumbnail_url', ''),
                'author_name': oembed_data.get('author_name', ''),
                'width': oembed_data.get('width', 640),
                'height': oembed_data.get('height', 360)
            })
        
        # Build final enriched data
        enriched_data = {
            'url': url,
            'embed_url': embed_url,
            'title': title or url,
            'metadata': metadata
        }
        
        return enriched_data
    
    def list_channels_by_category(self, category: Optional[str] = None) -> list:
        """
        List all channels, optionally filtered by category
        
        Args:
            category: Optional category filter (e.g., "News", "Comedy")
            
        Returns:
            list: List of channel dictionaries
        """
        if not category:
            return list(self.channels.values())
        
        return [
            channel for channel in self.channels.values()
            if channel.get('category', '').lower() == category.lower()
        ]


# Convenience functions for direct usage
def is_rumble_url(url: str) -> bool:
    """Quick check if URL is from Rumble"""
    return 'rumble.com' in url.lower() if url else False


def extract_video_id_from_url(url: str) -> Optional[str]:
    """Quick extraction of video ID from Rumble URL"""
    helper = RumbleHelper()
    return helper.extract_video_id(url)


def get_rumble_embed_url(url: str, handle: Optional[str] = None) -> str:
    """Quick conversion to Rumble embed URL"""
    helper = RumbleHelper()
    embed_url, _ = helper.normalize_url(url, handle)
    return embed_url


if __name__ == "__main__":
    # Test the helper
    helper = RumbleHelper()
    
    print("=== Rumble Helper Test ===\n")
    
    # Test video ID extraction
    test_urls = [
        "https://rumble.com/v66kw07-x22-report.html",
        "https://rumble.com/embed/v66kw07/?pub=4abcd",
        "https://rumble.com/c/RedPill78"
    ]
    
    for url in test_urls:
        print(f"URL: {url}")
        video_id = helper.extract_video_id(url)
        print(f"  Video ID: {video_id}")
        
        handle = helper.extract_channel_handle(url)
        print(f"  Handle: {handle}")
        
        embed_url, metadata = helper.normalize_url(url)
        print(f"  Embed: {embed_url}")
        print(f"  Metadata: {metadata}\n")
    
    # Test channel lookup
    print("\n=== Channel Lookup ===")
    handle = "RedPill78"
    channel_info = helper.get_channel_info(handle)
    print(f"Handle: {handle}")
    print(f"Channel: {channel_info}\n")
    
    # Test category listing
    print("\n=== News Channels ===")
    news_channels = helper.list_channels_by_category("News")
    for ch in news_channels:
        print(f"  • {ch['name']} (@{ch['handle']})")
