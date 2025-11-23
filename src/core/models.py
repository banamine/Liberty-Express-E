"""
Data models for ScheduleFlow

Extracted from M3U_MATRIX_PRO.py class to support modular architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass
class Channel:
    """Single channel/stream definition"""
    name: str
    url: str
    group: str = "Other"
    logo: str = ""
    tvg_id: str = ""
    tvg_name: str = ""
    num: int = 0
    backups: List[str] = field(default_factory=list)
    custom_tags: Dict[str, str] = field(default_factory=dict)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "unknown"  # working, broken, timeout
    last_checked: Optional[datetime] = None
    logo_cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'url': self.url,
            'group': self.group,
            'logo': self.logo,
            'tvg_id': self.tvg_id,
            'tvg_name': self.tvg_name,
            'num': self.num,
            'backups': self.backups,
            'custom_tags': self.custom_tags,
            'uuid': self.uuid,
            'status': self.status,
        }


@dataclass
class ScheduleEntry:
    """Single entry in a schedule"""
    channel: Channel
    start_time: datetime
    end_time: datetime
    show_name: str
    duration_minutes: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'channel': self.channel.to_dict(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'show_name': self.show_name,
            'duration_minutes': self.duration_minutes,
        }


@dataclass
class Schedule:
    """Multi-day schedule of channels"""
    entries: List[ScheduleEntry] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.now)
    num_days: int = 7
    
    def add_entry(self, entry: ScheduleEntry):
        """Add an entry to the schedule"""
        self.entries.append(entry)
    
    def get_entries_for_day(self, day_index: int) -> List[ScheduleEntry]:
        """Get all entries for a specific day"""
        return [e for e in self.entries if e.start_time.day == day_index]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entries': [e.to_dict() for e in self.entries],
            'start_date': self.start_date.isoformat(),
            'num_days': self.num_days,
        }


@dataclass
class ValidationResult:
    """Result of validating a channel"""
    channel_uuid: str
    channel_name: str
    status: str  # working, broken, timeout
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'channel_uuid': self.channel_uuid,
            'channel_name': self.channel_name,
            'status': self.status,
            'status_code': self.status_code,
            'error_message': self.error_message,
            'response_time_ms': self.response_time_ms,
        }
