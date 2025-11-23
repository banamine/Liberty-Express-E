"""Unit tests for config_manager module"""

import unittest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import ConfigManager, Config


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality"""
    
    def test_config_defaults(self):
        """Test that defaults are loaded when config file missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            manager = ConfigManager(str(config_path))
            
            # Check defaults exist
            self.assertEqual(manager.get("app.name"), "ScheduleFlow")
            self.assertEqual(manager.get("scheduling.cooldown_hours"), 48)
    
    def test_config_get_set(self):
        """Test getting and setting config values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.yaml"
            manager = ConfigManager(str(config_path))
            
            # Get existing value
            value = manager.get("app.name")
            self.assertIsNotNone(value)
            
            # Set new value
            manager.set("app.debug", True)
            self.assertEqual(manager.get("app.debug"), True)
    
    def test_config_nested_access(self):
        """Test nested key access with dot notation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.yaml"
            manager = ConfigManager(str(config_path))
            
            # Access deeply nested value
            storage_dir = manager.get("storage.schedules_dir")
            self.assertEqual(storage_dir, "schedules")
            
            # Access with default
            value = manager.get("nonexistent.key", "default_value")
            self.assertEqual(value, "default_value")
    
    def test_config_validation(self):
        """Test config validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.yaml"
            manager = ConfigManager(str(config_path))
            
            # Should be valid with defaults
            self.assertTrue(manager.validate())


class TestConfig(unittest.TestCase):
    """Test Config container"""
    
    def test_config_get_method(self):
        """Test Config.get() method"""
        config_data = {"app": {"name": "Test"}, "value": 42}
        config = Config(config_data)
        
        self.assertEqual(config.get("app.name"), "Test")
        self.assertEqual(config.get("value"), 42)
        self.assertIsNone(config.get("nonexistent"))
    
    def test_config_set_method(self):
        """Test Config.set() method"""
        config_data = {"app": {"name": "Test"}}
        config = Config(config_data)
        
        config.set("app.name", "NewName")
        self.assertEqual(config.get("app.name"), "NewName")
        
        config.set("new.nested.value", "created")
        self.assertEqual(config.get("new.nested.value"), "created")


if __name__ == '__main__':
    unittest.main()
