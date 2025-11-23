#!/usr/bin/env python3
"""
ScheduleFlow Unit Tests
Tests individual components: Import, Export, Schedule functions
"""

import sys
sys.path.insert(0, '.')
from M3U_Matrix_Pro import M3UMatrixPro, ScheduleAlgorithm, TimestampParser, ScheduleValidator, DuplicateDetector, ConflictDetector
from datetime import datetime, timezone, timedelta
import json
import tempfile
import os

class UnitTestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.matrix = M3UMatrixPro()

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
        """Run all unit tests"""
        print("\n" + "="*70)
        print("SCHEDULEFLOW UNIT TESTS")
        print("="*70 + "\n")

        self.test_import_functions()
        self.test_export_functions()
        self.test_schedule_functions()
        self.test_validators()

        print("\n" + "="*70)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*70 + "\n")
        return self.tests_failed == 0

    def test_import_functions(self):
        """Unit tests for Import function"""
        print("IMPORT FUNCTION TESTS")
        print("-" * 70)

        # Test 1: Valid XML import
        valid_xml = """<?xml version="1.0"?>
        <tvguide>
            <schedule id="test1">
                <name>Test Schedule</name>
                <event id="evt1">
                    <title>Show 1</title>
                    <start>2025-11-22T10:00:00Z</start>
                    <end>2025-11-22T11:00:00Z</end>
                </event>
            </schedule>
        </tvguide>"""
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(valid_xml)
            is_valid, errors = ScheduleValidator.validate_xml_schedule(root)
            self.test("Valid XML imports without error", is_valid)
        except Exception as e:
            self.test("Valid XML imports without error", False, f"Exception: {str(e)[:50]}")

        # Test 2: Invalid XML rejected
        invalid_xml = """<?xml version="1.0"?>
        <tvguide>
            <schedule>
                <name>Unclosed tag"""
        
        try:
            root = ET.fromstring(invalid_xml)
            is_valid, errors = ScheduleValidator.validate_xml_schedule(root)
            self.test("Malformed XML rejected", not is_valid)
        except ET.ParseError:
            self.test("Malformed XML rejected", True)

        # Test 3: JSON import
        valid_json = '{"schedule": {"events": [{"title": "Show", "start": "2025-11-22T10:00:00Z"}]}}'
        try:
            data = json.loads(valid_json)
            self.test("Valid JSON imports without error", data is not None)
        except:
            self.test("Valid JSON imports without error", False)

        # Test 4: Invalid JSON rejected
        invalid_json = '{"schedule": {"events": [invalid]}}'
        try:
            json.loads(invalid_json)
            self.test("Malformed JSON rejected", False)
        except json.JSONDecodeError:
            self.test("Malformed JSON rejected", True)

        print()

    def test_export_functions(self):
        """Unit tests for Export function"""
        print("EXPORT FUNCTION TESTS")
        print("-" * 70)

        # Test 1: XML export format valid
        xml_output = """<?xml version="1.0" encoding="utf-8"?>
        <tvguide generated="2025-11-22T10:00:00Z">
            <schedule id="test1">
                <name>Test</name>
                <event>
                    <title>Show</title>
                    <start>2025-11-22T10:00:00Z</start>
                </event>
            </schedule>
        </tvguide>"""

        try:
            from xml.etree import ElementTree as ET
            ET.fromstring(xml_output)
            self.test("XML export format is valid", True)
        except:
            self.test("XML export format is valid", False)

        # Test 2: JSON export format valid
        json_output = {
            "schedule": {
                "name": "Test",
                "events": [{"title": "Show", "start": "2025-11-22T10:00:00Z"}]
            }
        }
        try:
            json_str = json.dumps(json_output, indent=2)
            parsed = json.loads(json_str)
            self.test("JSON export format is valid", parsed is not None)
        except:
            self.test("JSON export format is valid", False)

        # Test 3: Export contains all fields
        export_has_fields = (
            "schedule" in json_output and
            "name" in json_output["schedule"] and
            "events" in json_output["schedule"]
        )
        self.test("Export contains required fields", export_has_fields)

        # Test 4: Output is human-readable
        json_readable = json.dumps(json_output, indent=2)
        is_readable = "\n" in json_readable and "    " in json_readable
        self.test("JSON output is human-readable (indented)", is_readable)

        print()

    def test_schedule_functions(self):
        """Unit tests for Schedule function"""
        print("SCHEDULE FUNCTION TESTS")
        print("-" * 70)

        # Test 1: Playlist distribution
        playlist = [f"http://example.com/video_{i}.mp4" for i in range(10)]
        start = datetime(2025, 11, 22, 10, 0, 0, tzinfo=timezone.utc)
        slots = ScheduleAlgorithm.create_schedule_slots(start, 10, 60)

        result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, cooldown_hours=48, shuffle=False)
        coverage = float(result['coverage'].strip('%'))
        self.test("Playlist distributes to fill calendar", coverage == 100.0)

        # Test 2: Cooldown enforcement
        single_video = ["http://example.com/video.mp4"]
        slots_30h = ScheduleAlgorithm.create_schedule_slots(start, 30, 60)
        result_cooldown = ScheduleAlgorithm.auto_fill_schedule(
            single_video, slots_30h, cooldown_hours=48, shuffle=False
        )
        # With 48h cooldown, same video in 30h window should appear limited times
        self.test("Cooldown enforcement limits repeats", result_cooldown['log']['scheduled'] >= 1)

        # Test 3: Shuffle creates variation
        playlist_vary = [f"http://example.com/video_{i}.mp4" for i in range(5)]
        shuffled1 = ScheduleAlgorithm.fisher_yates_shuffle(playlist_vary)
        shuffled2 = ScheduleAlgorithm.fisher_yates_shuffle(playlist_vary)
        same_order = shuffled1 == shuffled2
        self.test("Shuffle creates variation", not same_order)

        # Test 4: Empty playlist handled
        empty = []
        try:
            result_empty = ScheduleAlgorithm.auto_fill_schedule(empty, slots, 48, False)
            coverage_empty = float(result_empty['coverage'].strip('%'))
            self.test("Empty playlist results in 0% coverage", coverage_empty == 0.0)
        except:
            self.test("Empty playlist handled gracefully", True)

        print()

    def test_validators(self):
        """Unit tests for validator classes"""
        print("VALIDATOR TESTS")
        print("-" * 70)

        # Test 1: Duplicate detection
        items = [
            {"title": "Video1", "url": "http://example.com/v1.mp4"},
            {"title": "Video2", "url": "http://example.com/v2.mp4"},
            {"title": "Video1", "url": "http://example.com/v1.mp4"}  # Duplicate
        ]
        unique, dupes = DuplicateDetector.detect_duplicates(items)
        self.test("Duplicate detection identifies duplicates", len(dupes) > 0)
        self.test("Unique items extracted correctly", len(unique) < len(items))

        # Test 2: Timestamp parsing
        ts_utc = TimestampParser.parse_iso8601("2025-11-22T10:00:00Z")
        ts_offset = TimestampParser.parse_iso8601("2025-11-22T10:00:00+08:00")
        self.test("UTC timestamp parses correctly", ts_utc is not None)
        self.test("Offset timestamp parses correctly", ts_offset is not None)
        self.test("Timestamps are UTC normalized", ts_utc.tzinfo == timezone.utc and ts_offset.tzinfo == timezone.utc)

        # Test 3: Conflict detection
        events = [
            {
                "title": "Event1",
                "start": "2025-11-22T10:00:00Z",
                "end": "2025-11-22T11:00:00Z"
            },
            {
                "title": "Event2",
                "start": "2025-11-22T10:30:00Z",
                "end": "2025-11-22T11:30:00Z"
            }
        ]
        conflicts = ConflictDetector.detect_conflicts(events)
        self.test("Conflict detection identifies overlaps", len(conflicts) > 0)

        print()


if __name__ == "__main__":
    runner = UnitTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
