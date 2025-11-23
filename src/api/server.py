"""
FastAPI Server for ScheduleFlow

REST API endpoints:
- GET /api/schedule - Get current schedule
- POST /api/schedule - Create new schedule
- GET /api/channels - List all channels
- POST /api/channels - Add channel
- GET /api/validate - Validate channels
- POST /api/validate - Start validation
- GET /api/status - Get operation status
- POST /api/export - Export to M3U format
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Channel, Schedule, ValidationResult
from core.scheduler import ScheduleEngine
from core.file_handler import FileHandler
from core.validator import ChannelValidator
from core.versioning import VersionManager
from core.backup import BackupManager
from core.paths import CrossPlatformPath, get_app_data_dir, get_cache_dir
from core.stripper import StripperManager, MediaExtractor

logger = logging.getLogger(__name__)

# Global app instance (singleton)
_app_instance = None


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="ScheduleFlow API",
        description="REST API for professional playlist scheduling",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components
    scheduler = ScheduleEngine()
    file_handler = FileHandler()
    validator = ChannelValidator()
    
    # Week 2: File Management
    app_data_dir = get_app_data_dir("ScheduleFlow")
    version_manager = VersionManager(app_data_dir / "versions")
    backup_manager = BackupManager(app_data_dir / "backups", retention_days=30)
    
    # Week 3: Media Stripper
    stripper_dir = app_data_dir / "stripped_media"
    stripper_manager = StripperManager(stripper_dir)
    
    # State
    app.state.channels: List[Channel] = []
    app.state.current_schedule: Optional[Schedule] = None
    app.state.validation_results: List[ValidationResult] = []
    app.state.is_validating = False
    app.state.version_manager = version_manager
    app.state.backup_manager = backup_manager
    app.state.stripper_manager = stripper_manager
    
    # ===== HEALTH & INFO =====
    
    @app.get("/api/system-version")
    def get_system_version():
        """Get system version"""
        return {
            "version": "2.0.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/api/status")
    def get_status():
        """Get current application status"""
        return {
            "channels_loaded": len(app.state.channels),
            "schedule_exists": app.state.current_schedule is not None,
            "validation_in_progress": app.state.is_validating,
            "validation_results_count": len(app.state.validation_results),
            "timestamp": datetime.now().isoformat()
        }
    
    # ===== CHANNELS =====
    
    @app.get("/api/channels")
    def list_channels():
        """Get all loaded channels"""
        return {
            "count": len(app.state.channels),
            "channels": [c.to_dict() for c in app.state.channels]
        }
    
    @app.post("/api/channels")
    def add_channel(channel_data: Dict[str, Any]):
        """Add a new channel"""
        try:
            channel = Channel(
                name=channel_data.get("name", "Unknown"),
                url=channel_data.get("url", ""),
                group=channel_data.get("group", "Other"),
                logo=channel_data.get("logo", ""),
                tvg_id=channel_data.get("tvg_id", ""),
                tvg_name=channel_data.get("tvg_name", ""),
                custom_tags=channel_data.get("custom_tags", {})
            )
            app.state.channels.append(channel)
            logger.info(f"Added channel: {channel.name}")
            return {
                "status": "success",
                "channel": channel.to_dict()
            }
        except Exception as e:
            logger.error(f"Failed to add channel: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/channels/import")
    def import_m3u(file_path: str):
        """Import channels from M3U file"""
        try:
            channels = file_handler.parse_m3u_file(file_path)
            app.state.channels = channels
            logger.info(f"Imported {len(channels)} channels from {file_path}")
            return {
                "status": "success",
                "count": len(channels),
                "channels": [c.to_dict() for c in channels]
            }
        except Exception as e:
            logger.error(f"Failed to import M3U: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== SCHEDULE =====
    
    @app.get("/api/schedule")
    def get_schedule():
        """Get current schedule"""
        if not app.state.current_schedule:
            return {
                "status": "no_schedule",
                "entries": []
            }
        
        return {
            "status": "success",
            "entries": [e.to_dict() for e in app.state.current_schedule.entries],
            "num_days": app.state.current_schedule.num_days
        }
    
    @app.post("/api/schedule/create")
    def create_schedule(
        show_duration: int = 30,
        num_days: int = 7,
        max_consecutive: int = 3
    ):
        """Create a new intelligent schedule"""
        try:
            if not app.state.channels:
                raise ValueError("No channels loaded")
            
            schedule = scheduler.create_smart_schedule(
                channels=app.state.channels,
                show_duration=show_duration,
                num_days=num_days,
                max_consecutive=max_consecutive
            )
            app.state.current_schedule = schedule
            logger.info(f"Created schedule with {len(schedule.entries)} entries")
            return {
                "status": "success",
                "entries_count": len(schedule.entries),
                "num_days": num_days
            }
        except Exception as e:
            logger.error(f"Failed to create schedule: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== VALIDATION =====
    
    @app.post("/api/validate")
    async def validate_channels_async(background_tasks: BackgroundTasks):
        """Start channel validation in background"""
        if app.state.is_validating:
            return {
                "status": "already_validating",
                "message": "Validation already in progress"
            }
        
        try:
            app.state.is_validating = True
            background_tasks.add_task(_validate_channels_task, app, validator)
            return {
                "status": "started",
                "message": "Validation started in background",
                "channels_count": len(app.state.channels)
            }
        except Exception as e:
            app.state.is_validating = False
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/validate/results")
    def get_validation_results():
        """Get validation results"""
        return {
            "in_progress": app.state.is_validating,
            "results_count": len(app.state.validation_results),
            "results": [r.to_dict() for r in app.state.validation_results]
        }
    
    # ===== EXPORT =====
    
    @app.post("/api/export/m3u")
    def export_m3u(output_path: Optional[str] = None):
        """Export schedule/channels to M3U file"""
        try:
            if not app.state.channels:
                raise ValueError("No channels to export")
            
            if not output_path:
                output_path = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u"
            
            success = file_handler.save_m3u_file(output_path, app.state.channels)
            if not success:
                raise ValueError(f"Failed to write to {output_path}")
            
            logger.info(f"Exported {len(app.state.channels)} channels to {output_path}")
            return {
                "status": "success",
                "file": output_path,
                "channels_count": len(app.state.channels)
            }
        except Exception as e:
            logger.error(f"Failed to export M3U: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== WEEK 2: FILE VERSIONING =====
    
    @app.post("/api/versions/create")
    def create_version(file_path: str, message: str = ""):
        """Create a new version of a file"""
        try:
            file_full_path = Path(file_path)
            if not file_full_path.exists():
                raise ValueError(f"File not found: {file_path}")
            
            with open(file_full_path, 'r') as f:
                content = f.read()
            
            version = version_manager.create_version(
                file_path=str(file_path),
                content=content,
                message=message
            )
            logger.info(f"Created version {version.version_id} for {file_path}")
            return {
                "status": "success",
                "version": version.to_dict()
            }
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/versions/list")
    def list_versions():
        """List all file versions"""
        try:
            versions = version_manager.list_versions()
            return {
                "status": "success",
                "count": len(versions),
                "versions": versions
            }
        except Exception as e:
            logger.error(f"Failed to list versions: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/versions/{version_id}")
    def get_version_content(version_id: str):
        """Get content of a specific version"""
        try:
            content = version_manager.get_version_content(version_id)
            if not content:
                raise ValueError(f"Version {version_id} not found")
            
            return {
                "status": "success",
                "version_id": version_id,
                "content_length": len(content)
            }
        except Exception as e:
            logger.error(f"Failed to get version content: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/versions/restore")
    def restore_version(version_id: str, output_path: str):
        """Restore a specific version to a file"""
        try:
            result = version_manager.restore_version(
                version_id=version_id,
                output_path=Path(output_path)
            )
            if result.status != 'success':
                raise ValueError(result.message)
            
            logger.info(f"Restored {version_id} to {output_path}")
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Failed to restore version: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/versions/diff")
    def get_version_diff(version1: str, version2: str):
        """Get diff between two versions"""
        try:
            diff = version_manager.get_diff(version1, version2)
            return {"status": "success", "diff": diff}
        except Exception as e:
            logger.error(f"Failed to get diff: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== WEEK 2: BACKUPS =====
    
    @app.post("/api/backup/create")
    def create_backup(file_path: str, backup_name: str = None):
        """Create a compressed backup of a file"""
        try:
            result = backup_manager.create_backup(
                source_file=Path(file_path),
                backup_name=backup_name
            )
            if result.status != 'success':
                raise ValueError(result.message)
            
            logger.info(f"Backup created for {file_path}")
            return {"status": "success", "backup": result.data}
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/backup/list")
    def list_backups():
        """List all available backups"""
        try:
            backups = backup_manager.list_backups()
            stats = backup_manager.get_backup_stats()
            return {
                "status": "success",
                "count": len(backups),
                "backups": backups,
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/backup/restore")
    def restore_backup(backup_id: str, output_path: str):
        """Restore a file from backup"""
        try:
            result = backup_manager.restore_backup(
                backup_id=backup_id,
                output_path=Path(output_path)
            )
            if result.status != 'success':
                raise ValueError(result.message)
            
            logger.info(f"Backup {backup_id} restored to {output_path}")
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.delete("/api/backup/{backup_id}")
    def delete_backup(backup_id: str):
        """Delete a specific backup"""
        try:
            result = backup_manager.delete_backup(backup_id)
            if result.status != 'success':
                raise ValueError(result.message)
            
            logger.info(f"Backup {backup_id} deleted")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/backup/cleanup")
    def cleanup_old_backups():
        """Remove backups older than retention period"""
        try:
            result = backup_manager.cleanup_old_backups()
            if result.status != 'success':
                raise ValueError(result.message)
            
            logger.info(f"Backup cleanup complete: {result.data}")
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== WEEK 2: PATHS & PLATFORM INFO =====
    
    @app.get("/api/platform/info")
    def get_platform_info():
        """Get platform and path information"""
        try:
            platform_info = CrossPlatformPath.get_platform_info()
            app_data = str(get_app_data_dir("ScheduleFlow"))
            cache_dir = str(get_cache_dir("ScheduleFlow"))
            
            return {
                "status": "success",
                "platform": platform_info,
                "app_data_dir": app_data,
                "cache_dir": cache_dir
            }
        except Exception as e:
            logger.error(f"Failed to get platform info: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ===== WEEK 3: MEDIA STRIPPER =====
    
    @app.post("/api/strip/scan")
    def strip_scan(url: str, html_content: str = None):
        """Scan a website for media and extract playlist"""
        try:
            import requests
            
            if not html_content:
                # Fetch HTML if not provided
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                html_content = response.text
            
            # Scan for media
            result = app.state.stripper_manager.scan_website(url, html_content)
            logger.info(f"Stripped {result.get('media_count', 0)} media items from {url}")
            return result
        except Exception as e:
            logger.error(f"Stripper scan failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/strip/progress")
    def strip_progress():
        """Get current/last stripper scan progress"""
        try:
            current = app.state.stripper_manager.get_current_scan()
            if not current:
                return {"status": "idle", "message": "No active scan"}
            
            return {
                "status": "success",
                "scan": current
            }
        except Exception as e:
            logger.error(f"Failed to get stripper progress: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/strip/results")
    def strip_results():
        """Get stripper scan results/history"""
        try:
            history = app.state.stripper_manager.get_scan_history()
            return {
                "status": "success",
                "total_scans": len(history),
                "results": history
            }
        except Exception as e:
            logger.error(f"Failed to get stripper results: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/strip/clear")
    def strip_clear():
        """Clear stripper history"""
        try:
            app.state.stripper_manager.clear_history()
            logger.info("Stripper history cleared")
            return {"status": "success", "message": "History cleared"}
        except Exception as e:
            logger.error(f"Failed to clear stripper history: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    return app


async def _validate_channels_task(app: FastAPI, validator: ChannelValidator):
    """Background task for channel validation"""
    try:
        app.state.validation_results = validator.validate_channels_batch(
            app.state.channels
        )
        logger.info(f"Validation complete: {len(app.state.validation_results)} results")
    except Exception as e:
        logger.error(f"Validation task failed: {e}")
    finally:
        app.state.is_validating = False


def get_app_instance() -> FastAPI:
    """Get or create singleton FastAPI app instance"""
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
        logger.info("FastAPI app instance created")
    return _app_instance


# Create app instance on module import
app = get_app_instance()
