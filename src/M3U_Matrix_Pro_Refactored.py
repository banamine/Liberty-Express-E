#!/usr/bin/env python3
"""
ScheduleFlow M3U Matrix Pro - Refactored Modular Version
Now using clean separation of concerns across multiple modules

REFACTORING COMPLETE - All 8 Steps:
1. ✅ Monolithic structure split into modular architecture
2. ✅ Cross-platform file management with backups
3. ✅ Structured JSON logging
4. ✅ Enhanced media stripper (Selenium + robots.txt)
5. ✅ Scheduling logic with timezone support
6. ✅ API layer (FastAPI integration)
7. ✅ Threading model (ThreadPoolExecutor)
8. ✅ Configuration management (YAML)
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import refactored modules
from core.config_manager import ConfigManager, get_config
from core.logging_manager import LoggingManager, initialize_logging
from core.file_manager import FileManager
from core.threading_manager import ThreadPool, get_thread_pool
from core.cooldown import CooldownManager, CooldownValidator
from core.timestamps import TimestampParser
from core.validation import ScheduleValidator, DuplicateDetector, ConflictDetector
from core.scheduling import ScheduleEngine
from stripper.enhanced_stripper import EnhancedMediaStripper
from core.database import DatabaseManager

# Configure logging first
config = get_config()
initialize_logging(config.raw_config)
logger = logging.getLogger(__name__)


class ScheduleFlowApplication:
    """Main application class using refactored modules"""
    
    def __init__(self, config_path: str = "config/scheduleflow.yaml"):
        """Initialize application with all modules"""
        logger.info("Initializing ScheduleFlow Application...")
        
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize managers
        self.file_manager = FileManager(
            backup_dir=self.config.get("storage.backups_dir"),
            backup_retention_days=self.config.get("storage.backup_retention_days")
        )
        
        self.thread_pool = ThreadPool(
            max_workers=self.config.get("threading.max_workers")
        )
        
        self.cooldown_manager = CooldownManager(
            history_file=Path(self.config.get("storage.schedules_dir")) / "cooldown_history.json"
        )
        
        self.schedule_engine = ScheduleEngine(self.cooldown_manager)
        
        self.media_stripper = EnhancedMediaStripper(
            headless=self.config.get("media_stripper.headless")
        )
        
        self.database = DatabaseManager(
            db_path=Path(self.config.get("storage.schedules_dir")) / "scheduleflow.db"
        )
        
        logger.info("ScheduleFlow Application initialized successfully")
    
    def create_intelligent_schedule(self, videos: list, duration_seconds: int) -> dict:
        """Create an intelligent schedule using the scheduling engine"""
        logger.info(f"Creating schedule for {len(videos)} videos, {duration_seconds}s duration")
        
        from datetime import datetime, timezone
        start_time = datetime.now(tz=timezone.utc)
        
        schedule = self.schedule_engine.create_schedule_intelligent(
            videos=videos,
            start_time=start_time,
            total_duration=duration_seconds,
            timezone_str=self.config.get("scheduling.timezone"),
            auto_fill=self.config.get("scheduling.auto_fill"),
            category_balancing=self.config.get("scheduling.category_balancing")
        )
        
        # Backup schedule
        schedule_path = Path(self.config.get("storage.schedules_dir")) / "current_schedule.json"
        import json
        with open(schedule_path, 'w') as f:
            json.dump(schedule, f)
        
        self.file_manager.create_backup(str(schedule_path), "auto_save")
        
        return schedule
    
    def extract_media_from_website(self, url: str) -> list:
        """Extract media URLs from website"""
        logger.info(f"Extracting media from: {url}")
        
        urls = self.media_stripper.extract_media_urls(
            url=url,
            respect_robots_txt=self.config.get("media_stripper.respect_robots_txt")
        )
        
        logger.info(f"Found {len(urls)} media URLs")
        return urls
    
    def validate_schedule(self, events: list) -> dict:
        """Validate schedule for conflicts and compliance"""
        logger.info(f"Validating schedule with {len(events)} events")
        
        validator = ScheduleValidator()
        valid, errors = validator.validate_schedule(events)
        
        if not valid:
            logger.warning(f"Validation errors: {errors}")
            return {"valid": False, "errors": errors}
        
        # Check for conflicts
        detector = ConflictDetector()
        valid, conflicts = detector.validate_no_conflicts(events)
        
        if not valid:
            logger.warning(f"Conflicts detected: {len(conflicts)}")
        
        # Check for duplicates
        dup_detector = DuplicateDetector()
        duplicates = dup_detector.find_duplicates(events)
        
        return {
            "valid": valid,
            "conflicts": conflicts,
            "duplicates": duplicates,
            "event_count": len(events)
        }
    
    def execute_background_task(self, task_func, task_id: str, *args, **kwargs):
        """Execute a task in background thread pool"""
        return self.thread_pool.submit(task_id, task_func, *args, **kwargs)
    
    def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down ScheduleFlow Application...")
        
        self.thread_pool.shutdown(wait=True)
        self.media_stripper.close()
        
        logger.info("Shutdown complete")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ScheduleFlow M3U Matrix Pro - Refactored")
    parser.add_argument('--config', default='config/scheduleflow.yaml', help='Config file path')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Initialize application
    app = ScheduleFlowApplication(args.config)
    
    if args.test:
        logger.info("Running in test mode...")
        
        # Test schedule creation
        test_videos = [
            {"url": "http://example.com/video1.mp4", "duration": 300, "category": "News"},
            {"url": "http://example.com/video2.mp4", "duration": 600, "category": "Sports"},
            {"url": "http://example.com/video3.mp4", "duration": 450, "category": "News"},
        ]
        
        schedule = app.create_intelligent_schedule(test_videos, 3600)
        logger.info(f"Generated schedule: {schedule}")
    
    app.shutdown()


if __name__ == "__main__":
    main()
