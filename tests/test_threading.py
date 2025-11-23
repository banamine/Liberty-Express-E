"""Unit tests for threading_manager module"""

import unittest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.threading_manager import ThreadPool


class TestThreadPool(unittest.TestCase):
    """Test ThreadPool functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.pool = ThreadPool(max_workers=2)
    
    def tearDown(self):
        """Cleanup test fixtures"""
        self.pool.shutdown(wait=True)
    
    def test_submit_task(self):
        """Test submitting a task to the pool"""
        def test_func(x):
            return x * 2
        
        future = self.pool.submit("test_1", test_func, 5)
        
        self.assertIsNotNone(future)
        result = future.result(timeout=5)
        self.assertEqual(result, 10)
    
    def test_submit_batch(self):
        """Test submitting batch of tasks"""
        def add(a, b):
            return a + b
        
        tasks = [
            ("task_1", add, (1, 2)),
            ("task_2", add, (3, 4)),
            ("task_3", add, (5, 6))
        ]
        
        futures = self.pool.submit_batch(tasks)
        
        self.assertEqual(len(futures), 3)
    
    def test_task_error_handling(self):
        """Test error handling in thread pool"""
        def failing_func():
            raise ValueError("Test error")
        
        future = self.pool.submit("failing_task", failing_func)
        time.sleep(0.1)
        
        # Check that error was caught
        self.assertIn("failing_task", self.pool.errors)
    
    def test_wait_all(self):
        """Test waiting for all tasks"""
        def slow_func(duration):
            time.sleep(duration)
            return "done"
        
        self.pool.submit("task_1", slow_func, 0.1)
        self.pool.submit("task_2", slow_func, 0.1)
        
        results = self.pool.wait_all(timeout=5)
        
        self.assertEqual(len(results["results"]), 2)
    
    def test_pool_status(self):
        """Test getting pool status"""
        status = self.pool.get_status()
        
        self.assertIn("pending_tasks", status)
        self.assertIn("completed_tasks", status)
        self.assertIn("max_workers", status)
        self.assertEqual(status["max_workers"], 2)


if __name__ == '__main__':
    unittest.main()
