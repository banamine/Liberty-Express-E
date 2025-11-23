"""
Cooldown Management Module - from M3U_Matrix_Pro refactoring
Manages 48-hour cooldown constraints for video playback
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class CooldownManager:
    """Manage persistent cooldown history across sessions"""
    
    def __init__(self, history_file: str = "schedules/cooldown_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        self.load_history()
    
    def load_history(self):
        """Load cooldown history from file"""
        self.last_played = {}
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for video_url, timestamp_str in data.items():
                        try:
                            dt = datetime.fromisoformat(timestamp_str)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            self.last_played[video_url] = dt
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Skipping malformed timestamp for '{video_url}': {e}")
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted cooldown history file: {e}")
                self.last_played = {}
    
    def save_history(self):
        """Save cooldown history to file"""
        data = {}
        for video_url, dt in self.last_played.items():
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            data[video_url] = dt.isoformat()
        
        try:
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved cooldown history: {len(data)} entries")
        except IOError as e:
            logger.error(f"Failed to save cooldown history: {e}")
    
    def update_play_time(self, video_url: str, play_time: datetime):
        """Record that a video was played"""
        if play_time.tzinfo is None:
            play_time = play_time.replace(tzinfo=timezone.utc)
        else:
            play_time = play_time.astimezone(timezone.utc)
        self.last_played[video_url] = play_time
        self.save_history()
    
    def is_in_cooldown(self, video_url: str, check_time: datetime, 
                       cooldown_hours: int = 48) -> bool:
        """Check if video is in cooldown period"""
        if video_url not in self.last_played:
            return False
        
        last_play = self.last_played[video_url]
        if check_time.tzinfo is None:
            check_time = check_time.replace(tzinfo=timezone.utc)
        else:
            check_time = check_time.astimezone(timezone.utc)
        
        cooldown_end = last_play + timedelta(hours=cooldown_hours)
        return check_time < cooldown_end
    
    def get_cooldown_end_time(self, video_url: str, 
                             cooldown_hours: int = 48) -> Optional[datetime]:
        """Get when cooldown expires for a video"""
        if video_url not in self.last_played:
            return None
        
        last_play = self.last_played[video_url]
        return last_play + timedelta(hours=cooldown_hours)


class CooldownValidator:
    """Validate schedule compliance with cooldown constraints"""
    
    @staticmethod
    def validate_schedule_cooldown(events: List[Dict[str, Any]], 
                                  cooldown_manager: CooldownManager,
                                  cooldown_hours: int = 48) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Validate that a schedule doesn't violate cooldown constraints
        
        Returns: (is_valid, violations)
        """
        violations = []
        
        # Sort events by start time
        sorted_events = sorted(events, 
                              key=lambda e: datetime.fromisoformat(
                                  e['start'].replace('Z', '+00:00')))
        
        for event in sorted_events:
            video_url = event.get('video_url') or event.get('url')
            start_str = event.get('start')
            
            if not video_url or not start_str:
                continue
            
            try:
                start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                
                if cooldown_manager.is_in_cooldown(video_url, start_time, cooldown_hours):
                    cooldown_end = cooldown_manager.get_cooldown_end_time(video_url, cooldown_hours)
                    violations.append({
                        "video_url": video_url,
                        "scheduled_time": start_str,
                        "cooldown_end_time": cooldown_end.isoformat() if cooldown_end else "Unknown"
                    })
            except (ValueError, TypeError, AttributeError):
                pass
        
        return len(violations) == 0, violations
