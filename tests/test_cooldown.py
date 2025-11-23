"""Unit tests for cooldown module"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.cooldown import CooldownManager, CooldownValidator


class TestCooldownManager(unittest.TestCase):
    """Test CooldownManager functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_file = Path(self.temp_dir.name) / "cooldown.json"
        self.manager = CooldownManager(str(self.history_file))
    
    def tearDown(self):
        """Cleanup test fixtures"""
        self.temp_dir.cleanup()
    
    def test_update_and_check_cooldown(self):
        """Test recording and checking cooldown"""
        video_url = "http://example.com/video1.mp4"
        play_time = datetime.now(tz=timezone.utc)
        
        # Update play time
        self.manager.update_play_time(video_url, play_time)
        
        # Check if in cooldown (should be true immediately)
        check_time = play_time + timedelta(hours=24)
        is_cooldown = self.manager.is_in_cooldown(video_url, check_time)
        self.assertTrue(is_cooldown)
    
    def test_cooldown_expiration(self):
        """Test that cooldown expires after the period"""
        video_url = "http://example.com/video2.mp4"
        play_time = datetime.now(tz=timezone.utc) - timedelta(hours=49)
        
        # Mark as played 49 hours ago
        self.manager.update_play_time(video_url, play_time)
        
        # Check if in cooldown now (should be false, >48 hours passed)
        check_time = datetime.now(tz=timezone.utc)
        is_cooldown = self.manager.is_in_cooldown(video_url, check_time, cooldown_hours=48)
        self.assertFalse(is_cooldown)
    
    def test_get_cooldown_end_time(self):
        """Test getting cooldown end time"""
        video_url = "http://example.com/video3.mp4"
        play_time = datetime.now(tz=timezone.utc)
        
        self.manager.update_play_time(video_url, play_time)
        end_time = self.manager.get_cooldown_end_time(video_url, cooldown_hours=48)
        
        self.assertIsNotNone(end_time)
        expected_end = play_time + timedelta(hours=48)
        self.assertEqual(end_time.replace(microsecond=0), expected_end.replace(microsecond=0))
    
    def test_persistence(self):
        """Test that cooldown history persists across sessions"""
        video_url = "http://example.com/video4.mp4"
        play_time = datetime.now(tz=timezone.utc)
        
        # Record in first manager
        self.manager.update_play_time(video_url, play_time)
        
        # Load in second manager from same file
        manager2 = CooldownManager(str(self.history_file))
        is_cooldown = manager2.is_in_cooldown(video_url, play_time + timedelta(hours=24))
        
        self.assertTrue(is_cooldown)


class TestCooldownValidator(unittest.TestCase):
    """Test CooldownValidator functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = CooldownManager(str(Path(self.temp_dir.name) / "cooldown.json"))
        self.validator = CooldownValidator()
    
    def tearDown(self):
        """Cleanup test fixtures"""
        self.temp_dir.cleanup()
    
    def test_validate_schedule_no_violations(self):
        """Test validating schedule with no cooldown violations"""
        # Clear manager
        self.manager.last_played = {}
        
        events = [
            {
                "video_url": "http://example.com/video1.mp4",
                "start": "2025-12-01T10:00:00Z"
            }
        ]
        
        valid, violations = self.validator.validate_schedule_cooldown(events, self.manager)
        
        self.assertTrue(valid)
        self.assertEqual(len(violations), 0)
    
    def test_validate_schedule_with_violations(self):
        """Test validating schedule with cooldown violations"""
        video_url = "http://example.com/video1.mp4"
        play_time = datetime.fromisoformat("2025-12-01T10:00:00+00:00")
        
        # Mark video as recently played
        self.manager.update_play_time(video_url, play_time)
        
        # Try to schedule it again within cooldown
        events = [
            {
                "video_url": video_url,
                "start": "2025-12-02T10:00:00Z"  # Next day, within 48-hour cooldown
            }
        ]
        
        valid, violations = self.validator.validate_schedule_cooldown(events, self.manager)
        
        self.assertFalse(valid)
        self.assertGreater(len(violations), 0)


if __name__ == '__main__':
    unittest.main()
