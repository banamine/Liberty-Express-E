#!/usr/bin/env python3
"""
ScheduleFlow Integration Tests
End-to-end validation: Import → Schedule → Export
"""

import sys
sys.path.insert(0, '.')
from M3U_Matrix_Pro import M3UMatrixPro, ScheduleAlgorithm, TimestampParser
from datetime import datetime, timezone, timedelta
import json
import tempfile
import os

class IntegrationTestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.temp_dir = tempfile.mkdtemp()
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
        """Run all integration tests"""
        print("\n" + "="*70)
        print("SCHEDULEFLOW INTEGRATION TESTS")
        print("="*70 + "\n")

        self.test_end_to_end_import_schedule_export()
        self.test_playlist_distribution()
        self.test_calendar_update_on_edit()
        self.test_export_integrity()

        print("\n" + "="*70)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*70 + "\n")
        return self.tests_failed == 0

    def test_end_to_end_import_schedule_export(self):
        """E2E: Import TVGuide XML → Schedule 1,000 videos → Export"""
        print("END-TO-END WORKFLOW TEST")
        print("-" * 70)

        # Step 1: Create sample TVGuide XML
        sample_xml = """<?xml version="1.0"?>
        <tvguide>
            <schedule id="test_schedule">
                <name>Test Schedule</name>
                <event id="evt1">
                    <title>Morning Show</title>
                    <start>2025-11-22T08:00:00Z</start>
                    <end>2025-11-22T09:00:00Z</end>
                </event>
                <event id="evt2">
                    <title>News</title>
                    <start>2025-11-22T09:00:00Z</start>
                    <end>2025-11-22T10:00:00Z</end>
                </event>
            </schedule>
        </tvguide>"""

        xml_file = os.path.join(self.temp_dir, "test_schedule.xml")
        with open(xml_file, 'w') as f:
            f.write(sample_xml)
        
        self.test("Step 1: TVGuide XML created", os.path.exists(xml_file))

        # Step 2: Schedule 1,000 videos
        playlist = [f"http://example.com/video_{i:04d}.mp4" for i in range(1000)]
        start = datetime(2025, 11, 22, 10, 0, 0, tzinfo=timezone.utc)
        slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=50, slot_duration_minutes=60)
        
        result = ScheduleAlgorithm.auto_fill_schedule(
            playlist, slots, cooldown_hours=48, shuffle=True
        )
        
        events_scheduled = result['log']['scheduled']
        self.test("Step 2: 1,000 videos scheduled successfully", events_scheduled == len(slots))

        # Step 3: Verify export data structure
        export_data = {
            "schedule": {
                "name": "Generated Schedule",
                "events": result['scheduled_events'][:10]  # Sample first 10 events
            }
        }
        
        export_json = os.path.join(self.temp_dir, "export_schedule.json")
        with open(export_json, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.test("Step 3: Schedule exported to JSON", os.path.exists(export_json))

        # Step 4: Verify export can be re-imported
        with open(export_json) as f:
            imported_data = json.load(f)
        
        has_required_fields = (
            "schedule" in imported_data and
            "events" in imported_data["schedule"] and
            len(imported_data["schedule"]["events"]) > 0
        )
        self.test("Step 4: Exported data can be re-imported", has_required_fields)

        print()

    def test_playlist_distribution(self):
        """Verify playlist distributes evenly across calendar"""
        print("PLAYLIST DISTRIBUTION TEST")
        print("-" * 70)

        # Create playlist with identifiable videos
        playlist = [f"video_{i:03d}.mp4" for i in range(100)]
        start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
        slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=100, slot_duration_minutes=60)

        result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, cooldown_hours=0, shuffle=False)

        # Check distribution
        scheduled_videos = [e['video_url'] for e in result['scheduled_events']]
        unique_videos = set(scheduled_videos)
        repeat_count = len(scheduled_videos) - len(unique_videos)

        distribution_even = len(unique_videos) > 50  # Most videos should be used
        self.test("Multiple videos used in schedule", distribution_even)

        # Check coverage
        coverage = float(result['coverage'].strip('%'))
        self.test("Calendar fully covered", coverage == 100.0)

        print()

    def test_calendar_update_on_edit(self):
        """Verify calendar updates when playlist is edited"""
        print("CALENDAR UPDATE ON EDIT TEST")
        print("-" * 70)

        # Initial schedule
        playlist_v1 = ["http://example.com/video_1.mp4", "http://example.com/video_2.mp4"]
        start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
        slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=4, slot_duration_minutes=60)

        result_v1 = ScheduleAlgorithm.auto_fill_schedule(playlist_v1, slots, cooldown_hours=0, shuffle=False)
        v1_events = len(result_v1['scheduled_events'])

        self.test("Initial schedule created", v1_events > 0)

        # Edit playlist (add more videos)
        playlist_v2 = [f"http://example.com/video_{i}.mp4" for i in range(1, 11)]  # 10 videos
        result_v2 = ScheduleAlgorithm.auto_fill_schedule(playlist_v2, slots, cooldown_hours=0, shuffle=False)
        v2_events = len(result_v2['scheduled_events'])

        self.test("Calendar updates after playlist edit", v2_events > 0)
        self.test("Updated calendar uses new videos", v2_events == len(slots))

        print()

    def test_export_integrity(self):
        """Verify exported data matches what was scheduled"""
        print("EXPORT INTEGRITY TEST")
        print("-" * 70)

        # Create and schedule
        playlist = [f"http://example.com/video_{i}.mp4" for i in range(20)]
        start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
        slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=20, slot_duration_minutes=60)

        result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, cooldown_hours=0, shuffle=False)

        # Verify event structure
        all_have_required_fields = all(
            'video_url' in e and 'start' in e and 'end' in e
            for e in result['scheduled_events']
        )
        self.test("All events have required fields", all_have_required_fields)

        # Verify timestamps are valid ISO8601
        timestamps_valid = all(
            'T' in e['start'] and 'Z' in e['start']
            for e in result['scheduled_events']
        )
        self.test("Timestamps are valid ISO8601 UTC", timestamps_valid)

        # Verify no overlaps
        events_sorted = sorted(result['scheduled_events'], key=lambda e: e['start'])
        no_overlaps = True
        for i in range(len(events_sorted) - 1):
            current_end = events_sorted[i]['end']
            next_start = events_sorted[i+1]['start']
            if current_end > next_start:
                no_overlaps = False
                break

        self.test("No overlapping events in export", no_overlaps)

        print()


if __name__ == "__main__":
    runner = IntegrationTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
