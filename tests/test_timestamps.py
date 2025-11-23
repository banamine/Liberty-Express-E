"""Unit tests for timestamps module"""

import unittest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.timestamps import TimestampParser


class TestTimestampParser(unittest.TestCase):
    """Test TimestampParser functionality"""
    
    def test_parse_iso8601_with_z(self):
        """Test parsing ISO 8601 with Z suffix"""
        timestamp = "2025-12-01T10:00:00Z"
        parsed = TimestampParser.parse_iso8601(timestamp)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2025)
        self.assertEqual(parsed.month, 12)
        self.assertEqual(parsed.day, 1)
    
    def test_parse_iso8601_with_offset(self):
        """Test parsing ISO 8601 with timezone offset"""
        timestamp = "2025-12-01T10:00:00+05:00"
        parsed = TimestampParser.parse_iso8601(timestamp)
        
        self.assertIsNotNone(parsed)
        self.assertIsNotNone(parsed.tzinfo)
    
    def test_parse_iso8601_utc_conversion(self):
        """Test that timestamp is converted to UTC"""
        timestamp = "2025-12-01T15:00:00+05:00"  # 3 PM +5 hours
        parsed = TimestampParser.parse_iso8601(timestamp)
        
        # Should be 10 AM UTC
        self.assertEqual(parsed.hour, 10)
        self.assertEqual(parsed.tzinfo, timezone.utc)
    
    def test_parse_invalid_timestamp(self):
        """Test parsing invalid timestamp"""
        timestamp = "not-a-valid-timestamp"
        parsed = TimestampParser.parse_iso8601(timestamp)
        
        self.assertIsNone(parsed)
    
    def test_parse_empty_timestamp(self):
        """Test parsing empty timestamp"""
        parsed = TimestampParser.parse_iso8601("")
        
        self.assertIsNone(parsed)
    
    def test_to_iso8601(self):
        """Test converting datetime to ISO 8601"""
        dt = datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)
        iso_str = TimestampParser.to_iso8601(dt)
        
        self.assertIn("2025-12-01", iso_str)
        self.assertIn("10:00:00", iso_str)
    
    def test_normalize_to_utc(self):
        """Test normalizing datetime to UTC"""
        dt = datetime(2025, 12, 1, 10, 0, 0)  # No timezone
        normalized = TimestampParser.normalize_to_utc(dt)
        
        self.assertEqual(normalized.tzinfo, timezone.utc)


if __name__ == '__main__':
    unittest.main()
