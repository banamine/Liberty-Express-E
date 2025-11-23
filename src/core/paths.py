"""
Cross-Platform Path Handling for ScheduleFlow

Ensures consistent path handling across Windows, macOS, and Linux.
"""

import os
import sys
from pathlib import Path, PureWindowsPath, PurePosixPath
from typing import Union


class CrossPlatformPath:
    """Handles paths consistently across all platforms"""
    
    @staticmethod
    def get_home_dir() -> Path:
        """Get user home directory (cross-platform)"""
        return Path.home()
    
    @staticmethod
    def get_app_data_dir(app_name: str = 'ScheduleFlow') -> Path:
        """Get platform-specific app data directory"""
        if sys.platform == 'win32':
            base = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif sys.platform == 'darwin':  # macOS
            base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux and others
            base = Path.home() / '.local' / 'share'
        
        app_dir = base / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    @staticmethod
    def get_cache_dir(app_name: str = 'ScheduleFlow') -> Path:
        """Get platform-specific cache directory"""
        if sys.platform == 'win32':
            base = Path(os.getenv('TEMP', Path.home() / 'AppData' / 'Local' / 'Temp'))
        elif sys.platform == 'darwin':  # macOS
            base = Path.home() / 'Library' / 'Caches'
        else:  # Linux and others
            base = Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))
        
        cache_dir = base / app_name
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def get_temp_dir(app_name: str = 'ScheduleFlow') -> Path:
        """Get platform-specific temporary directory"""
        import tempfile
        base = Path(tempfile.gettempdir())
        temp_dir = base / app_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize path for current platform"""
        p = Path(path)
        return p.resolve()
    
    @staticmethod
    def to_string(path: Path, use_forward_slash: bool = False) -> str:
        """Convert path to string with optional forward slash normalization"""
        s = str(path)
        if use_forward_slash and sys.platform == 'win32':
            s = s.replace('\\', '/')
        return s
    
    @staticmethod
    def is_absolute(path: Union[str, Path]) -> bool:
        """Check if path is absolute"""
        return Path(path).is_absolute()
    
    @staticmethod
    def join_path(*parts: Union[str, Path]) -> Path:
        """Join multiple path components"""
        result = Path(parts[0])
        for part in parts[1:]:
            result = result / part
        return result
    
    @staticmethod
    def ensure_exists(path: Union[str, Path], is_file: bool = False) -> Path:
        """Ensure path exists (create if needed)"""
        p = Path(path)
        if is_file:
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            p.mkdir(parents=True, exist_ok=True)
        return p
    
    @staticmethod
    def get_relative_path(path: Union[str, Path], 
                         relative_to: Union[str, Path]) -> Path:
        """Get relative path from one path to another"""
        try:
            return Path(path).relative_to(relative_to)
        except ValueError:
            return Path(path)
    
    @staticmethod
    def is_safe_path(path: Union[str, Path], base_dir: Union[str, Path]) -> bool:
        """Check if path is within base_dir (prevents directory traversal)"""
        try:
            Path(path).relative_to(base_dir)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_platform_info() -> dict:
        """Get platform information"""
        return {
            'system': sys.platform,
            'separator': os.sep,
            'path_separator': os.pathsep,
            'home_dir': str(Path.home()),
            'cwd': str(Path.cwd())
        }


# Convenience functions
def get_app_data_dir(app_name: str = 'ScheduleFlow') -> Path:
    """Get app data directory"""
    return CrossPlatformPath.get_app_data_dir(app_name)


def get_cache_dir(app_name: str = 'ScheduleFlow') -> Path:
    """Get cache directory"""
    return CrossPlatformPath.get_cache_dir(app_name)


def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize path"""
    return CrossPlatformPath.normalize_path(path)


def safe_join(*parts: Union[str, Path]) -> Path:
    """Safely join path components"""
    return CrossPlatformPath.join_path(*parts)
