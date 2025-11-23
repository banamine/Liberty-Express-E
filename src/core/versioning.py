"""
File Versioning System for ScheduleFlow

Tracks M3U file changes, maintains version history, supports rollback.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from .models import ValidationResult


class FileVersion:
    """Represents a single file version"""
    
    def __init__(self, version_id: str, file_path: str, content_hash: str,
                 timestamp: str, checksum: str, message: str = ""):
        self.version_id = version_id
        self.file_path = file_path
        self.content_hash = content_hash
        self.timestamp = timestamp
        self.checksum = checksum
        self.message = message
    
    def to_dict(self) -> Dict:
        return {
            'version_id': self.version_id,
            'file_path': self.file_path,
            'content_hash': self.content_hash,
            'timestamp': self.timestamp,
            'checksum': self.checksum,
            'message': self.message
        }


class VersionManager:
    """Manages file versioning, diffs, and rollback"""
    
    def __init__(self, versions_dir: Path):
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.versions_dir / 'versions.json'
        self.versions: List[FileVersion] = self._load_metadata()
    
    def _load_metadata(self) -> List[FileVersion]:
        """Load version metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    return [FileVersion(**v) for v in data]
            except Exception:
                return []
        return []
    
    def _save_metadata(self):
        """Save version metadata to disk"""
        data = [v.to_dict() for v in self.versions]
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_version(self, file_path: str, content: str, 
                      message: str = "") -> FileVersion:
        """Create a new version of a file"""
        content_hash = self._compute_hash(content)
        
        # Check if content hasn't changed
        if self.versions and self.versions[-1].content_hash == content_hash:
            return self.versions[-1]
        
        # Create new version
        version_id = f"v{len(self.versions) + 1}"
        timestamp = datetime.utcnow().isoformat()
        checksum = content_hash[:8]
        
        # Store version content
        version_file = self.versions_dir / f"{version_id}_{checksum}.m3u"
        with open(version_file, 'w') as f:
            f.write(content)
        
        # Create metadata entry
        version = FileVersion(
            version_id=version_id,
            file_path=file_path,
            content_hash=content_hash,
            timestamp=timestamp,
            checksum=checksum,
            message=message
        )
        
        self.versions.append(version)
        self._save_metadata()
        
        return version
    
    def get_version(self, version_id: str) -> Optional[FileVersion]:
        """Get version metadata by ID"""
        for v in self.versions:
            if v.version_id == version_id:
                return v
        return None
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """Get full content of a specific version"""
        version = self.get_version(version_id)
        if not version:
            return None
        
        version_file = self.versions_dir / f"{version_id}_{version.checksum}.m3u"
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read()
        return None
    
    def list_versions(self) -> List[Dict]:
        """List all versions with metadata"""
        return [v.to_dict() for v in self.versions]
    
    def get_diff(self, version_id1: str, version_id2: str) -> Dict:
        """Get differences between two versions"""
        content1 = self.get_version_content(version_id1)
        content2 = self.get_version_content(version_id2)
        
        if not content1 or not content2:
            return {'status': 'error', 'message': 'Version not found'}
        
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        return {
            'status': 'success',
            'version1': version_id1,
            'version2': version_id2,
            'added_lines': len(set(lines2) - set(lines1)),
            'removed_lines': len(set(lines1) - set(lines2)),
            'modified_lines': len(set(lines1) & set(lines2))
        }
    
    def restore_version(self, version_id: str, output_path: Path) -> dict:
        """Restore a specific version to a file"""
        content = self.get_version_content(version_id)
        
        if not content:
            return {'status': 'error', 'message': f'Version {version_id} not found'}
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(content)
            
            return {
                'status': 'success',
                'message': f'Version {version_id} restored to {output_path}',
                'data': {'version_id': version_id, 'file_path': str(output_path)}
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to restore version: {str(e)}'}
    
    def cleanup_old_versions(self, keep_count: int = 10):
        """Remove old versions, keeping only the N most recent"""
        if len(self.versions) > keep_count:
            old_versions = self.versions[:-keep_count]
            for version in old_versions:
                version_file = self.versions_dir / f"{version.version_id}_{version.checksum}.m3u"
                if version_file.exists():
                    version_file.unlink()
            
            self.versions = self.versions[-keep_count:]
            self._save_metadata()
