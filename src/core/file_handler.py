"""
M3U file parsing and file operations for ScheduleFlow

Extracted from M3U_MATRIX_PRO.py parsing methods.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional
from .models import Channel

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles M3U parsing and playlist file operations"""
    
    def __init__(self):
        """Initialize file handler"""
        self.logger = logger
    
    def parse_m3u_file(self, file_path: str) -> List[Channel]:
        """
        Parse M3U playlist file and return list of channels.
        
        Supports:
        - #EXTINF format
        - #EXTGRP groups
        - Custom tags
        - Multiple encodings (UTF-8, Latin-1)
        
        Args:
            file_path: Path to M3U file
        
        Returns:
            List of Channel objects
        """
        channels = []
        current_channel = None
        custom_tags = {}
        
        try:
            # Try UTF-8 first, fallback to Latin-1
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
        except Exception as e:
            self.logger.error(f"Cannot read file {file_path}: {e}")
            return []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and M3U headers
            if not line or line in ("#EXTM3U", "#EXTMM3U"):
                i += 1
                continue
            
            # Parse EXTINF line (channel info)
            if line.startswith("#EXTINF") or line.startswith("#EXTM:") or line.startswith("#EXTMM:"):
                current_channel = self._parse_extinf_line(line)
                
                # Check next line for EXTGRP (group)
                if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                    current_channel["group"] = lines[i + 1].split(":", 1)[1].strip()
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
            
            # Parse URL (must come after #EXTINF)
            if current_channel and not line.startswith("#"):
                current_channel["url"] = line.strip()
                current_channel["custom_tags"] = custom_tags.copy()
                
                # Create Channel object
                channel = Channel(
                    name=current_channel.get("name", "Unknown"),
                    url=current_channel.get("url", ""),
                    group=current_channel.get("group", "Other"),
                    logo=current_channel.get("logo", ""),
                    tvg_id=current_channel.get("tvg_id", ""),
                    tvg_name=current_channel.get("tvg_name", ""),
                    custom_tags=custom_tags.copy()
                )
                channels.append(channel)
                
                current_channel = None
                custom_tags = {}
            
            i += 1
        
        self.logger.info(f"Parsed {len(channels)} channels from {file_path}")
        return channels
    
    def _parse_extinf_line(self, line: str) -> Dict[str, str]:
        """Parse #EXTINF line and extract attributes"""
        channel = {
            "name": "Unknown",
            "group": "Other",
            "logo": "",
            "tvg_id": "",
            "tvg_name": "",
            "url": ""
        }
        
        # Extract attributes using regex
        attr_pattern = r'([a-zA-Z-]+)="([^"]*)"'
        attributes = dict(re.findall(attr_pattern, line))
        
        # Extract name (after comma)
        name_part = line.split(',')[-1].strip()
        if name_part:
            channel["name"] = name_part
        
        # Map attributes
        if "tvg-name" in attributes:
            channel["tvg_name"] = attributes["tvg-name"]
            channel["name"] = attributes["tvg-name"]
        if "group-title" in attributes:
            channel["group"] = attributes["group-title"]
        if "tvg-logo" in attributes:
            channel["logo"] = attributes["tvg-logo"]
        if "tvg-id" in attributes:
            channel["tvg_id"] = attributes["tvg-id"]
        
        return channel
    
    def build_m3u_content(self, channels: List[Channel]) -> str:
        """
        Build M3U file content from channels.
        
        Args:
            channels: List of Channel objects
        
        Returns:
            M3U format string
        """
        lines = ["#EXTM3U"]
        
        for channel in channels:
            # Build EXTINF line
            extinf_attrs = []
            
            if channel.tvg_id:
                extinf_attrs.append(f'tvg-id="{channel.tvg_id}"')
            if channel.logo:
                extinf_attrs.append(f'tvg-logo="{channel.logo}"')
            if channel.tvg_name:
                extinf_attrs.append(f'tvg-name="{channel.tvg_name}"')
            if channel.group:
                extinf_attrs.append(f'group-title="{channel.group}"')
            
            attrs_str = " ".join(extinf_attrs)
            if attrs_str:
                extinf_line = f"#EXTINF:-1 {attrs_str},{channel.name}"
            else:
                extinf_line = f"#EXTINF:-1,{channel.name}"
            
            lines.append(extinf_line)
            lines.append(channel.url)
            lines.append("")  # Blank line between entries
        
        return "\n".join(lines)
    
    def save_m3u_file(self, file_path: str, channels: List[Channel]) -> bool:
        """
        Save channels to M3U file.
        
        Args:
            file_path: Output file path
            channels: List of Channel objects
        
        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.build_m3u_content(channels)
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Saved {len(channels)} channels to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save M3U file: {e}")
            return False
