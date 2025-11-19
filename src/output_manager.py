#!/usr/bin/env python3
"""
Output Manager - Centralized file organization system for M3U Matrix Pro
Handles all output directories and ensures clean, organized file structure
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class OutputManager:
    """Manages all output directories and file organization"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the Output Manager
        
        Args:
            base_path: Custom base path for all outputs. If None, uses default.
        """
        # Load configuration or use default
        self.config = self._load_config()
        
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Use configured path or default to project directory
            default_path = self.config.get('output_base_path')
            if default_path:
                self.base_path = Path(default_path)
            else:
                # Default to project directory/M3U_Matrix_Output
                self.base_path = Path.cwd() / "M3U_Matrix_Output"
        
        # Initialize all directory paths
        self._init_directory_structure()
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load output configuration from settings file"""
        config_file = Path.cwd() / "output_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save output configuration"""
        config_file = Path.cwd() / "output_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config
    
    def _init_directory_structure(self):
        """Initialize all directory paths"""
        
        # Generated pages (HTML players)
        self.pages_dir = self.base_path / "generated_pages"
        self.nexus_tv_dir = self.pages_dir / "nexus_tv"
        self.buffer_tv_dir = self.pages_dir / "buffer_tv"
        self.multi_channel_dir = self.pages_dir / "multi_channel"
        self.standalone_dir = self.pages_dir / "standalone"
        self.simple_player_dir = self.pages_dir / "simple_player"
        self.rumble_channel_dir = self.pages_dir / "rumble_channel"
        self.stream_hub_dir = self.pages_dir / "stream_hub"
        self.web_iptv_dir = self.pages_dir / "web_iptv"
        
        # Playlists
        self.playlists_dir = self.base_path / "playlists"
        self.playlists_imported_dir = self.playlists_dir / "imported"
        self.playlists_exported_dir = self.playlists_dir / "exported"
        self.playlists_templates_dir = self.playlists_dir / "templates"
        
        # JSON data
        self.json_dir = self.base_path / "json_data"
        self.json_channel_dir = self.json_dir / "channel_data"
        self.json_settings_dir = self.json_dir / "settings"
        self.json_exports_dir = self.json_dir / "exports"
        
        # Thumbnails
        self.thumbnails_dir = self.base_path / "thumbnails"
        self.thumbnails_logos_dir = self.thumbnails_dir / "channel_logos"
        self.thumbnails_auto_dir = self.thumbnails_dir / "auto_captured"
        self.thumbnails_imported_dir = self.thumbnails_dir / "imported"
        
        # Screenshots
        self.screenshots_dir = self.base_path / "screenshots"
        self.screenshots_manual_dir = self.screenshots_dir / "manual"
        self.screenshots_auto_25_dir = self.screenshots_dir / "auto_25percent"
        self.screenshots_auto_75_dir = self.screenshots_dir / "auto_75percent"
        
        # Backups
        self.backups_dir = self.base_path / "backups"
        self.backups_daily_dir = self.backups_dir / "daily"
        self.backups_weekly_dir = self.backups_dir / "weekly"
        self.backups_manual_dir = self.backups_dir / "manual"
        
        # Saves
        self.saves_dir = self.base_path / "saves"
        self.saves_sessions_dir = self.saves_dir / "sessions"
        self.saves_presets_dir = self.saves_dir / "presets"
        self.saves_configs_dir = self.saves_dir / "configurations"
        
        # EPG data
        self.epg_dir = self.base_path / "epg_data"
        self.epg_xmltv_dir = self.epg_dir / "xmltv"
        self.epg_cached_dir = self.epg_dir / "cached"
        
        # Metadata
        self.metadata_dir = self.base_path / "metadata"
        self.metadata_channel_dir = self.metadata_dir / "channel_info"
        self.metadata_video_dir = self.metadata_dir / "video_metadata"
        self.metadata_rumble_dir = self.metadata_dir / "rumble_data"
        
        # Text exports
        self.text_exports_dir = self.base_path / "text_exports"
        self.text_channel_lists_dir = self.text_exports_dir / "channel_lists"
        self.text_csv_dir = self.text_exports_dir / "csv_exports"
        self.text_bookmarks_dir = self.text_exports_dir / "bookmarks"
        
        # Temp
        self.temp_dir = self.base_path / "temp"
        self.temp_cache_dir = self.temp_dir / "cache"
        self.temp_downloads_dir = self.temp_dir / "downloads"
        self.temp_processing_dir = self.temp_dir / "processing"
        
        # Logs
        self.logs_dir = self.base_path / "logs"
        self.logs_app_dir = self.logs_dir / "app_logs"
        self.logs_error_dir = self.logs_dir / "error_logs"
        self.logs_workflow_dir = self.logs_dir / "workflow_logs"
        
        # Recordings (future feature)
        self.recordings_dir = self.base_path / "recordings"
        
        # Redis data
        self.redis_dir = self.base_path / "redis_data"
    
    def _create_directories(self):
        """Create all directories if they don't exist"""
        all_dirs = [
            # Base
            self.base_path,
            
            # Generated pages
            self.pages_dir,
            self.nexus_tv_dir,
            self.buffer_tv_dir,
            self.multi_channel_dir,
            self.standalone_dir,
            self.simple_player_dir,
            self.rumble_channel_dir,
            self.stream_hub_dir,
            self.web_iptv_dir,
            
            # Playlists
            self.playlists_dir,
            self.playlists_imported_dir,
            self.playlists_exported_dir,
            self.playlists_templates_dir,
            
            # JSON
            self.json_dir,
            self.json_channel_dir,
            self.json_settings_dir,
            self.json_exports_dir,
            
            # Thumbnails
            self.thumbnails_dir,
            self.thumbnails_logos_dir,
            self.thumbnails_auto_dir,
            self.thumbnails_imported_dir,
            
            # Screenshots
            self.screenshots_dir,
            self.screenshots_manual_dir,
            self.screenshots_auto_25_dir,
            self.screenshots_auto_75_dir,
            
            # Backups
            self.backups_dir,
            self.backups_daily_dir,
            self.backups_weekly_dir,
            self.backups_manual_dir,
            
            # Saves
            self.saves_dir,
            self.saves_sessions_dir,
            self.saves_presets_dir,
            self.saves_configs_dir,
            
            # EPG
            self.epg_dir,
            self.epg_xmltv_dir,
            self.epg_cached_dir,
            
            # Metadata
            self.metadata_dir,
            self.metadata_channel_dir,
            self.metadata_video_dir,
            self.metadata_rumble_dir,
            
            # Text exports
            self.text_exports_dir,
            self.text_channel_lists_dir,
            self.text_csv_dir,
            self.text_bookmarks_dir,
            
            # Temp
            self.temp_dir,
            self.temp_cache_dir,
            self.temp_downloads_dir,
            self.temp_processing_dir,
            
            # Logs
            self.logs_dir,
            self.logs_app_dir,
            self.logs_error_dir,
            self.logs_workflow_dir,
            
            # Recordings
            self.recordings_dir,
            
            # Redis
            self.redis_dir
        ]
        
        for directory in all_dirs:
            directory.mkdir(exist_ok=True, parents=True)
    
    def get_page_output_dir(self, page_type: str) -> Path:
        """
        Get the output directory for a specific page type
        
        Args:
            page_type: Type of page (nexus_tv, buffer_tv, etc.)
        
        Returns:
            Path to the output directory
        """
        page_dirs = {
            'nexus_tv': self.nexus_tv_dir,
            'buffer_tv': self.buffer_tv_dir,
            'multi_channel': self.multi_channel_dir,
            'standalone': self.standalone_dir,
            'simple_player': self.simple_player_dir,
            'rumble_channel': self.rumble_channel_dir,
            'stream_hub': self.stream_hub_dir,
            'web_iptv': self.web_iptv_dir
        }
        return page_dirs.get(page_type, self.pages_dir)
    
    def get_export_path(self, export_type: str, filename: str) -> Path:
        """
        Get the path for an export file
        
        Args:
            export_type: Type of export (m3u, json, txt, csv, etc.)
            filename: Name of the file
        
        Returns:
            Full path for the export file
        """
        export_dirs = {
            'm3u': self.playlists_exported_dir,
            'm3u8': self.playlists_exported_dir,
            'json': self.json_exports_dir,
            'txt': self.text_channel_lists_dir,
            'csv': self.text_csv_dir,
            'bookmark': self.text_bookmarks_dir,
            'xmltv': self.epg_xmltv_dir
        }
        
        export_dir = export_dirs.get(export_type.lower(), self.text_exports_dir)
        return export_dir / filename
    
    def get_thumbnail_path(self, channel_name: str, thumbnail_type: str = 'logo') -> Path:
        """
        Get the path for a thumbnail
        
        Args:
            channel_name: Name of the channel
            thumbnail_type: Type of thumbnail (logo, auto, imported)
        
        Returns:
            Path for the thumbnail
        """
        thumbnail_dirs = {
            'logo': self.thumbnails_logos_dir,
            'auto': self.thumbnails_auto_dir,
            'imported': self.thumbnails_imported_dir
        }
        
        thumbnail_dir = thumbnail_dirs.get(thumbnail_type, self.thumbnails_logos_dir)
        # Sanitize channel name for filename
        safe_name = "".join(c for c in channel_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return thumbnail_dir / f"{safe_name}.png"
    
    def get_backup_path(self, backup_type: str = 'manual') -> Path:
        """
        Get the path for a backup with timestamp
        
        Args:
            backup_type: Type of backup (daily, weekly, manual)
        
        Returns:
            Path for the backup file
        """
        backup_dirs = {
            'daily': self.backups_daily_dir,
            'weekly': self.backups_weekly_dir,
            'manual': self.backups_manual_dir
        }
        
        backup_dir = backup_dirs.get(backup_type, self.backups_manual_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return backup_dir / f"backup_{backup_type}_{timestamp}.json"
    
    def clean_temp_files(self):
        """Clean all temporary files"""
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            # Recreate temp subdirectories
            self.temp_cache_dir.mkdir(exist_ok=True)
            self.temp_downloads_dir.mkdir(exist_ok=True)
            self.temp_processing_dir.mkdir(exist_ok=True)
    
    def set_output_base_path(self, new_path: Path):
        """
        Change the base output path and move existing files
        
        Args:
            new_path: New base path for all outputs
        """
        old_path = self.base_path
        self.base_path = Path(new_path)
        
        # Reinitialize directory structure with new base
        self._init_directory_structure()
        self._create_directories()
        
        # Save configuration
        self.save_config({'output_base_path': str(self.base_path)})
        
        # Optionally move existing files
        if old_path.exists() and old_path != self.base_path:
            response = input(f"Move existing files from {old_path} to {self.base_path}? (y/n): ")
            if response.lower() == 'y':
                self._move_existing_files(old_path, self.base_path)
    
    def _move_existing_files(self, old_base: Path, new_base: Path):
        """Move files from old base to new base"""
        try:
            if old_base.exists():
                for item in old_base.iterdir():
                    if item.is_file():
                        shutil.move(str(item), str(new_base / item.name))
                    elif item.is_dir():
                        target = new_base / item.name
                        if target.exists():
                            shutil.rmtree(target)
                        shutil.move(str(item), str(target))
                print(f"Successfully moved files from {old_base} to {new_base}")
        except Exception as e:
            print(f"Error moving files: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the output structure"""
        info = {
            'base_path': str(self.base_path),
            'total_size': self._get_directory_size(self.base_path),
            'directories': {
                'pages': self._count_files(self.pages_dir),
                'playlists': self._count_files(self.playlists_dir),
                'thumbnails': self._count_files(self.thumbnails_dir),
                'screenshots': self._count_files(self.screenshots_dir),
                'backups': self._count_files(self.backups_dir),
                'saves': self._count_files(self.saves_dir),
                'logs': self._count_files(self.logs_dir)
            }
        }
        return info
    
    def _get_directory_size(self, path: Path) -> str:
        """Get human-readable directory size"""
        total = 0
        if path.exists():
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        
        # Convert to human-readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024.0:
                return f"{total:.2f} {unit}"
            total /= 1024.0
        return f"{total:.2f} TB"
    
    def _count_files(self, path: Path) -> int:
        """Count files in a directory"""
        if not path.exists():
            return 0
        return sum(1 for item in path.rglob('*') if item.is_file())


# Singleton instance
_output_manager = None

def get_output_manager(base_path: Optional[Path] = None) -> OutputManager:
    """Get or create the singleton OutputManager instance"""
    global _output_manager
    if _output_manager is None:
        _output_manager = OutputManager(base_path)
    return _output_manager