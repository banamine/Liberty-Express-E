import subprocess
import threading
from pathlib import Path
from typing import List, Optional, Callable
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self._stop_processing = False
        self.progress_callbacks = []

    def add_progress_callback(self, callback: Callable):
        """Add callback for progress updates"""
        self.progress_callbacks.append(callback)

    def notify_progress(self, current: int, total: int, message: str = ""):
        """Notify all progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(current, total, message)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")

    def stop_processing(self):
        """Signal to stop all processing"""
        self._stop_processing = True

    def batch_process_episodes(self, episodes: List[dict], operations: List[str]) -> List[dict]:
        """Process multiple episodes in batch"""
        if self._stop_processing:
            return []

        processed = []
        total = len(episodes)
        
        for i, episode in enumerate(episodes):
            if self._stop_processing:
                break
                
            processed_ep = self._process_single_episode(episode, operations)
            processed.append(processed_ep)
            self.notify_progress(i + 1, total, f"Processing {processed_ep['key']}")
        
        return processed

    def _process_single_episode(self, episode: dict, operations: List[str]) -> dict:
        """Process a single episode with specified operations"""
        result = episode.copy()
        
        if 'validate' in operations and episode.get('url'):
            # Simple validation - just check if URL looks valid
            result['valid'] = episode['url'].startswith('http')
        
        result['imported_at'] = time.time()
        return result