"""
Scheduling Module - Step 5 of refactoring
Scheduling logic with timezone support and conflict detection
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import random
from .cooldown import CooldownManager
from .validation import ConflictDetector, ScheduleValidator

logger = logging.getLogger(__name__)


class ScheduleEngine:
    """Main scheduling engine with timezone and conflict awareness"""
    
    def __init__(self, cooldown_manager: Optional[CooldownManager] = None):
        self.cooldown_manager = cooldown_manager or CooldownManager()
        self.conflict_detector = ConflictDetector()
        self.validator = ScheduleValidator()
    
    def create_schedule_intelligent(self, videos: List[Dict[str, Any]],
                                   start_time: datetime,
                                   total_duration: int,
                                   timezone_str: str = 'UTC',
                                   auto_fill: bool = True,
                                   category_balancing: bool = True) -> Dict[str, Any]:
        """
        Create an intelligent schedule from video list
        
        Args:
            videos: List of videos with metadata
            start_time: Schedule start time
            total_duration: Total duration in seconds
            timezone_str: Timezone for schedule
            auto_fill: Auto-fill gaps with repeated content
            category_balancing: Balance categories across schedule
        
        Returns:
            Generated schedule with events
        """
        if not videos:
            logger.warning("No videos provided for scheduling")
            return {"events": [], "duration": 0, "status": "error"}
        
        # Ensure timezone-aware start time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        events = []
        current_time = start_time.timestamp()
        end_time = current_time + total_duration
        
        # Sort videos by category for balancing
        if category_balancing:
            videos = self._balance_by_category(videos)
        
        # Fill schedule
        video_index = 0
        while current_time < end_time and videos:
            video = videos[video_index % len(videos)]
            duration = video.get('duration', 300)  # Default 5 minutes
            
            # Check cooldown
            if self.cooldown_manager:
                event_time = datetime.fromtimestamp(current_time, tz=timezone.utc)
                if self.cooldown_manager.is_in_cooldown(video['url'], event_time):
                    video_index += 1
                    continue
            
            # Add event
            event = {
                'video_url': video['url'],
                'start': datetime.fromtimestamp(current_time, tz=timezone.utc).isoformat(),
                'duration': duration,
                'title': video.get('title', 'Unknown'),
                'category': video.get('category', 'General')
            }
            
            events.append(event)
            current_time += duration
            video_index += 1
        
        # Validate for conflicts
        is_valid, conflicts = self.conflict_detector.validate_no_conflicts(events)
        if conflicts:
            logger.warning(f"Schedule has {len(conflicts)} conflicts")
        
        return {
            "events": events,
            "start_time": start_time.isoformat(),
            "duration": int(current_time - start_time.timestamp()),
            "video_count": len(events),
            "has_conflicts": not is_valid,
            "status": "success" if events else "empty"
        }
    
    @staticmethod
    def _balance_by_category(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balance videos by category for diversity"""
        categories = {}
        for video in videos:
            cat = video.get('category', 'General')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(video)
        
        # Interleave categories
        balanced = []
        max_len = max(len(v) for v in categories.values()) if categories else 0
        
        for i in range(max_len):
            for cat in categories:
                if i < len(categories[cat]):
                    balanced.append(categories[cat][i])
        
        return balanced
    
    def optimize_for_conflict_detection(self, events: List[Dict[str, Any]],
                                       max_batch_size: int = 1000) -> bool:
        """
        Optimize schedule by processing in batches for large schedules
        
        Args:
            events: List of events
            max_batch_size: Process this many at a time
        
        Returns:
            True if valid, False if conflicts found
        """
        if len(events) <= max_batch_size:
            # Simple validation
            is_valid, conflicts = self.conflict_detector.validate_no_conflicts(events)
            return is_valid
        
        # Batch validation for large schedules
        for i in range(0, len(events), max_batch_size):
            batch = events[i:i+max_batch_size]
            is_valid, conflicts = self.conflict_detector.validate_no_conflicts(batch)
            if not is_valid:
                logger.error(f"Conflicts found in batch {i//max_batch_size}")
                return False
        
        return True
