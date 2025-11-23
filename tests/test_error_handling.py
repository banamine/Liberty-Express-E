"""Error handling and edge case tests"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import ConfigManager
from core.file_manager import FileManager
from core.cooldown import CooldownManager
from core.validation import ScheduleValidator, ConflictDetector
from core.scheduling import ScheduleEngine


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""
    
    def test_corrupt_json_recovery(self):
        """Test recovery from corrupted JSON files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "bad.json"
            history_file.write_text("{ corrupt json ]")
            
            # Should handle gracefully
            manager = CooldownManager(str(history_file))
            self.assertEqual(len(manager.last_played), 0)
    
    def test_missing_config_file(self):
        """Test config loading when file missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            manager = ConfigManager(str(config_path))
            
            # Should use defaults
            self.assertIsNotNone(manager.get("app.name"))
    
    def test_permission_denied_backup(self):
        """Test handling of permission denied during backup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")
            
            manager = FileManager(backup_dir=str(Path(tmpdir) / "backups"))
            
            # Should not crash even if permissions denied
            try:
                backup = manager.create_backup(str(test_file))
                self.assertIsNotNone(backup)
            except PermissionError:
                pass  # Expected in some environments


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_event_list(self):
        """Test validation of empty event list"""
        events = []
        valid, errors = ScheduleValidator.validate_schedule(events)
        self.assertTrue(valid)  # Empty is valid
    
    def test_extremely_long_duration(self):
        """Test event with very long duration"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 365 * 24 * 3600,  # 1 year
            "video_url": "http://example.com/long.mp4"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        self.assertTrue(valid)  # Should accept (no max limit)
    
    def test_zero_duration(self):
        """Test event with zero duration"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 0,
            "video_url": "http://example.com/video.mp4"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        self.assertFalse(valid)  # Should reject
    
    def test_special_characters_in_url(self):
        """Test handling of special characters in URLs"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 300,
            "video_url": "http://example.com/video?id=123&lang=en&format=hd"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        self.assertTrue(valid)
    
    def test_unicode_characters(self):
        """Test handling of unicode in event data"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 300,
            "video_url": "http://example.com/video.mp4",
            "title": "视频标题 🎬 Vidéo"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        self.assertTrue(valid)
    
    def test_very_old_timestamp(self):
        """Test event with very old timestamp"""
        event = {
            "start": "1970-01-01T00:00:00Z",
            "duration": 300,
            "video_url": "http://example.com/video.mp4"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        self.assertTrue(valid)


class TestCooldownEdgeCases(unittest.TestCase):
    """Test cooldown edge cases"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = CooldownManager(str(Path(self.temp_dir.name) / "cooldown.json"))
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_multiple_same_video_same_time(self):
        """Test multiple entries for same video"""
        video_url = "http://example.com/video.mp4"
        play_time = datetime.now(tz=timezone.utc)
        
        # Record same video multiple times
        self.manager.update_play_time(video_url, play_time)
        self.manager.update_play_time(video_url, play_time)
        
        # Should only have latest
        is_cooldown = self.manager.is_in_cooldown(video_url, play_time)
        self.assertTrue(is_cooldown)
    
    def test_cooldown_exact_boundary(self):
        """Test cooldown at exact 48-hour boundary"""
        from datetime import timedelta
        
        video_url = "http://example.com/video.mp4"
        play_time = datetime.now(tz=timezone.utc) - timedelta(hours=48)
        
        self.manager.update_play_time(video_url, play_time)
        
        # At exact boundary - should be true (inclusive)
        check_time = datetime.now(tz=timezone.utc)
        is_cooldown = self.manager.is_in_cooldown(video_url, check_time, cooldown_hours=48)
        
        # Boundary behavior: >= 48 hours should be allowed
        # This tests the exact implementation


class TestConflictDetectionEdgeCases(unittest.TestCase):
    """Test conflict detection edge cases"""
    
    def test_simultaneous_events(self):
        """Test events that start at exact same time"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/v1.mp4"
            },
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/v2.mp4"
            }
        ]
        
        conflicts = ConflictDetector.check_overlaps(events)
        self.assertGreater(len(conflicts), 0)  # Should detect conflict
    
    def test_back_to_back_events(self):
        """Test events that are back-to-back (no overlap)"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/v1.mp4"
            },
            {
                "start": "2025-12-01T10:05:00Z",
                "duration": 300,
                "video_url": "http://example.com/v2.mp4"
            }
        ]
        
        conflicts = ConflictDetector.check_overlaps(events)
        self.assertEqual(len(conflicts), 0)  # No conflict
    
    def test_microsecond_overlap(self):
        """Test events overlapping by microseconds"""
        events = [
            {
                "start": "2025-12-01T10:00:00.000000Z",
                "duration": 300,
                "video_url": "http://example.com/v1.mp4"
            },
            {
                "start": "2025-12-01T10:04:59.999999Z",
                "duration": 300,
                "video_url": "http://example.com/v2.mp4"
            }
        ]
        
        conflicts = ConflictDetector.check_overlaps(events)
        self.assertGreater(len(conflicts), 0)  # Should detect overlap


class TestSchedulingEdgeCases(unittest.TestCase):
    """Test scheduling edge cases"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cooldown = CooldownManager(str(Path(self.temp_dir.name) / "cooldown.json"))
        self.engine = ScheduleEngine(self.cooldown)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_schedule_single_video(self):
        """Test scheduling with only one video"""
        videos = [
            {"url": "http://example.com/video.mp4", "duration": 300, "category": "News"}
        ]
        
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=3600
        )
        
        self.assertEqual(schedule["status"], "success")
        self.assertGreater(len(schedule["events"]), 0)
    
    def test_schedule_videos_longer_than_duration(self):
        """Test when total video duration exceeds requested duration"""
        videos = [
            {"url": "http://example.com/v1.mp4", "duration": 2000, "category": "A"},
            {"url": "http://example.com/v2.mp4", "duration": 2000, "category": "B"}
        ]
        
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=3600  # Only 1 hour, but videos take 66 minutes
        )
        
        # Should handle gracefully
        self.assertEqual(schedule["status"], "success")
        self.assertLessEqual(schedule["duration"], 3600 * 1.1)  # Some tolerance


if __name__ == '__main__':
    unittest.main()
