"""
Channel Model - Data structure and utilities for channel management
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Channel:
    """
    Data model for an individual channel with all its properties.
    This replaces the dictionary-based approach with a structured class.
    """
    
    name: str = "Unknown"
    group: str = "Other"
    url: str = ""
    logo: str = ""
    tvg_id: str = ""
    num: int = 0
    backups: List[str] = field(default_factory=list)
    custom_tags: Dict[str, str] = field(default_factory=dict)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Additional metadata
    source: Optional[str] = None
    logo_cached: bool = False
    last_checked: Optional[datetime] = None
    status: str = "unknown"  # working, broken, timeout, unknown
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert channel to dictionary for compatibility with existing code"""
        return {
            "name": self.name,
            "group": self.group,
            "url": self.url,
            "logo": self.logo,
            "tvg_id": self.tvg_id,
            "num": self.num,
            "backups": self.backups.copy(),
            "custom_tags": self.custom_tags.copy(),
            "uuid": self.uuid,
            "source": self.source,
            "logo_cached": self.logo_cached,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Channel':
        """Create a Channel instance from dictionary"""
        channel_data = data.copy()
        
        # Handle datetime conversion
        if 'last_checked' in channel_data and channel_data['last_checked']:
            if isinstance(channel_data['last_checked'], str):
                try:
                    channel_data['last_checked'] = datetime.fromisoformat(channel_data['last_checked'])
                except:
                    channel_data['last_checked'] = None
        
        # Ensure defaults for missing fields
        channel_data.setdefault('backups', [])
        channel_data.setdefault('custom_tags', {})
        channel_data.setdefault('uuid', str(uuid.uuid4()))
        
        return cls(**channel_data)
    
    def add_backup_url(self, url: str) -> None:
        """Add a backup URL to the channel"""
        if url and url not in self.backups:
            self.backups.append(url)
    
    def set_custom_tag(self, key: str, value: str) -> None:
        """Set a custom tag for the channel"""
        self.custom_tags[key] = value
    
    def get_custom_tag(self, key: str, default: str = "") -> str:
        """Get a custom tag value"""
        return self.custom_tags.get(key, default)
    
    def update_status(self, status: str) -> None:
        """Update channel status and timestamp"""
        self.status = status
        self.last_checked = datetime.now()
    
    def is_rumble_channel(self) -> bool:
        """Check if this is a Rumble channel"""
        return (
            'rumble.com' in self.url.lower() or 
            self.custom_tags.get('PROVIDER', '').upper() == 'RUMBLE'
        )
    
    def get_display_name(self) -> str:
        """Get formatted display name for UI"""
        if self.num:
            return f"{self.num}. {self.name}"
        return self.name
    
    def __str__(self) -> str:
        return f"Channel({self.num}: {self.name} - {self.group})"
    
    def __repr__(self) -> str:
        return f"Channel(name='{self.name}', group='{self.group}', num={self.num})"


# Maintain backward compatibility with dictionary-based code
ChannelDict = Dict[str, Any]


class ChannelUtils:
    """Utility functions for channel operations"""
    
    @staticmethod
    def create_default_channel() -> ChannelDict:
        """Create a default channel dictionary for backward compatibility"""
        return {
            "name": "Unknown",
            "group": "Other",
            "logo": "",
            "tvg_id": "",
            "num": 0,
            "url": "",
            "backups": [],
            "custom_tags": {},
            "uuid": str(uuid.uuid4())
        }
    
    @staticmethod
    def validate_channel_dict(channel: ChannelDict) -> ChannelDict:
        """Ensure a channel dictionary has all required fields"""
        default = ChannelUtils.create_default_channel()
        
        # Merge with defaults
        for key, value in default.items():
            if key not in channel:
                if isinstance(value, list):
                    channel[key] = []
                elif isinstance(value, dict):
                    channel[key] = {}
                else:
                    channel[key] = value
        
        # Ensure UUID exists
        if not channel.get('uuid'):
            channel['uuid'] = str(uuid.uuid4())
        
        return channel
    
    @staticmethod
    def group_channels_by_group(channels: List[ChannelDict]) -> Dict[str, List[ChannelDict]]:
        """Group channels by their group field"""
        groups = {}
        for channel in channels:
            group = channel.get('group', 'Other')
            if group not in groups:
                groups[group] = []
            groups[group].append(channel)
        return groups
    
    @staticmethod
    def normalize_group_name(group_name: str) -> str:
        """Normalize group names for consistency"""
        if not group_name:
            return "Other"
        
        # Common normalizations
        normalized = group_name.strip().title()
        
        # Map common variations
        group_map = {
            'Uk': 'UK',
            'Usa': 'USA',
            'Us': 'USA',
            'Ppv': 'PPV',
            'Vod': 'VOD',
            'Hd': 'HD',
            'Sd': 'SD',
            '24/7': '24-7',
            '24_7': '24-7',
            'Tv': 'TV'
        }
        
        for old, new in group_map.items():
            if normalized.upper() == old.upper():
                return new
        
        return normalized
    
    @staticmethod
    def extract_channel_number(channel_name: str) -> Optional[int]:
        """Extract channel number from channel name if present"""
        import re
        
        # Look for patterns like "1. ESPN" or "#1 ESPN" or "CH1 ESPN"
        patterns = [
            r'^(\d+)\.\s*',  # "1. ESPN"
            r'^#(\d+)\s+',   # "#1 ESPN"
            r'^CH(\d+)\s+',  # "CH1 ESPN"
            r'^\[(\d+)\]',   # "[1] ESPN"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, channel_name, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None