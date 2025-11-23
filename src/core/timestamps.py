"""
Timestamp Parsing Module - from M3U_Matrix_Pro refactoring
Parse and normalize timestamps to UTC with timezone support
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import pendulum

logger = logging.getLogger(__name__)


class TimestampParser:
    """Parse and normalize timestamps to UTC"""
    
    @staticmethod
    def parse_iso8601(timestamp_str: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp and return as UTC datetime"""
        if not timestamp_str:
            return None
        
        try:
            # Handle various formats
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            
            # Use pendulum for robust parsing
            dt = pendulum.parse(timestamp_str)
            
            # Convert to UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.in_tz('UTC')
            
            return dt.datetime
        except Exception as e:
            logger.error(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return None
    
    @staticmethod
    def to_iso8601(dt: datetime, include_timezone: bool = True) -> str:
        """Convert datetime to ISO 8601 string"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        if include_timezone:
            return dt.isoformat()
        else:
            return dt.isoformat(timespec='seconds').split('+')[0]
    
    @staticmethod
    def normalize_to_utc(dt: datetime) -> datetime:
        """Ensure datetime is in UTC"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        else:
            return dt.astimezone(timezone.utc)
    
    @staticmethod
    def parse_with_timezone(timestamp_str: str, 
                           default_tz: str = 'UTC') -> Optional[datetime]:
        """Parse timestamp with fallback to default timezone"""
        parsed = TimestampParser.parse_iso8601(timestamp_str)
        if parsed:
            return parsed
        
        try:
            # Fallback: assume timestamp is in default timezone
            dt = pendulum.parse(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.in_tz(default_tz)
            return dt.in_tz('UTC').datetime
        except Exception as e:
            logger.warning(f"Failed to parse with fallback: {e}")
            return None
