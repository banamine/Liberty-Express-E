"""
Progress Tracking System for ScheduleFlow

Tracks long-running operations (validation, stripping, backups) with progress updates.
"""

from datetime import datetime
from typing import Dict, Optional
import threading


class ProgressTracker:
    """Tracks progress of async operations"""
    
    def __init__(self, operation_id: str, total_steps: int):
        self.operation_id = operation_id
        self.total_steps = total_steps
        self.current_step = 0
        self.status = "pending"  # pending, running, completed, failed, cancelled
        self.message = ""
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.error = None
        self.lock = threading.Lock()
    
    def start(self):
        """Mark operation as started"""
        with self.lock:
            self.status = "running"
            self.message = "Operation started"
    
    def update(self, step: int, message: str = ""):
        """Update progress"""
        with self.lock:
            self.current_step = min(step, self.total_steps)
            self.message = message
    
    def complete(self, message: str = ""):
        """Mark operation as completed"""
        with self.lock:
            self.status = "completed"
            self.current_step = self.total_steps
            self.message = message or "Operation completed"
            self.end_time = datetime.utcnow()
    
    def fail(self, error: str):
        """Mark operation as failed"""
        with self.lock:
            self.status = "failed"
            self.error = error
            self.end_time = datetime.utcnow()
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        with self.lock:
            percentage = (self.current_step / self.total_steps * 100) if self.total_steps > 0 else 0
            duration = None
            
            if self.end_time:
                duration = (self.end_time - self.start_time).total_seconds()
            elif self.status == "running":
                duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                'operation_id': self.operation_id,
                'status': self.status,
                'current_step': self.current_step,
                'total_steps': self.total_steps,
                'percentage': round(percentage, 1),
                'message': self.message,
                'started_at': self.start_time.isoformat(),
                'ended_at': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': round(duration, 2) if duration else None,
                'error': self.error
            }


class ProgressManager:
    """Manages multiple progress trackers"""
    
    def __init__(self):
        self.trackers: Dict[str, ProgressTracker] = {}
        self.lock = threading.Lock()
    
    def create_tracker(self, operation_id: str, total_steps: int) -> ProgressTracker:
        """Create new progress tracker"""
        with self.lock:
            tracker = ProgressTracker(operation_id, total_steps)
            self.trackers[operation_id] = tracker
            return tracker
    
    def get_tracker(self, operation_id: str) -> Optional[ProgressTracker]:
        """Get tracker by ID"""
        return self.trackers.get(operation_id)
    
    def get_progress(self, operation_id: str) -> Optional[Dict]:
        """Get progress for operation"""
        tracker = self.get_tracker(operation_id)
        if not tracker:
            return None
        return tracker.get_progress()
    
    def list_progress(self) -> Dict[str, Dict]:
        """List all active operations"""
        with self.lock:
            return {
                op_id: tracker.get_progress()
                for op_id, tracker in self.trackers.items()
            }
    
    def cleanup_completed(self):
        """Remove completed/failed operations (keep last 100)"""
        with self.lock:
            completed = [
                op_id for op_id, tracker in self.trackers.items()
                if tracker.status in ['completed', 'failed']
            ]
            
            if len(completed) > 100:
                for op_id in completed[:-100]:
                    del self.trackers[op_id]
