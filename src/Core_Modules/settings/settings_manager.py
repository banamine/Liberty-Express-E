"""
Settings Manager - Handles application configuration and user preferences
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil


class SettingsManager:
    """
    Manages application settings including loading, saving, importing, and exporting.
    Provides centralized configuration management with validation and backup.
    """
    
    DEFAULT_SETTINGS = {
        "window_geometry": "1600x950",
        "theme": "dark",
        "auto_check_channels": False,
        "default_epg_url": "",
        "recent_files": [],
        "cache_thumbnails": True,
        "use_ffmpeg_extraction": False,
        "output_base_dir": None,  # None means use default
        "max_recent_files": 10,
        "auto_save_interval": 300,  # seconds
        "enable_auto_save": True,
        "default_group": "Other",
        "check_timeout": 5,  # seconds for channel validation
        "enable_logging": True,
        "log_level": "INFO",
        "ui_scale": 1.0,
        "show_tooltips": True,
        "confirm_delete": True,
        "auto_organize_on_load": True,
        "preserve_channel_numbers": False,
        "backup_on_save": True,
        "max_backups": 5
    }
    
    def __init__(self, settings_file: str = "m3u_matrix_settings.json"):
        """
        Initialize the settings manager.
        
        Args:
            settings_file: Path to the settings JSON file
        """
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from file with error handling and validation"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    if not content:
                        self.logger.warning("Settings file is empty, using defaults")
                        self.settings = self.DEFAULT_SETTINGS.copy()
                    else:
                        try:
                            loaded_settings = json.loads(content)
                            # Merge with defaults to ensure all keys exist
                            self.settings = {**self.DEFAULT_SETTINGS, **loaded_settings}
                            self._validate_settings()
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Settings file corrupted: {e}, using defaults")
                            self._backup_corrupted_settings()
                            self.settings = self.DEFAULT_SETTINGS.copy()
            else:
                self.logger.info("Settings file not found, creating with defaults")
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.save_settings()
        
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def _validate_settings(self) -> None:
        """Validate loaded settings and fix invalid values"""
        # Validate window geometry
        if not isinstance(self.settings.get('window_geometry'), str):
            self.settings['window_geometry'] = self.DEFAULT_SETTINGS['window_geometry']
        
        # Validate recent files list
        if not isinstance(self.settings.get('recent_files'), list):
            self.settings['recent_files'] = []
        
        # Limit recent files to max
        max_recent = self.settings.get('max_recent_files', 10)
        if len(self.settings['recent_files']) > max_recent:
            self.settings['recent_files'] = self.settings['recent_files'][:max_recent]
        
        # Validate numeric settings
        numeric_settings = ['auto_save_interval', 'check_timeout', 'ui_scale', 'max_backups']
        for key in numeric_settings:
            if key in self.settings:
                try:
                    float(self.settings[key])
                except (TypeError, ValueError):
                    self.settings[key] = self.DEFAULT_SETTINGS.get(key, 1)
        
        # Validate boolean settings
        boolean_settings = ['auto_check_channels', 'cache_thumbnails', 'use_ffmpeg_extraction',
                          'enable_auto_save', 'enable_logging', 'show_tooltips',
                          'confirm_delete', 'auto_organize_on_load', 'preserve_channel_numbers',
                          'backup_on_save']
        for key in boolean_settings:
            if key in self.settings and not isinstance(self.settings[key], bool):
                self.settings[key] = self.DEFAULT_SETTINGS.get(key, False)
    
    def _backup_corrupted_settings(self) -> None:
        """Backup corrupted settings file"""
        try:
            backup_name = f"{self.settings_file}.corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.settings_file, backup_name)
            self.logger.info(f"Backed up corrupted settings to {backup_name}")
        except Exception as e:
            self.logger.error(f"Failed to backup corrupted settings: {e}")
    
    def save_settings(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if enabled
            if self.settings.get('backup_on_save', True) and self.settings_file.exists():
                self._create_settings_backup()
            
            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            
            self.logger.debug("Settings saved successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def _create_settings_backup(self) -> None:
        """Create a backup of current settings file"""
        try:
            backup_dir = Path("settings_backups")
            backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"settings_backup_{timestamp}.json"
            
            # Copy current settings
            shutil.copy2(self.settings_file, backup_file)
            
            # Clean old backups
            self._clean_old_backups(backup_dir)
            
        except Exception as e:
            self.logger.warning(f"Failed to create settings backup: {e}")
    
    def _clean_old_backups(self, backup_dir: Path) -> None:
        """Remove old backup files exceeding max_backups limit"""
        try:
            max_backups = self.settings.get('max_backups', 5)
            backups = sorted(backup_dir.glob("settings_backup_*.json"))
            
            if len(backups) > max_backups:
                for old_backup in backups[:-max_backups]:
                    old_backup.unlink()
                    self.logger.debug(f"Removed old backup: {old_backup}")
        
        except Exception as e:
            self.logger.warning(f"Failed to clean old backups: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple settings at once.
        
        Args:
            updates: Dictionary of settings to update
        """
        self.settings.update(updates)
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.logger.info("Settings reset to defaults")
    
    def export_settings(self, export_path: Path) -> bool:
        """
        Export settings to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            self.logger.info(f"Settings exported to {export_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """
        Import settings from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            if isinstance(imported_settings, dict):
                # Backup current settings
                self._create_settings_backup()
                
                # Import and validate
                self.settings = {**self.DEFAULT_SETTINGS, **imported_settings}
                self._validate_settings()
                self.save_settings()
                
                self.logger.info(f"Settings imported from {import_path}")
                return True
            else:
                self.logger.error("Invalid settings format in import file")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to recent files list.
        
        Args:
            file_path: Path to add to recent files
        """
        recent = self.settings.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to beginning
        recent.insert(0, file_path)
        
        # Limit to max recent files
        max_recent = self.settings.get('max_recent_files', 10)
        self.settings['recent_files'] = recent[:max_recent]
    
    def get_recent_files(self) -> List[str]:
        """
        Get list of recent files.
        
        Returns:
            List of recent file paths
        """
        return self.settings.get('recent_files', [])
    
    def clear_recent_files(self) -> None:
        """Clear the recent files list"""
        self.settings['recent_files'] = []
    
    def get_output_directory(self) -> Path:
        """
        Get the configured output directory.
        
        Returns:
            Path to output directory
        """
        custom_dir = self.settings.get('output_base_dir')
        if custom_dir and Path(custom_dir).exists():
            return Path(custom_dir)
        return Path("M3U_Matrix_Output")
    
    def set_output_directory(self, directory: str) -> None:
        """
        Set the output directory.
        
        Args:
            directory: Path to output directory
        """
        self.settings['output_base_dir'] = directory
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings as a dictionary.
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()