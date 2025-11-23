"""
Scheduling engine for ScheduleFlow

Extracted from M3U_MATRIX_PRO.py.create_smart_schedule method.
Generates multi-day schedules with intelligent channel rotation.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import random
import logging

from .models import Channel, Schedule, ScheduleEntry


logger = logging.getLogger(__name__)


class ScheduleEngine:
    """Generates intelligent schedules from channel lists"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.logger = logger
    
    def create_smart_schedule(
        self,
        channels: List[Channel],
        show_duration: int = 30,
        num_days: int = 7,
        max_consecutive: int = 3
    ) -> Schedule:
        """
        Create intelligent schedule with balanced rotation.
        
        Args:
            channels: List of channels to schedule
            show_duration: Minutes per show (default 30)
            num_days: Number of days to schedule (default 7)
            max_consecutive: Max consecutive repeats of same channel (default 3)
        
        Returns:
            Schedule object with entries
        """
        if not channels:
            self.logger.warning("No channels provided for scheduling")
            return Schedule()
        
        schedule = Schedule(num_days=num_days)
        
        # Group channels by category
        groups = self._group_channels(channels)
        self.logger.info(f"Grouped {len(channels)} channels into {len(groups)} categories")
        
        # Generate entries
        current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        minutes_per_day = 24 * 60
        
        for day in range(num_days):
            day_start = current_time + timedelta(days=day)
            current_slot = day_start
            
            # Track consecutive uses to avoid repetition
            consecutive_count = defaultdict(int)
            last_channel = None
            
            while (current_slot - day_start).total_seconds() < minutes_per_day * 60:
                # Select next channel with balancing
                next_channel = self._select_next_channel(
                    channels=channels,
                    groups=groups,
                    last_channel=last_channel,
                    consecutive_count=consecutive_count,
                    max_consecutive=max_consecutive
                )
                
                if next_channel is None:
                    break
                
                # Create schedule entry
                end_slot = current_slot + timedelta(minutes=show_duration)
                entry = ScheduleEntry(
                    channel=next_channel,
                    start_time=current_slot,
                    end_time=end_slot,
                    show_name=next_channel.name,
                    duration_minutes=show_duration
                )
                schedule.add_entry(entry)
                
                # Update tracking
                last_channel = next_channel
                consecutive_count[next_channel.uuid] += 1
                if next_channel.uuid != last_channel.uuid:
                    consecutive_count[next_channel.uuid] = 1
                
                current_slot = end_slot
        
        self.logger.info(f"Created schedule with {len(schedule.entries)} entries")
        return schedule
    
    def _group_channels(self, channels: List[Channel]) -> Dict[str, List[Channel]]:
        """Group channels by category"""
        groups = defaultdict(list)
        for channel in channels:
            group = channel.group or "Other"
            groups[group].append(channel)
        return groups
    
    def _select_next_channel(
        self,
        channels: List[Channel],
        groups: Dict[str, List[Channel]],
        last_channel: Channel,
        consecutive_count: Dict[str, int],
        max_consecutive: int
    ) -> Channel:
        """Select next channel with intelligent balancing"""
        
        # Filter out channels that would exceed max consecutive
        available = [
            c for c in channels
            if consecutive_count.get(c.uuid, 0) < max_consecutive or c != last_channel
        ]
        
        if not available:
            available = channels
        
        # Prefer different groups
        if last_channel:
            different_group = [
                c for c in available
                if c.group != last_channel.group
            ]
            if different_group:
                return random.choice(different_group)
        
        return random.choice(available) if available else channels[0]


def extract_show_name(channel_name: str) -> str:
    """Extract show name from channel name (remove group prefix)"""
    # Remove common prefixes
    for prefix in ['[', '(', '|']:
        if prefix in channel_name:
            return channel_name.split(prefix)[0].strip()
    return channel_name
