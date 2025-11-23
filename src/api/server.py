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
    
    # State
    app.state.channels: List[Channel] = []
    app.state.current_schedule: Optional[Schedule] = None
    app.state.validation_results: List[ValidationResult] = []
    app.state.is_validating = False
    
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
