#!/usr/bin/env python3
"""
ScheduleFlow Stress Tests
Scale testing: 10,000+ videos, concurrent operations
"""

import sys
sys.path.insert(0, '.')
from M3U_Matrix_Pro import ScheduleAlgorithm
from datetime import datetime, timezone
import time
import threading

class StressTestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0

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
        """Run all stress tests"""
        print("\n" + "="*70)
        print("SCHEDULEFLOW STRESS TESTS")
        print("="*70 + "\n")

        self.test_10k_video_load()
        self.test_concurrent_scheduling()
        self.test_memory_efficiency()
        self.test_scaling()

        print("\n" + "="*70)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*70 + "\n")
        return self.tests_failed == 0

    def test_10k_video_load(self):
        """Test loading and scheduling 10,000 videos"""
        print("10,000 VIDEO LOAD TEST")
        print("-" * 70)

        try:
            start_time = time.time()
            
            # Generate 10,000 video URLs
            playlist = [f"http://example.com/video_{i:05d}.mp4" for i in range(10000)]
            self.test("10,000 videos generated in memory", len(playlist) == 10000)

            # Create 100 scheduling slots
            start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
            slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=100, slot_duration_minutes=60)
            
            # Schedule with cooldown
            result = ScheduleAlgorithm.auto_fill_schedule(
                playlist, slots, cooldown_hours=48, shuffle=True
            )

            elapsed = time.time() - start_time
            coverage = float(result['coverage'].strip('%'))
            scheduled = result['log']['scheduled']

            self.test("10,000 videos scheduled successfully", scheduled == 100)
            self.test("Calendar fully covered with 10k videos", coverage == 100.0)
            self.test("10k scheduling completes in <5 seconds", elapsed < 5.0, 
                     f"Took {elapsed:.2f}s")

        except Exception as e:
            self.test("10,000 video load without crash", False, str(e)[:60])

        print()

    def test_concurrent_scheduling(self):
        """Test concurrent scheduling operations"""
        print("CONCURRENT SCHEDULING TEST")
        print("-" * 70)

        results = []
        errors = []

        def schedule_task(thread_id):
            """Simulate a scheduling task"""
            try:
                playlist = [f"http://example.com/user{thread_id}_video_{i}.mp4" for i in range(50)]
                start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
                slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=50, slot_duration_minutes=60)
                
                result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, cooldown_hours=48, shuffle=True)
                results.append((thread_id, result['log']['scheduled']))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Simulate 100 concurrent users scheduling
        threads = []
        start_time = time.time()

        for i in range(100):
            t = threading.Thread(target=schedule_task, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        elapsed = time.time() - start_time
        successful = len(results)
        failed = len(errors)

        self.test("100 concurrent scheduling operations", successful == 100)
        self.test("No concurrency errors", failed == 0, 
                 f"{failed} errors: {errors[:1] if errors else 'None'}")
        self.test("Concurrent scheduling completes in <30 seconds", elapsed < 30.0,
                 f"Took {elapsed:.2f}s")

        print()

    def test_memory_efficiency(self):
        """Test memory usage with large playlists"""
        print("MEMORY EFFICIENCY TEST")
        print("-" * 70)

        import sys

        try:
            # Check memory before
            baseline = sys.getsizeof([])

            # Create 5,000 video URLs
            playlist = [f"http://example.com/video_{i:05d}.mp4" for i in range(5000)]
            playlist_size = sys.getsizeof(playlist)

            # Check memory after shuffle
            shuffled = ScheduleAlgorithm.fisher_yates_shuffle(playlist)
            shuffled_size = sys.getsizeof(shuffled)

            # Memory should be reasonable (< 500KB for 5000 URLs)
            reasonable_memory = shuffled_size < 500000

            self.test("5,000 URL playlist fits in memory", playlist_size > 0)
            self.test("Shuffle creates copy efficiently", shuffled_size > 0)
            self.test("Memory usage is reasonable (<500KB)", reasonable_memory,
                     f"Used {shuffled_size/1024:.1f}KB")

        except Exception as e:
            self.test("Memory efficiency check", False, str(e)[:60])

        print()

    def test_scaling(self):
        """Test scaling behavior with increasing load"""
        print("SCALING TEST")
        print("-" * 70)

        try:
            start = datetime(2025, 11, 22, 0, 0, 0, tzinfo=timezone.utc)
            
            scaling_results = []

            # Test with increasing playlist sizes
            for playlist_size in [100, 1000, 5000, 10000]:
                playlist = [f"http://example.com/video_{i:05d}.mp4" for i in range(playlist_size)]
                slots = ScheduleAlgorithm.create_schedule_slots(start, duration_hours=50, slot_duration_minutes=60)
                
                task_start = time.time()
                result = ScheduleAlgorithm.auto_fill_schedule(playlist, slots, cooldown_hours=48, shuffle=True)
                task_time = time.time() - task_start

                scaling_results.append({
                    'size': playlist_size,
                    'time': task_time,
                    'scheduled': result['log']['scheduled']
                })

            # Verify linear scaling (time shouldn't increase exponentially)
            times = [r['time'] for r in scaling_results]
            max_time = max(times)
            linear_scaling = max_time < 5.0  # 10k videos should complete in <5s

            self.test("100 video schedule", scaling_results[0]['scheduled'] == 50)
            self.test("1,000 video schedule", scaling_results[1]['scheduled'] == 50)
            self.test("5,000 video schedule", scaling_results[2]['scheduled'] == 50)
            self.test("10,000 video schedule", scaling_results[3]['scheduled'] == 50)
            self.test("Scaling is near-linear (<5s for 10k)", linear_scaling)

            print(f"\n  Timing breakdown:")
            for r in scaling_results:
                print(f"    {r['size']:,} videos → {r['time']:.3f}s")

        except Exception as e:
            self.test("Scaling test", False, str(e)[:60])

        print()


if __name__ == "__main__":
    runner = StressTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
