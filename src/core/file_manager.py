"""
File Management Module - Step 2 of refactoring
Cross-platform file handling with automatic backups and versioning
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import gzip
import json

logger = logging.getLogger(__name__)


class FileManager:
    """Manage files across Windows, macOS, and Linux with backups"""
    
    def __init__(self, backup_dir: Optional[str] = None, 
                 backup_retention_days: int = 30,
                 compression: str = "gzip"):
        """
        Initialize file manager
        
        Args:
            backup_dir: Directory to store backups (uses pathlib for cross-platform)
            backup_retention_days: Keep backups for N days
            compression: Compression method ('gzip' or 'none')
        """
        self.backup_dir = Path(backup_dir) if backup_dir else Path("backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_retention_days = backup_retention_days
        self.compression = compression
        logger.info(f"FileManager initialized with backup dir: {self.backup_dir}")
    
    def create_backup(self, source_path: str, backup_suffix: Optional[str] = None) -> Optional[Path]:
        """
        Create a timestamped backup of a file
        
        Args:
            source_path: Path to file to backup
            backup_suffix: Optional suffix (e.g., 'before_import')
        
        Returns:
            Path to backup file, or None if failed
        """
        source = Path(source_path)
        
        if not source.exists():
            logger.warning(f"Cannot backup non-existent file: {source}")
            return None
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{backup_suffix}" if backup_suffix else ""
        backup_name = f"{source.stem}_{timestamp}{suffix}{source.suffix}"
        
        # Create category subdirectory in backups
        category_dir = self.backup_dir / source.parent.name
        category_dir.mkdir(parents=True, exist_ok=True)
        
        backup_path = category_dir / backup_name
        
        try:
            if self.compression == "gzip" and source.suffix in ['.json', '.xml', '.m3u', '.m3u8']:
                # Compress text files
                with open(source, 'rb') as f_in:
                    with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = Path(f"{backup_path}.gz")
            else:
                # Copy without compression
                shutil.copy2(source, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            self._cleanup_old_backups(source.name)
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str, restore_to: Optional[str] = None) -> bool:
        """
        Restore a file from backup
        
        Args:
            backup_path: Path to backup file
            restore_to: Where to restore (if None, overwrites original)
        
        Returns:
            True if successful, False otherwise
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            logger.error(f"Backup file not found: {backup}")
            return False
        
        try:
            if str(backup).endswith('.gz'):
                # Decompress
                with gzip.open(backup, 'rb') as f_in:
                    restore_path = Path(restore_to) if restore_to else backup.with_suffix('')
                    with open(restore_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Copy directly
                restore_path = Path(restore_to) if restore_to else backup
                shutil.copy2(backup, restore_path)
            
            logger.info(f"Restored from backup: {backup} -> {restore_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def _cleanup_old_backups(self, filename: str) -> None:
        """Remove backups older than retention period"""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(days=self.backup_retention_days)
        
        try:
            for backup_file in self.backup_dir.rglob(f"{Path(filename).stem}_*"):
                if backup_file.stat().st_mtime < cutoff.timestamp():
                    backup_file.unlink()
                    logger.debug(f"Deleted old backup: {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def list_backups(self, original_filename: Optional[str] = None) -> List[Path]:
        """List all backups, optionally filtered by original filename"""
        if not self.backup_dir.exists():
            return []
        
        backups = list(self.backup_dir.rglob("*"))
        
        if original_filename:
            stem = Path(original_filename).stem
            backups = [b for b in backups if stem in b.name]
        
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)
    
    @staticmethod
    def get_app_data_dir(app_name: str) -> Path:
        """Get platform-specific application data directory"""
        import sys
        
        if sys.platform == "win32":
            # Windows: C:\Users\{user}\AppData\Local\{app_name}
            app_data = Path.home() / "AppData" / "Local" / app_name
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/{app_name}
            app_data = Path.home() / "Library" / "Application Support" / app_name
        else:
            # Linux: ~/.{app_name_lowercase}
            app_data = Path.home() / f".{app_name.lower()}"
        
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """Convert any path string to cross-platform Path object"""
        return Path(path).expanduser().resolve()


class FileWatcher:
    """Monitor file changes for auto-backup (optional)"""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.watched_files = {}
    
    def watch(self, filepath: str) -> None:
        """Start watching a file for changes"""
        path = Path(filepath)
        self.watched_files[str(path)] = path.stat().st_mtime
        logger.info(f"Now watching: {path}")
    
    def check_and_backup_if_changed(self, filepath: str) -> bool:
        """Check if file changed and backup if needed"""
        path = Path(filepath)
        
        if not path.exists():
            return False
        
        current_mtime = path.stat().st_mtime
        last_mtime = self.watched_files.get(str(path), 0)
        
        if current_mtime > last_mtime:
            logger.info(f"File changed, creating backup: {path}")
            self.file_manager.create_backup(str(path), "auto")
            self.watched_files[str(path)] = current_mtime
            return True
        
        return False
