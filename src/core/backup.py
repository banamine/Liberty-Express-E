"""
Backup Management System for ScheduleFlow

Handles automatic backups, compression, rotation, and recovery.
"""

import json
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class BackupManager:
    """Manages automated backups with compression and retention"""
    
    def __init__(self, backup_dir: Path, retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.metadata_file = self.backup_dir / 'backups.json'
        self.backups = self._load_metadata()
    
    def _load_metadata(self) -> List[Dict]:
        """Load backup metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_metadata(self):
        """Save backup metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.backups, f, indent=2)
    
    def create_backup(self, source_file: Path, backup_name: Optional[str] = None) -> dict:
        """Create a compressed backup of a file"""
        if not source_file.exists():
            return {'status': 'error', 'message': f'Source file not found: {source_file}'}
        
        try:
            # Generate backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_name = backup_name or source_file.stem
            backup_file = self.backup_dir / f"{backup_name}_{timestamp}.gz"
            
            # Compress and save
            with open(source_file, 'rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Record metadata
            backup_entry = {
                'backup_id': backup_file.stem,
                'original_file': str(source_file),
                'backup_file': str(backup_file),
                'size': backup_file.stat().st_size,
                'timestamp': timestamp,
                'compressed': True
            }
            
            self.backups.append(backup_entry)
            self._save_metadata()
            
            return {'status': 'success', 'message': f'Backup created: {backup_file.name}', 'data': backup_entry}
        except Exception as e:
            return {'status': 'error', 'message': f'Backup failed: {str(e)}'}
    
    def restore_backup(self, backup_id: str, output_path: Path) -> dict:
        """Restore a file from backup"""
        backup_entry = None
        for entry in self.backups:
            if entry['backup_id'] == backup_id:
                backup_entry = entry
                break
        
        if not backup_entry:
            return {'status': 'error', 'message': f'Backup {backup_id} not found'}
        
        backup_file = Path(backup_entry['backup_file'])
        if not backup_file.exists():
            return {'status': 'error', 'message': f'Backup file not found: {backup_file}'}
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(backup_file, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            return {
                'status': 'success',
                'message': f'Restored from backup: {backup_file.name}',
                'data': {'backup_id': backup_id, 'restored_to': str(output_path)}
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Restore failed: {str(e)}'}
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        return self.backups
    
    def cleanup_old_backups(self) -> dict:
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            removed = 0
            
            for backup in list(self.backups):
                backup_time = datetime.strptime(backup['timestamp'], '%Y%m%d_%H%M%S')
                if backup_time < cutoff_date:
                    backup_file = Path(backup['backup_file'])
                    if backup_file.exists():
                        backup_file.unlink()
                    self.backups.remove(backup)
                    removed += 1
            
            self._save_metadata()
            
            return {'status': 'success', 'message': f'Cleaned up {removed} old backups', 'data': {'removed_count': removed}}
        except Exception as e:
            return {'status': 'error', 'message': f'Cleanup failed: {str(e)}'}
    
    def delete_backup(self, backup_id: str) -> dict:
        """Manually delete a specific backup"""
        for i, backup in enumerate(self.backups):
            if backup['backup_id'] == backup_id:
                backup_file = Path(backup['backup_file'])
                try:
                    if backup_file.exists():
                        backup_file.unlink()
                    self.backups.pop(i)
                    self._save_metadata()
                    return {'status': 'success', 'message': f'Backup {backup_id} deleted'}
                except Exception as e:
                    return {'status': 'error', 'message': f'Failed to delete backup: {str(e)}'}
        
        return {'status': 'error', 'message': f'Backup {backup_id} not found'}
    
    def get_backup_stats(self) -> Dict:
        """Get backup statistics"""
        total_size = sum(b.get('size', 0) for b in self.backups)
        
        return {
            'total_backups': len(self.backups),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'oldest_backup': self.backups[0]['timestamp'] if self.backups else None,
            'newest_backup': self.backups[-1]['timestamp'] if self.backups else None,
            'retention_days': self.retention_days
        }
