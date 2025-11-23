"""Unit tests for scheduling module"""

import unittest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.scheduling import ScheduleEngine
from core.cooldown import CooldownManager
import tempfile


class TestScheduleEngine(unittest.TestCase):
    """Test ScheduleEngine functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cooldown = CooldownManager(str(Path(self.temp_dir.name) / "cooldown.json"))
        self.engine = ScheduleEngine(self.cooldown)
    
    def tearDown(self):
        """Cleanup test fixtures"""
        self.temp_dir.cleanup()
    
    def test_create_schedule_intelligent(self):
        """Test creating an intelligent schedule"""
        videos = [
            {"url": "http://example.com/video1.mp4", "duration": 300, "category": "News"},
            {"url": "http://example.com/video2.mp4", "duration": 600, "category": "Sports"}
        ]
        
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=3600,
            timezone_str='UTC'
        )
        
        self.assertEqual(schedule["status"], "success")
        self.assertGreater(len(schedule["events"]), 0)
        self.assertFalse(schedule["has_conflicts"])
    
    def test_schedule_with_empty_videos(self):
        """Test creating schedule with no videos"""
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=[],
            start_time=start_time,
            total_duration=3600
        )
        
        self.assertEqual(schedule["status"], "error")
        self.assertEqual(len(schedule["events"]), 0)
    
    def test_category_balancing(self):
        """Test category balancing in schedule"""
        videos = [
            {"url": "http://example.com/v1.mp4", "duration": 300, "category": "A"},
            {"url": "http://example.com/v2.mp4", "duration": 300, "category": "B"},
            {"url": "http://example.com/v3.mp4", "duration": 300, "category": "A"}
        ]
        
        balanced = self.engine._balance_by_category(videos)
        
        # Should have same number of videos, different order
        self.assertEqual(len(balanced), 3)
    
    def test_optimize_for_conflict_detection(self):
        """Test conflict detection optimization"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/v1.mp4"
            },
            {
                "start": "2025-12-01T10:10:00Z",
                "duration": 300,
                "video_url": "http://example.com/v2.mp4"
            }
        ]
        
        is_valid = self.engine.optimize_for_conflict_detection(events)
        
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
