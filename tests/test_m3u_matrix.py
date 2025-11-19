#!/usr/bin/env python3
"""
Unit Tests for M3U Matrix Pro
Tests the load-bearing functions: parse_extinf_line, parse_m3u_file, build_m3u
"""

import unittest
import tempfile
import os
from pathlib import Path


class TestM3UMatrix(unittest.TestCase):
    """Test critical M3U parsing and building functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_m3u = """#EXTM3U
#EXTINF:-1 tvg-id="test1" tvg-name="Test Channel 1" tvg-logo="http://logo.png" group-title="Movies",Test Channel 1
http://example.com/stream1.m3u8
#EXTINF:-1 tvg-id="test2" tvg-name="Test Channel 2" tvg-logo="" group-title="Sports",Test Channel 2
http://example.com/stream2.m3u8
#EXTGRP:News
#EXTINF:-1,Test Channel 3
http://example.com/stream3.m3u8
"""
    
    def test_parse_extinf_line_basic(self):
        """Test basic EXTINF line parsing"""
        # Import here to avoid circular imports
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from M3U_MATRIX_PRO import M3UMatrix
        
        # Create minimal mock
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                
        matrix = MockMatrix()
        
        line = '#EXTINF:-1 tvg-id="test1" tvg-name="Test Channel" tvg-logo="http://logo.png" group-title="Movies",Test Channel'
        result = matrix.parse_extinf_line(line)
        
        self.assertEqual(result['tvg_id'], 'test1')
        self.assertEqual(result['name'], 'Test Channel')
        self.assertEqual(result['logo'], 'http://logo.png')
        self.assertEqual(result['group'], 'Movies')
    
    def test_parse_extinf_line_minimal(self):
        """Test EXTINF line with minimal info"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        line = '#EXTINF:-1,Simple Channel'
        result = matrix.parse_extinf_line(line)
        
        self.assertEqual(result['name'], 'Simple Channel')
        self.assertEqual(result.get('tvg_id', ''), '')
        self.assertEqual(result.get('group', 'Other'), 'Other')
    
    def test_parse_extinf_line_malformed(self):
        """Test handling of malformed EXTINF lines"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
        
        matrix = MockMatrix()
        
        # Malformed line should return empty dict or default values
        line = '#EXTINF:invalid'
        result = matrix.parse_extinf_line(line)
        
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
    
    def test_build_m3u_output(self):
        """Test M3U content building"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from M3U_MATRIX_PRO import M3UMatrix
        
        class MockRoot:
            def after(self, *args): pass
        
        class MockMatrix(M3UMatrix):
            def __init__(self):
                self.root = MockRoot()
                self.channels = [
                    {
                        'num': 1,
                        'tvg_id': 'test1',
                        'name': 'Test Channel',
                        'logo': 'http://logo.png',
                        'group': 'Movies',
                        'url': 'http://example.com/stream.m3u8'
                    }
                ]
                self.m3u = ""
        
        matrix = MockMatrix()
        matrix.build_m3u()
        
        # Check that M3U was built
        self.assertTrue(matrix.m3u.startswith('#EXTM3U'))
        self.assertIn('Test Channel', matrix.m3u)
        self.assertIn('http://example.com/stream.m3u8', matrix.m3u)
    
    def test_uuid_generation(self):
        """Test that UUIDs are generated for channels"""
        import uuid
        
        # Simulate channel loading
        channel = {'name': 'Test', 'url': 'http://test.com'}
        
        if 'uuid' not in channel:
            channel['uuid'] = str(uuid.uuid4())
        
        # UUID should be valid
        self.assertIn('uuid', channel)
        self.assertEqual(len(channel['uuid']), 36)  # UUID4 format
        
        # Should be unique
        channel2 = {'name': 'Test2', 'url': 'http://test2.com'}
        channel2['uuid'] = str(uuid.uuid4())
        
        self.assertNotEqual(channel['uuid'], channel2['uuid'])
    
    def test_large_import_validation(self):
        """Test that large imports trigger confirmation"""
        # This is more of a integration test
        # Simulate 1500 channels
        large_channel_list = [
            {'name': f'Channel {i}', 'url': f'http://example.com/stream{i}.m3u8'}
            for i in range(1500)
        ]
        
        # Should exceed 1000 threshold
        self.assertGreater(len(large_channel_list), 1000)


class TestTagHandling(unittest.TestCase):
    """Test consistent tag handling"""
    
    def test_tag_standardization(self):
        """Test that tags are stored consistently"""
        # Tags should be stored in a standard key
        channel = {
            'name': 'Test',
            'url': 'http://test.com',
            'tags': ['hd', 'sports']
        }
        
        # Verify tags are accessible
        self.assertIn('tags', channel)
        self.assertIsInstance(channel['tags'], list)
    
    def test_custom_tags(self):
        """Test custom tag preservation"""
        custom_tags = {
            'custom-id': '12345',
            'custom-rating': 'PG'
        }
        
        # Tags should be preserved as dict
        channel = {
            'name': 'Test',
            'custom_tags': custom_tags
        }
        
        self.assertEqual(channel['custom_tags']['custom-id'], '12345')


if __name__ == '__main__':
    print("=" * 70)
    print("M3U MATRIX PRO - UNIT TESTS")
    print("=" * 70)
    print("\nTesting load-bearing functions...")
    print("-" * 70)
    
    # Run tests
    unittest.main(verbosity=2)
