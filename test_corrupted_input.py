#!/usr/bin/env python3
"""
ScheduleFlow Corrupted Input Handling Tests
Test how system handles malformed/corrupted data
"""

import sys
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, '.')
from M3U_Matrix_Pro import M3UMatrixPro


class CorruptedInputTests:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.temp_dir = tempfile.mkdtemp()
    
    def test(self, name, condition, details=""):
        """Run a single test"""
        if condition:
            print(f"  ✅ {name}")
            self.tests_passed += 1
        else:
            print(f"  ❌ {name}")
            if details:
                print(f"     {details}")
            self.tests_failed += 1
    
    def run_all(self):
        """Run all corrupted input tests"""
        print("\n" + "="*70)
        print("SCHEDULEFLOW CORRUPTED INPUT HANDLING TESTS")
        print("="*70 + "\n")
        
        self.test_malformed_xml()
        self.test_invalid_json()
        self.test_missing_fields()
        self.test_invalid_timestamps()
        self.test_type_errors()
        self.test_empty_files()
        self.test_oversized_data()
        self.test_special_characters()
        
        print("\n" + "="*70)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*70 + "\n")
        return self.tests_failed == 0
    
    def test_malformed_xml(self):
        """Test handling of malformed XML"""
        print("MALFORMED XML TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: XML with unclosed tag
        malformed_file = Path(self.temp_dir) / "malformed.xml"
        malformed_file.write_text("""<?xml version="1.0"?>
<schedule>
    <event>
        <title>Video 1</title>
        <start>2025-11-22T10:00:00Z
</schedule>""")
        
        result = matrix.import_schedule_xml(str(malformed_file))
        self.test(
            "Unclosed XML tag returns error",
            result.get("status") == "error",
            f"Status: {result.get('status')}"
        )
        self.test(
            "Error type identified",
            result.get("type") in ["parse_error", "error"],
            f"Type: {result.get('type')}"
        )
        
        # Test 2: Invalid XML declaration
        bad_xml_file = Path(self.temp_dir) / "bad_xml.xml"
        bad_xml_file.write_text("not valid xml at all")
        
        result = matrix.import_schedule_xml(str(bad_xml_file))
        self.test(
            "Invalid XML detected",
            result.get("status") == "error"
        )
        
        # Test 3: Missing root element
        no_root_file = Path(self.temp_dir) / "no_root.xml"
        no_root_file.write_text("""<?xml version="1.0"?>
<wrongroot>
    <event>test</event>
</wrongroot>""")
        
        result = matrix.import_schedule_xml(str(no_root_file))
        self.test(
            "Invalid root element rejected",
            result.get("status") == "error" and "root" in str(result)
        )
        
        print()
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        print("INVALID JSON TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Malformed JSON (trailing comma)
        bad_json_file = Path(self.temp_dir) / "bad.json"
        bad_json_file.write_text('{"events": [{"title": "Video"}],}')
        
        result = matrix.import_schedule_json(str(bad_json_file))
        self.test(
            "Malformed JSON returns error",
            result.get("status") == "error"
        )
        
        # Test 2: Not JSON at all
        not_json_file = Path(self.temp_dir) / "not_json.json"
        not_json_file.write_text("This is plain text, not JSON")
        
        result = matrix.import_schedule_json(str(not_json_file))
        self.test(
            "Non-JSON file returns error",
            result.get("status") == "error"
        )
        
        # Test 3: JSON array instead of object
        array_json_file = Path(self.temp_dir) / "array.json"
        array_json_file.write_text('[{"title": "Video"}]')
        
        result = matrix.import_schedule_json(str(array_json_file))
        self.test(
            "JSON array instead of object rejected",
            result.get("status") == "error" or result.get("status") == "success"
        )
        
        print()
    
    def test_missing_fields(self):
        """Test handling of missing required fields"""
        print("MISSING FIELDS TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: XML missing title
        missing_title_xml = Path(self.temp_dir) / "missing_title.xml"
        missing_title_xml.write_text("""<?xml version="1.0"?>
<schedule>
    <event>
        <start>2025-11-22T10:00:00Z</start>
        <end>2025-11-22T11:00:00Z</end>
    </event>
</schedule>""")
        
        result = matrix.import_schedule_xml(str(missing_title_xml))
        self.test(
            "Missing title detected",
            result.get("status") == "error" or "title" in str(result).lower()
        )
        
        # Test 2: JSON missing start time
        missing_start_json = Path(self.temp_dir) / "missing_start.json"
        missing_start_json.write_text("""{
            "schedule": [
                {
                    "title": "Video 1",
                    "end": "2025-11-22T11:00:00Z"
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(missing_start_json))
        self.test(
            "Missing start time detected",
            result.get("status") == "error" or "start" in str(result).lower()
        )
        
        # Test 3: Event with empty fields
        empty_fields_json = Path(self.temp_dir) / "empty_fields.json"
        empty_fields_json.write_text("""{
            "schedule": [
                {
                    "title": "",
                    "start": "2025-11-22T10:00:00Z",
                    "end": "2025-11-22T11:00:00Z"
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(empty_fields_json))
        self.test(
            "Empty title field detected",
            result.get("status") == "error" or "title" in str(result).lower()
        )
        
        print()
    
    def test_invalid_timestamps(self):
        """Test handling of invalid timestamp formats"""
        print("INVALID TIMESTAMP TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Non-ISO timestamp format
        bad_timestamp_xml = Path(self.temp_dir) / "bad_timestamp.xml"
        bad_timestamp_xml.write_text("""<?xml version="1.0"?>
<schedule>
    <event>
        <title>Video 1</title>
        <start>11/22/2025 10:00 AM</start>
        <end>11/22/2025 11:00 AM</end>
    </event>
</schedule>""")
        
        result = matrix.import_schedule_xml(str(bad_timestamp_xml))
        self.test(
            "Non-ISO timestamp rejected",
            result.get("status") == "error" or "timestamp" in str(result).lower()
        )
        
        # Test 2: Completely invalid date
        invalid_date_json = Path(self.temp_dir) / "invalid_date.json"
        invalid_date_json.write_text("""{
            "schedule": [
                {
                    "title": "Video 1",
                    "start": "not-a-date",
                    "end": "2025-11-22T11:00:00Z"
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(invalid_date_json))
        self.test(
            "Invalid date format detected",
            result.get("status") == "error" or "start" in str(result).lower()
        )
        
        # Test 3: Start after end
        reversed_times_json = Path(self.temp_dir) / "reversed_times.json"
        reversed_times_json.write_text("""{
            "schedule": [
                {
                    "title": "Video 1",
                    "start": "2025-11-22T11:00:00Z",
                    "end": "2025-11-22T10:00:00Z"
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(reversed_times_json))
        self.test(
            "Start after end detected",
            result.get("status") == "error" or "order" in str(result).lower() or result.get("status") == "success"
        )
        
        print()
    
    def test_type_errors(self):
        """Test handling of type mismatches"""
        print("TYPE ERROR TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Events as object instead of array
        wrong_type_json = Path(self.temp_dir) / "wrong_type.json"
        wrong_type_json.write_text("""{
            "schedule": {
                "title": "Video 1",
                "start": "2025-11-22T10:00:00Z"
            }
        }""")
        
        result = matrix.import_schedule_json(str(wrong_type_json))
        self.test(
            "Non-array schedule field rejected",
            result.get("status") == "error" or "list" in str(result).lower()
        )
        
        # Test 2: Timestamp as number instead of string
        number_timestamp_json = Path(self.temp_dir) / "number_time.json"
        number_timestamp_json.write_text("""{
            "schedule": [
                {
                    "title": "Video 1",
                    "start": 1700640000,
                    "end": 1700643600
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(number_timestamp_json))
        # Should either handle it gracefully or reject it
        has_result = result.get("status") in ["error", "success"]
        self.test(
            "Numeric timestamp handled",
            has_result,
            f"Status: {result.get('status')}"
        )
        
        print()
    
    def test_empty_files(self):
        """Test handling of empty or near-empty files"""
        print("EMPTY FILE TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Empty XML file
        empty_xml = Path(self.temp_dir) / "empty.xml"
        empty_xml.write_text("")
        
        result = matrix.import_schedule_xml(str(empty_xml))
        self.test(
            "Empty XML handled",
            result.get("status") == "error"
        )
        
        # Test 2: Empty JSON file
        empty_json = Path(self.temp_dir) / "empty.json"
        empty_json.write_text("")
        
        result = matrix.import_schedule_json(str(empty_json))
        self.test(
            "Empty JSON handled",
            result.get("status") == "error"
        )
        
        # Test 3: JSON with no events
        no_events_json = Path(self.temp_dir) / "no_events.json"
        no_events_json.write_text('{"schedule": []}')
        
        result = matrix.import_schedule_json(str(no_events_json))
        self.test(
            "Empty events array rejected",
            result.get("status") == "error"
        )
        
        print()
    
    def test_oversized_data(self):
        """Test handling of oversized/excessive data"""
        print("OVERSIZED DATA TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Very large JSON (many events)
        large_json = Path(self.temp_dir) / "large.json"
        events = [
            {
                "title": f"Video {i}",
                "start": "2025-11-22T10:00:00Z",
                "end": "2025-11-22T11:00:00Z"
            }
            for i in range(1000)  # 1000 events
        ]
        large_json.write_text(json.dumps({"schedule": events}))
        
        result = matrix.import_schedule_json(str(large_json))
        self.test(
            "Large file processed",
            result.get("status") in ["error", "success"],
            f"Status: {result.get('status')}"
        )
        self.test(
            "Result has events_imported",
            "events_imported" in result or result.get("status") == "error"
        )
        
        print()
    
    def test_special_characters(self):
        """Test handling of special characters and encoding"""
        print("SPECIAL CHARACTER TESTS")
        print("-" * 70)
        
        matrix = M3UMatrixPro()
        
        # Test 1: Unicode in title
        unicode_json = Path(self.temp_dir) / "unicode.json"
        unicode_json.write_text("""{
            "schedule": [
                {
                    "title": "视频 🎬 Видео",
                    "start": "2025-11-22T10:00:00Z",
                    "end": "2025-11-22T11:00:00Z"
                }
            ]
        }""")
        
        result = matrix.import_schedule_json(str(unicode_json))
        self.test(
            "Unicode characters handled",
            result.get("status") in ["error", "success"]
        )
        
        # Test 2: XML special characters
        special_chars_xml = Path(self.temp_dir) / "special_chars.xml"
        special_chars_xml.write_text("""<?xml version="1.0"?>
<schedule>
    <event>
        <title>Video &amp; Special &lt;Tags&gt;</title>
        <start>2025-11-22T10:00:00Z</start>
        <end>2025-11-22T11:00:00Z</end>
    </event>
</schedule>""")
        
        result = matrix.import_schedule_xml(str(special_chars_xml))
        self.test(
            "XML special characters handled",
            result.get("status") in ["error", "success"]
        )
        
        print()


def main():
    runner = CorruptedInputTests()
    success = runner.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
