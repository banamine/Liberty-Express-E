"""
M3U Parser - Handles parsing of M3U/M3U8 playlist files
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import unquote
import requests
from datetime import datetime

# Import models - works with sys.path injection in Core_Modules
from models.channel import Channel, ChannelDict, ChannelUtils


class M3UParser:
    """
    Parser for M3U/M3U8 playlist files with support for various formats and encodings.
    Handles EXTINF, EXTGRP, custom tags, and Rumble URL detection.
    """
    
    def __init__(self, cache_thumbnails: bool = True, thumbnails_dir: Optional[Path] = None):
        """
        Initialize the M3U parser.
        
        Args:
            cache_thumbnails: Whether to cache thumbnail images
            thumbnails_dir: Directory for cached thumbnails
        """
        self.logger = logging.getLogger(__name__)
        self.cache_thumbnails = cache_thumbnails
        self.thumbnails_dir = thumbnails_dir or Path("thumbnails")
        self.custom_tags = {}
    
    def parse_file(self, file_path: str) -> List[ChannelDict]:
        """
        Parse an M3U file and extract channel information.
        
        Args:
            file_path: Path to the M3U file
            
        Returns:
            List of channel dictionaries
        """
        channels = []
        current_channel = None
        custom_tags = {}
        
        try:
            lines = self._read_file_lines(file_path)
            if not lines:
                return []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines or M3U header
                if not line or line == "#EXTM3U" or line == "#EXTMM3U":
                    i += 1
                    continue
                
                # Parse EXTINF line
                if line.startswith("#EXTINF") or line.startswith("#EXTM:") or line.startswith("#EXTMM:"):
                    current_channel = self._parse_extinf_line(line)
                    
                    # Check for EXTGRP on next line
                    if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                        current_channel["group"] = lines[i + 1].split(":")[1].strip()
                        i += 1
                    i += 1
                    continue
                
                # Parse custom tags
                if line.startswith("#") and ":" in line and not line.startswith("#EXTINF"):
                    tag_parts = line[1:].split(":", 1)
                    if len(tag_parts) == 2:
                        tag_name, tag_value = tag_parts
                        custom_tags[tag_name.strip()] = tag_value.strip()
                    i += 1
                    continue
                
                # Process URL line
                if current_channel and not line.startswith("#"):
                    current_channel["url"] = line.strip()
                    current_channel["custom_tags"] = custom_tags.copy()
                    
                    # Detect and enrich Rumble URLs
                    rumble_info = self._detect_rumble_url(current_channel["url"])
                    if rumble_info:
                        self._enrich_rumble_channel(current_channel, rumble_info)
                    
                    # Add UUID if not present
                    channel = ChannelUtils.validate_channel_dict(current_channel)
                    channels.append(channel)
                    
                    current_channel = None
                    custom_tags = {}
                
                i += 1
            
            self.logger.info(f"Parsed {len(channels)} channels from {Path(file_path).name}")
            return channels
            
        except Exception as e:
            self.logger.error(f"Failed to parse M3U file {file_path}: {e}")
            return []
    
    def _read_file_lines(self, file_path: str) -> List[str]:
        """
        Read lines from a file with encoding detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of lines from the file
        """
        try:
            # Try UTF-8 first
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.readlines()
            except:
                # Fallback to Latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.readlines()
        except Exception as e:
            self.logger.error(f"Cannot read file {file_path}: {e}")
            return []
    
    def _parse_extinf_line(self, line: str) -> ChannelDict:
        """
        Parse an EXTINF line to extract channel attributes.
        
        Args:
            line: The EXTINF line to parse
            
        Returns:
            Dictionary containing channel information
        """
        channel = ChannelUtils.create_default_channel()
        
        # Extract attributes using regex
        attr_pattern = r'([a-zA-Z-]+)="([^"]*)"'
        attributes = dict(re.findall(attr_pattern, line))
        
        # Extract channel name from the end of the line
        name_part = line.split(',')[-1].strip()
        if name_part:
            channel["name"] = unquote(name_part)
        
        # Process attributes
        if "tvg-name" in attributes:
            channel["name"] = unquote(attributes["tvg-name"])
        if "group-title" in attributes:
            channel["group"] = unquote(attributes["group-title"])
        if "tvg-logo" in attributes:
            channel["logo"] = attributes["tvg-logo"]  # Don't decode URLs
        if "tvg-id" in attributes:
            channel["tvg_id"] = attributes["tvg-id"]
        
        # Normalize group name
        channel["group"] = ChannelUtils.normalize_group_name(channel["group"])
        
        return channel
    
    def _detect_rumble_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Detect if URL is a Rumble video and extract metadata.
        
        Args:
            url: The URL to check
            
        Returns:
            Dictionary with Rumble video information or None
        """
        if not url or 'rumble.com' not in url.lower():
            return None
        
        # Pattern 1: Embed URL
        embed_match = re.search(r'rumble\.com/embed/(v[a-zA-Z0-9]+)/?\?pub=([a-zA-Z0-9]+)', url)
        if embed_match:
            return {
                'video_id': embed_match.group(1),
                'pub_code': embed_match.group(2),
                'embed_url': url
            }
        
        # Pattern 2: Watch URL
        watch_match = re.search(r'rumble\.com/(?:watch/)?(v[a-zA-Z0-9]+)', url)
        if watch_match:
            return {
                'video_id': watch_match.group(1),
                'pub_code': None,
                'embed_url': None
            }
        
        return None
    
    def _enrich_rumble_channel(self, channel: ChannelDict, rumble_info: Dict[str, Any]) -> None:
        """
        Enrich channel with Rumble metadata.
        
        Args:
            channel: Channel dictionary to enrich
            rumble_info: Rumble video information
        """
        channel["custom_tags"]["PROVIDER"] = "RUMBLE"
        channel["custom_tags"]["VIDEO_ID"] = rumble_info.get('video_id', '')
        channel["custom_tags"]["PUB_CODE"] = rumble_info.get('pub_code', '')
        
        # Fetch metadata from oEmbed API if needed
        rumble_meta = self._fetch_rumble_metadata(channel["url"])
        if rumble_meta:
            if not channel.get("name") or channel["name"] == "Unknown":
                channel["name"] = rumble_meta['title']
            if not channel.get("logo"):
                channel["logo"] = rumble_meta.get('thumbnail', '')
            channel["custom_tags"]["EMBED_URL"] = rumble_meta.get('embed_url', '')
            channel["custom_tags"]["WIDTH"] = str(rumble_meta.get('width', 640))
            channel["custom_tags"]["HEIGHT"] = str(rumble_meta.get('height', 360))
    
    def _fetch_rumble_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Rumble video metadata using oEmbed API.
        
        Args:
            url: Rumble video URL
            
        Returns:
            Dictionary with metadata or None
        """
        try:
            import urllib.parse
            oembed_url = f"https://rumble.com/api/Media/oembed.json?url={urllib.parse.quote(url)}"
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract embed URL from HTML
                html = data.get('html', '')
                embed_match = re.search(r'src=["\']([^"\']+)["\']', html)
                embed_url = embed_match.group(1) if embed_match else None
                
                return {
                    'title': data.get('title', 'Rumble Video'),
                    'thumbnail': data.get('thumbnail_url', ''),
                    'width': data.get('width', 640),
                    'height': data.get('height', 360),
                    'embed_url': embed_url,
                    'provider': 'Rumble'
                }
        except Exception as e:
            self.logger.debug(f"Failed to fetch Rumble oEmbed for {url}: {e}")
        
        return None
    
    def parse_txt_file(self, file_path: str) -> List[ChannelDict]:
        """
        Parse a TXT file containing URLs.
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            List of channel dictionaries
        """
        channels = []
        
        try:
            content = self._read_file_content(file_path)
            if not content:
                return []
            
            # Extract URLs from content
            url_pattern = r'https?://[^\s<>"\']+|rtmp://[^\s<>"\']+|rtsp://[^\s<>"\']+|file://[^\s<>"\']+|/[^\s<>"\']+\.[a-zA-Z0-9]+'
            urls = re.findall(url_pattern, content)
            
            # Create channels from URLs
            for idx, url in enumerate(urls, 1):
                url = url.strip()
                if not url:
                    continue
                
                # Extract name from URL
                name = url.split('/')[-1]
                if '?' in name:
                    name = name.split('?')[0]
                name = unquote(name)
                
                channel = ChannelUtils.create_default_channel()
                channel.update({
                    "name": name or f"Link {idx}",
                    "group": "Imported Links",
                    "url": url
                })
                
                channels.append(channel)
            
            self.logger.info(f"Extracted {len(channels)} links from {Path(file_path).name}")
            return channels
            
        except Exception as e:
            self.logger.error(f"Failed to parse TXT file {file_path}: {e}")
            return []
    
    def _read_file_content(self, file_path: str) -> str:
        """
        Read entire file content with encoding detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        try:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Cannot read file {file_path}: {e}")
            return ""
    
    def write_m3u(self, channels: List[ChannelDict], output_path: str) -> bool:
        """
        Write channels to an M3U file.
        
        Args:
            channels: List of channel dictionaries
            output_path: Path to output M3U file
            
        Returns:
            True if successful
        """
        try:
            m3u_content = self.build_m3u_content(channels)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            self.logger.info(f"Wrote {len(channels)} channels to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write M3U file: {e}")
            return False
    
    def build_m3u_content(self, channels: List[ChannelDict]) -> str:
        """
        Build M3U content from channels.
        
        Args:
            channels: List of channel dictionaries
            
        Returns:
            M3U content as string
        """
        m3u = "#EXTM3U\n"
        
        for ch in channels:
            # Build EXTINF line
            extinf = f'#EXTINF:-1 tvg-id="{ch.get("tvg_id", "")}" '
            extinf += f'tvg-name="{ch.get("name", "")}" '
            extinf += f'tvg-logo="{ch.get("logo", "")}" '
            extinf += f'group-title="{ch.get("group", "Other")}",{ch.get("name", "")}\n'
            
            # Add EXTGRP if group exists
            if ch.get("group"):
                extinf += f'#EXTGRP:{ch.get("group", "Other")}\n'
            
            # Add custom tags
            for tag_name, tag_value in ch.get('custom_tags', {}).items():
                extinf += f'#{tag_name}:{tag_value}\n'
            
            # Add URL
            m3u += extinf + ch.get("url", "") + "\n"
            
            # Add backup URLs
            for backup in ch.get("backups", []):
                m3u += backup + "\n"
        
        return m3u
    
    def parse_from_url(self, url: str) -> List[ChannelDict]:
        """
        Parse M3U content from a URL.
        
        Args:
            url: URL to M3U playlist
            
        Returns:
            List of channel dictionaries
        """
        try:
            response = requests.get(url, timeout=15, headers={'User-Agent': 'M3UMatrix/2.0'})
            response.raise_for_status()
            
            # Validate M3U format
            if '#EXTM3U' not in response.text and '#EXTINF' not in response.text:
                self.logger.error("Downloaded content is not a valid M3U playlist")
                return []
            
            # Save to temporary file and parse
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.m3u', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(response.text)
                temp_path = temp_file.name
            
            channels = self.parse_file(temp_path)
            
            # Add source information
            for channel in channels:
                channel['source'] = f"URL: {url}"
            
            # Clean up temp file
            Path(temp_path).unlink()
            
            return channels
            
        except Exception as e:
            self.logger.error(f"Failed to parse M3U from URL {url}: {e}")
            return []