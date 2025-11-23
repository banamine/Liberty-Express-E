"""
Validation Module - from M3U_Matrix_Pro refactoring
Schedule validation, duplicate detection, and conflict detection
"""

import logging
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ScheduleValidator:
    """Validate schedule structure and content"""
    
    REQUIRED_FIELDS = ['start', 'duration', 'video_url']
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a single schedule event"""
        # Check required fields
        for field in ScheduleValidator.REQUIRED_FIELDS:
            if field not in event:
                return False, f"Missing required field: {field}"
        
        # Validate start time (ISO 8601)
        try:
            datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        except (ValueError, KeyError):
            return False, "Invalid start time format"
        
        # Validate duration
        try:
            duration = int(event['duration'])
            if duration <= 0:
                return False, "Duration must be positive"
        except (ValueError, KeyError):
            return False, "Invalid duration"
        
        return True, None
    
    @staticmethod
    def validate_schedule(events: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, str]]]:
        """Validate entire schedule"""
        errors = []
        
        for i, event in enumerate(events):
            valid, error = ScheduleValidator.validate_event(event)
            if not valid:
                errors.append({
                    'event_index': i,
                    'error': error
                })
        
        return len(errors) == 0, errors


class DuplicateDetector:
    """Detect duplicate videos in schedule"""
    
    @staticmethod
    def get_content_hash(content: str, method: str = 'md5') -> str:
        """Calculate hash of content"""
        if method == 'md5':
            return hashlib.md5(content.encode()).hexdigest()
        elif method == 'sha256':
            return hashlib.sha256(content.encode()).hexdigest()
        else:
            return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def find_duplicates(events: List[Dict[str, Any]], 
                       tolerance_hours: int = 24,
                       ignore_case: bool = True) -> List[Dict[str, Any]]:
        """Find duplicate videos in schedule"""
        duplicates = []
        seen = {}
        
        for i, event in enumerate(events):
            video_url = event.get('video_url', '').strip()
            
            if ignore_case:
                video_url = video_url.lower()
            
            if video_url in seen:
                duplicates.append({
                    'first_index': seen[video_url],
                    'second_index': i,
                    'video_url': event.get('video_url'),
                    'duplicate_type': 'exact'
                })
            else:
                seen[video_url] = i
        
        return duplicates


class ConflictDetector:
    """Detect scheduling conflicts"""
    
    @staticmethod
    def check_overlaps(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for overlapping events"""
        conflicts = []
        
        # Sort by start time
        sorted_events = sorted(events, 
                              key=lambda e: datetime.fromisoformat(
                                  e['start'].replace('Z', '+00:00')))
        
        for i in range(len(sorted_events) - 1):
            event1 = sorted_events[i]
            event2 = sorted_events[i + 1]
            
            try:
                start1 = datetime.fromisoformat(event1['start'].replace('Z', '+00:00'))
                start2 = datetime.fromisoformat(event2['start'].replace('Z', '+00:00'))
                
                duration1 = int(event1.get('duration', 0))
                end1 = start1.timestamp() + duration1
                
                if end1 > start2.timestamp():
                    conflicts.append({
                        'event_1_index': i,
                        'event_2_index': i + 1,
                        'overlap_seconds': int(end1 - start2.timestamp()),
                        'event_1': event1.get('video_url'),
                        'event_2': event2.get('video_url')
                    })
            except (ValueError, TypeError):
                pass
        
        return conflicts
    
    @staticmethod
    def validate_no_conflicts(events: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate that schedule has no conflicts"""
        conflicts = ConflictDetector.check_overlaps(events)
        return len(conflicts) == 0, conflicts
