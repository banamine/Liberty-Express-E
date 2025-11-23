"""
Threading Module - Step 7 of refactoring
Thread pool management with proper error handling
"""

import logging
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Callable, List, Any, Optional, Dict
import threading
import time

logger = logging.getLogger(__name__)


class ThreadPool:
    """Managed thread pool with error handling"""
    
    def __init__(self, max_workers: int = 4,
                 catch_exceptions: bool = True,
                 retry_failed: bool = True,
                 max_retries: int = 3):
        """
        Initialize thread pool
        
        Args:
            max_workers: Maximum concurrent threads
            catch_exceptions: Catch exceptions instead of crashing
            retry_failed: Retry failed tasks
            max_retries: Number of retries for failed tasks
        """
        self.max_workers = max_workers
        self.catch_exceptions = catch_exceptions
        self.retry_failed = retry_failed
        self.max_retries = max_retries
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[Future, Dict[str, Any]] = {}
        self.results = {}
        self.errors = {}
        logger.info(f"ThreadPool initialized with {max_workers} workers")
    
    def submit(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        """
        Submit a task to the thread pool
        
        Args:
            task_id: Unique task identifier
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            Future object
        """
        try:
            future = self.executor.submit(self._execute_with_error_handling, 
                                         task_id, func, args, kwargs)
            self.futures[future] = {
                'task_id': task_id,
                'func': func,
                'args': args,
                'kwargs': kwargs,
                'retries': 0,
                'submitted_time': time.time()
            }
            logger.debug(f"Task submitted: {task_id}")
            return future
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {e}")
            return None
    
    def _execute_with_error_handling(self, task_id: str, func: Callable,
                                    args: tuple, kwargs: dict) -> Any:
        """Execute task with error handling and retry logic"""
        retries = 0
        
        while retries <= self.max_retries:
            try:
                logger.debug(f"Executing task: {task_id} (attempt {retries + 1})")
                result = func(*args, **kwargs)
                logger.info(f"Task completed: {task_id}")
                self.results[task_id] = result
                return result
            except Exception as e:
                retries += 1
                
                if self.catch_exceptions:
                    logger.error(f"Task {task_id} failed (attempt {retries}): {e}")
                    
                    if retries <= self.max_retries and self.retry_failed:
                        logger.info(f"Retrying task {task_id}...")
                        time.sleep(1)  # Backoff before retry
                        continue
                    else:
                        self.errors[task_id] = str(e)
                        logger.error(f"Task {task_id} exhausted retries")
                        return None
                else:
                    raise
        
        return None
    
    def submit_batch(self, tasks: List[tuple]) -> List[Future]:
        """
        Submit multiple tasks at once
        
        Args:
            tasks: List of (task_id, func, args, kwargs) tuples
        
        Returns:
            List of Future objects
        """
        futures = []
        for task_id, func, *rest in tasks:
            args = rest[0] if rest else ()
            kwargs = rest[1] if len(rest) > 1 else {}
            future = self.submit(task_id, func, *args, **kwargs)
            if future:
                futures.append(future)
        
        return futures
    
    def wait_all(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for all submitted tasks to complete
        
        Args:
            timeout: Maximum time to wait in seconds
        
        Returns:
            Dictionary with results and errors
        """
        logger.info(f"Waiting for {len(self.futures)} tasks to complete...")
        
        try:
            for future in as_completed(self.futures.keys(), timeout=timeout):
                task_info = self.futures.pop(future)
                task_id = task_info['task_id']
                
                try:
                    result = future.result()
                    logger.debug(f"Task result: {task_id}")
                except Exception as e:
                    logger.error(f"Task exception: {task_id}: {e}")
                    self.errors[task_id] = str(e)
        
        except Exception as e:
            logger.error(f"Error waiting for tasks: {e}")
        
        return {
            'results': self.results,
            'errors': self.errors,
            'total': len(self.results) + len(self.errors)
        }
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool"""
        logger.info("Shutting down thread pool...")
        self.executor.shutdown(wait=wait)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        return {
            'pending_tasks': len(self.futures),
            'completed_tasks': len(self.results),
            'failed_tasks': len(self.errors),
            'max_workers': self.max_workers
        }


class BackgroundTask:
    """Decorator for background task execution"""
    
    def __init__(self, thread_pool: ThreadPool):
        self.thread_pool = thread_pool
    
    def __call__(self, func: Callable) -> Callable:
        """Wrap function to execute in background"""
        def wrapper(*args, **kwargs):
            task_id = f"{func.__name__}_{int(time.time() * 1000)}"
            return self.thread_pool.submit(task_id, func, *args, **kwargs)
        return wrapper


# Global thread pool
_global_thread_pool: Optional[ThreadPool] = None


def get_thread_pool(max_workers: int = 4) -> ThreadPool:
    """Get or create global thread pool"""
    global _global_thread_pool
    if _global_thread_pool is None:
        _global_thread_pool = ThreadPool(max_workers=max_workers)
    return _global_thread_pool
