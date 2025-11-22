#!/usr/bin/env python3
"""
Test script for TV Schedule Center components
Verifies database, manager, and basic functionality
"""

import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

def test_database():
    """Test database operations"""
    print("Testing Database Module...")
    from Core_Modules.tv_schedule_db import TVScheduleDB
    
    db = TVScheduleDB("test_schedule.db")
    
    # Test channel operations
    channel_id = db.add_channel("Test Channel", "A test channel", "Entertainment")
    print(f"✓ Added channel with ID: {channel_id}")
    
    # Test show operations
    show_id = db.add_show(channel_id, "Test Show", 30, "A test show", "Comedy")
    print(f"✓ Added show with ID: {show_id}")
    
    # Test schedule operations
    schedule_id = db.create_schedule("Test Schedule", "2025-01-01", "2025-01-07")
    print(f"✓ Created schedule with ID: {schedule_id}")
    
    # Test time slot
    slot_id = db.add_time_slot(
        schedule_id, channel_id, show_id,
        "2025-01-01 20:00:00", "2025-01-01 20:30:00"
    )
    print(f"✓ Added time slot with ID: {slot_id}")
    
    # Get statistics
    stats = db.get_schedule_statistics(schedule_id)
    print(f"✓ Schedule has {stats.get('total_slots', 0)} slots")
    
    return True

def test_manager():
    """Test schedule manager"""
    print("\nTesting Schedule Manager...")
    from Core_Modules.schedule_manager import ScheduleManager
    
    manager = ScheduleManager("test_schedule.db")
    
    # Create time grid
    slots = manager.create_time_grid("2025-01-01", "2025-01-01", 30)
    print(f"✓ Created time grid with {len(slots)} slots")
    
    # Test conflict detection
    conflicts = manager.resolve_conflicts(1)  # Using schedule_id=1 from test above
    print(f"✓ Conflict check completed: {conflicts['conflicts_found']} found")
    
    return True

def test_gui_import():
    """Test that GUI can be imported"""
    print("\nTesting GUI Import...")
    try:
        from Applications.TV_SCHEDULE_CENTER import TVScheduleCenter
        print("✓ TV Schedule Center GUI module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import GUI: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("TV SCHEDULE CENTER - COMPONENT TESTS")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Database", test_database()))
    results.append(("Manager", test_manager()))
    results.append(("GUI Import", test_gui_import()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for component, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{component}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! TV Schedule Center is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)