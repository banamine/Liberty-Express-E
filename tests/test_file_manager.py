"""Unit tests for file_manager module"""

import unittest
import tempfile
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """Test FileManager functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.manager = FileManager(str(self.temp_path))
    
    def tearDown(self):
        """Cleanup test fixtures"""
        self.temp_dir.cleanup()
    
    def test_backup_creation(self):
        """Test creating a backup"""
        # Create a test file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test content")
        
        # Create backup
        backup_path = self.manager.create_backup(str(test_file))
        
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
    
    def test_backup_gzip_compression(self):
        """Test gzip backup compression"""
        test_file = self.temp_path / "test.json"
        test_file.write_text('{"data": "test"}')
        
        backup_path = self.manager.create_backup(str(test_file))
        
        # Should have .gz extension
        self.assertTrue(str(backup_path).endswith('.gz'))
    
    def test_backup_restoration(self):
        """Test restoring from backup"""
        # Create and backup a file
        test_file = self.temp_path / "test.txt"
        original_content = "original content"
        test_file.write_text(original_content)
        
        backup_path = self.manager.create_backup(str(test_file))
        
        # Modify the original
        test_file.write_text("modified content")
        
        # Restore from backup
        restore_path = self.temp_path / "restored.txt"
        success = self.manager.restore_backup(str(backup_path), str(restore_path))
        
        self.assertTrue(success)
        self.assertEqual(restore_path.read_text(), original_content)
    
    def test_list_backups(self):
        """Test listing backups"""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        
        # Create multiple backups
        self.manager.create_backup(str(test_file))
        time.sleep(0.1)  # Small delay to ensure different timestamps
        self.manager.create_backup(str(test_file))
        
        backups = self.manager.list_backups("test.txt")
        self.assertGreaterEqual(len(backups), 2)
    
    def test_normalize_path(self):
        """Test path normalization"""
        # Test with home directory expansion
        path = FileManager.normalize_path("~/test")
        self.assertNotIn("~", str(path))
        self.assertTrue(path.is_absolute())


if __name__ == '__main__':
    unittest.main()
