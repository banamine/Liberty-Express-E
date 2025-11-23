"""Integration tests - modules working together"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import ConfigManager
from core.file_manager import FileManager
from core.cooldown import CooldownManager
from core.validation import ScheduleValidator
from core.scheduling import ScheduleEngine


class TestIntegration(unittest.TestCase):
    """Test modules working together"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        self.config = ConfigManager(str(self.temp_path / "config.yaml"))
        self.file_manager = FileManager(backup_dir=str(self.temp_path / "backups"))
        self.cooldown = CooldownManager(str(self.temp_path / "cooldown.json"))
        self.engine = ScheduleEngine(self.cooldown)
    
    def tearDown(self):
        """Cleanup"""
        self.temp_dir.cleanup()
    
    def test_full_workflow_create_schedule(self):
        """Test complete workflow: config -> schedule -> validate -> backup"""
        # 1. Load config
        cooldown_hours = self.config.get("scheduling.cooldown_hours")
        self.assertEqual(cooldown_hours, 48)
        
        # 2. Create schedule
        videos = [
            {"url": "http://example.com/v1.mp4", "duration": 300, "category": "News"},
            {"url": "http://example.com/v2.mp4", "duration": 600, "category": "Sports"}
        ]
        
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=3600
        )
        
        # 3. Validate schedule
        valid, errors = ScheduleValidator.validate_schedule(schedule["events"])
        self.assertTrue(valid)
        
        # 4. Backup schedule
        schedule_file = self.temp_path / "schedule.json"
        import json
        schedule_file.write_text(json.dumps(schedule))
        
        backup = self.file_manager.create_backup(str(schedule_file))
        self.assertTrue(backup.exists())
    
    def test_cooldown_with_scheduling(self):
        """Test that cooldown is enforced during scheduling"""
        video_url = "http://example.com/video.mp4"
        play_time = datetime.now(tz=timezone.utc)
        
        # Record video as recently played
        self.cooldown.update_play_time(video_url, play_time)
        
        # Try to schedule it again
        videos = [
            {"url": video_url, "duration": 300, "category": "News"}
        ]
        
        check_time = play_time
        is_cooldown = self.cooldown.is_in_cooldown(video_url, check_time)
        self.assertTrue(is_cooldown)  # Should be in cooldown
    
    def test_config_driven_scheduling(self):
        """Test scheduling respects config settings"""
        # Get scheduling config
        timezone_str = self.config.get("scheduling.timezone")
        auto_fill = self.config.get("scheduling.auto_fill")
        
        # Create schedule with config values
        videos = [
            {"url": "http://example.com/v1.mp4", "duration": 300, "category": "News"}
        ]
        
        start_time = datetime.now(tz=timezone.utc)
        schedule = self.engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=3600,
            timezone_str=timezone_str,
            auto_fill=auto_fill
        )
        
        self.assertEqual(schedule["status"], "success")


class TestDataFlow(unittest.TestCase):
    """Test data flowing through system"""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_data_persistence_flow(self):
        """Test data persists through save/load cycle"""
        file_manager = FileManager(backup_dir=str(self.temp_path / "backups"))
        
        # Create test data
        test_data = {"events": [{"title": "Test", "duration": 300}]}
        import json
        data_file = self.temp_path / "data.json"
        data_file.write_text(json.dumps(test_data))
        
        # Backup
        backup_path = file_manager.create_backup(str(data_file))
        
        # Modify original
        data_file.write_text(json.dumps({"events": []}))
        
        # Restore
        restored_file = self.temp_path / "restored.json"
        file_manager.restore_backup(str(backup_path), str(restored_file))
        
        # Verify data
        restored_data = json.loads(restored_file.read_text())
        self.assertEqual(len(restored_data["events"]), 1)
        self.assertEqual(restored_data["events"][0]["title"], "Test")
    
    def test_multiple_modules_same_config(self):
        """Test multiple modules reading from same config"""
        config_path = self.temp_path / "config.yaml"
        
        config1 = ConfigManager(str(config_path))
        config2 = ConfigManager(str(config_path))
        
        # Both should have same defaults
        self.assertEqual(config1.get("app.name"), config2.get("app.name"))


if __name__ == '__main__':
    unittest.main()
