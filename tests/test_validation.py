"""Unit tests for validation module"""

import unittest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.validation import ScheduleValidator, DuplicateDetector, ConflictDetector


class TestScheduleValidator(unittest.TestCase):
    """Test ScheduleValidator functionality"""
    
    def test_validate_valid_event(self):
        """Test validating a valid event"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 300,
            "video_url": "http://example.com/video.mp4"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        
        self.assertTrue(valid)
        self.assertIsNone(error)
    
    def test_validate_missing_field(self):
        """Test validating event with missing field"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": 300
            # Missing video_url
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        
        self.assertFalse(valid)
        self.assertIsNotNone(error)
    
    def test_validate_invalid_duration(self):
        """Test validating event with invalid duration"""
        event = {
            "start": "2025-12-01T10:00:00Z",
            "duration": -100,  # Negative duration
            "video_url": "http://example.com/video.mp4"
        }
        
        valid, error = ScheduleValidator.validate_event(event)
        
        self.assertFalse(valid)
    
    def test_validate_full_schedule(self):
        """Test validating complete schedule"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/video1.mp4"
            },
            {
                "start": "2025-12-01T10:30:00Z",
                "duration": 300,
                "video_url": "http://example.com/video2.mp4"
            }
        ]
        
        valid, errors = ScheduleValidator.validate_schedule(events)
        
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)


class TestDuplicateDetector(unittest.TestCase):
    """Test DuplicateDetector functionality"""
    
    def test_no_duplicates(self):
        """Test detecting no duplicates"""
        events = [
            {"video_url": "http://example.com/video1.mp4"},
            {"video_url": "http://example.com/video2.mp4"}
        ]
        
        duplicates = DuplicateDetector.find_duplicates(events)
        
        self.assertEqual(len(duplicates), 0)
    
    def test_exact_duplicates(self):
        """Test detecting exact duplicate URLs"""
        events = [
            {"video_url": "http://example.com/video1.mp4"},
            {"video_url": "http://example.com/video1.mp4"}
        ]
        
        duplicates = DuplicateDetector.find_duplicates(events)
        
        self.assertGreater(len(duplicates), 0)
        self.assertEqual(duplicates[0]["duplicate_type"], "exact")
    
    def test_content_hash(self):
        """Test content hashing"""
        content = "test content"
        hash1 = DuplicateDetector.get_content_hash(content, "md5")
        hash2 = DuplicateDetector.get_content_hash(content, "md5")
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 32)  # MD5 is 32 hex chars


class TestConflictDetector(unittest.TestCase):
    """Test ConflictDetector functionality"""
    
    def test_no_overlaps(self):
        """Test detecting no overlaps"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/video1.mp4"
            },
            {
                "start": "2025-12-01T10:30:00Z",
                "duration": 300,
                "video_url": "http://example.com/video2.mp4"
            }
        ]
        
        conflicts = ConflictDetector.check_overlaps(events)
        
        self.assertEqual(len(conflicts), 0)
    
    def test_overlapping_events(self):
        """Test detecting overlapping events"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 600,  # 10 minutes
                "video_url": "http://example.com/video1.mp4"
            },
            {
                "start": "2025-12-01T10:05:00Z",  # 5 minutes later (overlaps)
                "duration": 300,
                "video_url": "http://example.com/video2.mp4"
            }
        ]
        
        conflicts = ConflictDetector.check_overlaps(events)
        
        self.assertGreater(len(conflicts), 0)
    
    def test_validate_no_conflicts(self):
        """Test validation method"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": "http://example.com/video1.mp4"
            }
        ]
        
        valid, conflicts = ConflictDetector.validate_no_conflicts(events)
        
        self.assertTrue(valid)
        self.assertEqual(len(conflicts), 0)


if __name__ == '__main__':
    unittest.main()
