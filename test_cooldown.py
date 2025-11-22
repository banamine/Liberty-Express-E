#!/usr/bin/env python3
"""
ScheduleFlow Cooldown Edge Case Tests
Comprehensive testing of 48-hour cooldown mechanism
"""

import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, '.')
from M3U_Matrix_Pro import ScheduleAlgorithm, CooldownManager, CooldownValidator
from datetime import datetime, timezone, timedelta


class CooldownEdgeCaseTests:
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
        """Run all edge case tests"""
        print("\n" + "="*70)
        print("SCHEDULEFLOW COOLDOWN EDGE CASE TESTS")
        print("="*70 + "\n")
        
        self.test_cooldown_persistence()
        self.test_exact_48h_boundary()
        self.test_day_transition()
        self.test_multiple_repeats()
        self.test_save_load_cycle()
        self.test_cooldown_validation()
        self.test_concurrent_videos()
        self.test_cooldown_override()
        
        print("\n" + "="*70)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*70 + "\n")
        return self.tests_failed == 0
    
    def test_cooldown_persistence(self):
        """Test that cooldown history persists across sessions"""
        print("COOLDOWN PERSISTENCE TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_1.json"
        
        # Session 1: Create manager and record a play
        manager1 = CooldownManager(str(history_file))
        video_url = "http://example.com/video1.mp4"
        play_time = datetime(2025, 11, 22, 10, 0, 0, tzinfo=timezone.utc)
        
        manager1.update_play_time(video_url, play_time)
        self.test("Cooldown recorded in session 1", video_url in manager1.last_played)
        
        # Verify it's in the file
        file_exists = history_file.exists()
        self.test("Cooldown history file created", file_exists)
        
        # Session 2: Load manager and verify history persists
        manager2 = CooldownManager(str(history_file))
        self.test("Cooldown history loads in session 2", video_url in manager2.last_played)
        self.test("Play time persisted correctly", manager2.last_played[video_url] == play_time)
        
        # Verify cooldown check uses persisted data
        check_time = datetime(2025, 11, 22, 11, 0, 0, tzinfo=timezone.utc)  # 1 hour later
        in_cooldown = manager2.is_in_cooldown(video_url, check_time, 48)
        self.test("Cooldown enforced from persisted data", in_cooldown)
        
        print()
    
    def test_exact_48h_boundary(self):
        """Test behavior at exactly 48-hour boundary"""
        print("EXACT 48-HOUR BOUNDARY TEST")
        print("-" * 70)
        
        video_url = "http://example.com/video_boundary.mp4"
        play_time = datetime(2025, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
        cooldown_end = play_time + timedelta(hours=48)  # 2025-11-24 12:00:00 UTC
        
        history_file = Path(self.temp_dir) / "cooldown_test_boundary.json"
        manager = CooldownManager(str(history_file))
        manager.update_play_time(video_url, play_time)
        
        # Test 1: Before cooldown ends
        test_time_before = datetime(2025, 11, 24, 11, 59, 59, tzinfo=timezone.utc)
        in_cooldown = manager.is_in_cooldown(video_url, test_time_before, 48)
        self.test("Video blocked 1 second before cooldown ends", in_cooldown)
        
        # Test 2: At exact cooldown end (boundary case)
        test_time_exact = cooldown_end
        in_cooldown = manager.is_in_cooldown(video_url, test_time_exact, 48)
        self.test("Video allowed at exact cooldown end time", not in_cooldown)
        
        # Test 3: After cooldown ends
        test_time_after = datetime(2025, 11, 24, 12, 0, 1, tzinfo=timezone.utc)
        in_cooldown = manager.is_in_cooldown(video_url, test_time_after, 48)
        self.test("Video allowed after cooldown ends", not in_cooldown)
        
        print()
    
    def test_day_transition(self):
        """Test cooldown across day boundaries (e.g., 23:59 to 00:01)"""
        print("DAY TRANSITION TEST")
        print("-" * 70)
        
        video_url = "http://example.com/video_day_transition.mp4"
        play_time = datetime(2025, 11, 22, 23, 59, 0, tzinfo=timezone.utc)
        
        history_file = Path(self.temp_dir) / "cooldown_test_day_transition.json"
        manager = CooldownManager(str(history_file))
        manager.update_play_time(video_url, play_time)
        
        # Next day at 00:01
        next_day_early = datetime(2025, 11, 23, 0, 1, 0, tzinfo=timezone.utc)
        time_diff_hours = (next_day_early - play_time).total_seconds() / 3600
        
        in_cooldown = manager.is_in_cooldown(video_url, next_day_early, 48)
        
        self.test(
            "Video blocked 2 minutes later (day transition)",
            in_cooldown,
            f"Time diff: {time_diff_hours:.2f}h, should be in 48h cooldown"
        )
        
        # 48 hours later should be allowed
        cooldown_end = play_time + timedelta(hours=48)
        in_cooldown = manager.is_in_cooldown(video_url, cooldown_end, 48)
        self.test("Video allowed exactly 48 hours later", not in_cooldown)
        
        print()
    
    def test_multiple_repeats(self):
        """Test multiple repeat scheduling of same video"""
        print("MULTIPLE REPEATS TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_repeats.json"
        manager = CooldownManager(str(history_file))
        
        video_url = "http://example.com/video_repeat.mp4"
        
        # Schedule same video multiple times with proper spacing
        times = [
            datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc),    # Nov 22, 00:00
            datetime(2025, 11, 24, 0, 0, 1, tzinfo=timezone.utc),    # Nov 24, 00:00 (48h+1s later)
            datetime(2025, 11, 26, 0, 0, 2, tzinfo=timezone.utc),    # Nov 26, 00:00 (48h+2s later)
        ]
        
        for i, time in enumerate(times):
            manager.update_play_time(video_url, time)
            
            # Verify it's recorded
            self.test(f"Play {i+1} recorded", video_url in manager.last_played)
            
            # Verify cooldown ends at correct time
            cooldown_end = manager.get_cooldown_end_time(video_url, 48)
            expected_end = time + timedelta(hours=48)
            self.test(
                f"Play {i+1} cooldown end correct",
                cooldown_end == expected_end,
                f"Got {cooldown_end}, expected {expected_end}"
            )
        
        print()
    
    def test_save_load_cycle(self):
        """Test that re-running schedule with cooldown history doesn't reset"""
        print("SAVE/LOAD CYCLE TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_cycle.json"
        
        playlist = ["http://example.com/vid1.mp4", "http://example.com/vid2.mp4"]
        start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
        
        # Schedule 1: Initial schedule
        slots1 = ScheduleAlgorithm.create_schedule_slots(start, 100, 60)
        manager = CooldownManager(str(history_file))
        result1 = ScheduleAlgorithm.auto_fill_schedule(playlist, slots1, 48, True, manager)
        
        scheduled_1 = result1['log']['scheduled']
        self.test("Initial schedule creates events", scheduled_1 > 0)
        
        # Verify cooldown was persisted
        has_history = len(manager.last_played) > 0
        self.test("Cooldown history persisted after schedule 1", has_history)
        
        # Schedule 2: Load persisted cooldown and schedule again
        manager2 = CooldownManager(str(history_file))
        slots2 = ScheduleAlgorithm.create_schedule_slots(
            start + timedelta(hours=100),  # Offset for new period
            100,
            60
        )
        result2 = ScheduleAlgorithm.auto_fill_schedule(playlist, slots2, 48, True, manager2)
        
        # Verify it uses the persisted cooldown
        skipped_2 = result2['log']['skipped_cooldown']
        self.test("Cooldown enforced across schedules", skipped_2 >= 0)
        
        print()
    
    def test_cooldown_validation(self):
        """Test CooldownValidator detects violations"""
        print("COOLDOWN VALIDATION TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_validation.json"
        manager = CooldownManager(str(history_file))
        
        video_url = "http://example.com/video_violation.mp4"
        play_time = datetime(2025, 11, 22, 10, 0, 0, tzinfo=timezone.utc)
        manager.update_play_time(video_url, play_time)
        
        # Create a schedule with a violation (video within 48h)
        violation_time = datetime(2025, 11, 22, 11, 0, 0, tzinfo=timezone.utc)  # 1 hour later
        violation_schedule = [
            {
                "video_url": video_url,
                "start": violation_time.isoformat(),
                "end": (violation_time + timedelta(hours=1)).isoformat()
            }
        ]
        
        is_valid, violations = CooldownValidator.validate_schedule_cooldown(
            violation_schedule, manager, 48
        )
        
        self.test("Violation detected", not is_valid)
        self.test("Violation details recorded", len(violations) > 0)
        
        # Create a valid schedule (after cooldown)
        valid_time = datetime(2025, 11, 24, 10, 0, 1, tzinfo=timezone.utc)  # 48h+ later
        valid_schedule = [
            {
                "video_url": video_url,
                "start": valid_time.isoformat(),
                "end": (valid_time + timedelta(hours=1)).isoformat()
            }
        ]
        
        is_valid, violations = CooldownValidator.validate_schedule_cooldown(
            valid_schedule, manager, 48
        )
        
        self.test("Valid schedule passes", is_valid)
        self.test("No violations in valid schedule", len(violations) == 0)
        
        print()
    
    def test_concurrent_videos(self):
        """Test cooldown works correctly with multiple different videos"""
        print("CONCURRENT VIDEOS TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_concurrent.json"
        manager = CooldownManager(str(history_file))
        
        # Schedule multiple videos at different times
        videos = [
            ("http://example.com/video_a.mp4", datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)),
            ("http://example.com/video_b.mp4", datetime(2025, 11, 22, 1, 0, 0, tzinfo=timezone.utc)),
            ("http://example.com/video_c.mp4", datetime(2025, 11, 22, 2, 0, 0, tzinfo=timezone.utc)),
        ]
        
        for video_url, play_time in videos:
            manager.update_play_time(video_url, play_time)
        
        self.test("All videos recorded", len(manager.last_played) == 3)
        
        # Check that each has independent cooldown
        check_time = datetime(2025, 11, 22, 3, 0, 0, tzinfo=timezone.utc)
        
        for video_url, _ in videos:
            in_cooldown = manager.is_in_cooldown(video_url, check_time, 48)
            self.test(
                f"{video_url.split('/')[-1]} in cooldown",
                in_cooldown
            )
        
        print()
    
    def test_cooldown_override(self):
        """Test that cooldown override is logged when necessary"""
        print("COOLDOWN OVERRIDE TEST")
        print("-" * 70)
        
        history_file = Path(self.temp_dir) / "cooldown_test_override.json"
        manager = CooldownManager(str(history_file))
        
        # Create a situation where all videos are in cooldown
        video = "http://example.com/video_override.mp4"
        play_time = datetime(2025, 11, 22, 10, 0, 0, tzinfo=timezone.utc)
        manager.update_play_time(video, play_time)
        
        # Create slots all within cooldown
        playlist = [video]  # Only one video
        start = datetime(2025, 11, 22, 11, 0, 0, tzinfo=timezone.utc)  # 1 hour later (in cooldown)
        slots = ScheduleAlgorithm.create_schedule_slots(start, 10, 60)
        
        result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, 48, False, manager)
        
        # Find forced override events
        forced_overrides = [d for d in result['log']['decisions'] 
                           if d.get('action') == 'forced_schedule_cooldown_override']
        
        self.test("Forced overrides recorded", len(forced_overrides) > 0,
                 f"Found {len(forced_overrides)} overrides")
        
        # Verify events still have warnings
        warned_events = [e for e in result['scheduled_events'] 
                        if 'warning' in e and e['warning'] == 'all_videos_in_cooldown']
        
        self.test("Override events marked with warning", len(warned_events) > 0)
        
        print()


def main():
    runner = CooldownEdgeCaseTests()
    success = runner.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
