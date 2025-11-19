"""
Helper functions and utilities
"""

import re
import os
import sys
import logging
import requests
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Tuple, Any, Dict
from datetime import datetime
import tkinter as tk
from tkinter import ttk


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Remove dangerous characters from filename.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Sanitized filename
    """
    # Remove dangerous characters
    clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(clean) > max_length:
        # Keep extension if present
        ext_pos = clean.rfind('.')
        if ext_pos > 0 and ext_pos > max_length - 10:
            ext = clean[ext_pos:]
            clean = clean[:max_length - len(ext)] + ext
        else:
            clean = clean[:max_length]
    
    return clean


def validate_url(url: str) -> bool:
    """
    Basic URL validation.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL
    """
    if not url:
        return False
    
    valid_schemes = ('http://', 'https://', 'rtmp://', 'rtmps://', 'rtsp://', 'file://')
    
    # Check if URL starts with a valid scheme
    if not url.startswith(valid_schemes):
        return False
    
    # Basic format check - should have something after the scheme
    for scheme in valid_schemes:
        if url.startswith(scheme):
            if len(url) <= len(scheme):
                return False
            break
    
    return True


def validate_file_path(file_path: str, base_dir: Optional[str] = None) -> bool:
    """
    Basic path validation with optional base directory check.
    
    Args:
        file_path: Path to validate
        base_dir: Optional base directory for relative path check
        
    Returns:
        True if valid path
    """
    try:
        path = Path(file_path)
        
        # Check if absolute path exists
        if path.is_absolute():
            return path.exists()
        
        # For relative paths, check against base_dir if provided
        if base_dir:
            full_path = Path(base_dir) / path
            return full_path.exists()
        
        return True
        
    except Exception:
        return False


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters except newline, return, tab
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Remove potential script tags
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def is_valid_m3u(content: str) -> bool:
    """
    Check if content is valid M3U format.
    
    Args:
        content: Content to check
        
    Returns:
        True if valid M3U format
    """
    if not content:
        return False
    
    # Check for M3U markers
    return '#EXTM3U' in content or '#EXTINF' in content


def download_and_cache_thumbnail(url: str, channel_name: str, 
                                cache_dir: Path, timeout: int = 5) -> Tuple[Optional[str], str]:
    """
    Download and cache a thumbnail image.
    
    Args:
        url: Thumbnail URL
        channel_name: Channel name for filename
        cache_dir: Directory to cache thumbnails
        timeout: Download timeout in seconds
        
    Returns:
        Tuple of (cached_path, status)
    """
    logger = logging.getLogger(__name__)
    
    if not url:
        return None, "no_url"
    
    try:
        # Create cache directory
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate cache filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        safe_name = sanitize_filename(channel_name)[:50]
        
        # Try to determine extension from URL
        ext = '.jpg'
        for image_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            if url.lower().endswith(image_ext):
                ext = image_ext
                break
        
        cache_filename = f"{safe_name}_{url_hash}{ext}"
        cache_path = cache_dir / cache_filename
        
        # Check if already cached
        if cache_path.exists():
            return str(cache_path), "cached"
        
        # Download thumbnail
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Save to cache
        with open(cache_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.debug(f"Cached thumbnail for {channel_name}: {cache_filename}")
        return str(cache_path), "downloaded"
        
    except Exception as e:
        logger.debug(f"Failed to cache thumbnail for {channel_name}: {e}")
        return None, "error"


def get_cached_thumbnail_stats(cache_dir: Path) -> Dict[str, Any]:
    """
    Get statistics about cached thumbnails.
    
    Args:
        cache_dir: Thumbnail cache directory
        
    Returns:
        Dictionary with cache statistics
    """
    try:
        cache_dir = Path(cache_dir)
        
        if not cache_dir.exists():
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_mb': 0.0
            }
        
        files = list(cache_dir.glob('*'))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }
        
    except Exception:
        return {
            'total_files': 0,
            'total_size': 0,
            'total_size_mb': 0.0
        }


class SimpleCache:
    """Simple LRU cache implementation"""
    
    def __init__(self, max_size: int = 200):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key: str) -> Any:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Update existing and move to end
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


def get_file_size(file_path: str) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        Human-readable size string
    """
    try:
        size_bytes = os.path.getsize(file_path)
        
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    except:
        return "Unknown"


def create_progress_dialog(root: tk.Tk, title: str, max_value: int) -> Tuple[tk.Toplevel, tk.IntVar, tk.Label, Dict]:
    """
    Create a progress dialog with cancel button.
    
    Args:
        root: Parent window
        title: Dialog title
        max_value: Maximum progress value
        
    Returns:
        Tuple of (dialog, progress_var, status_label, cancel_flag)
    """
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.configure(bg="#1e1e1e")
    dialog.transient(root)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Title label
    tk.Label(dialog, text=title, font=("Arial", 12, "bold"),
             bg="#1e1e1e", fg="white").pack(pady=10)
    
    # Progress bar
    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(dialog, variable=progress_var,
                                   maximum=max_value, length=350)
    progress_bar.pack(pady=10, padx=25)
    
    # Status label
    status_label = tk.Label(dialog, text="Starting...",
                           bg="#1e1e1e", fg="#aaa")
    status_label.pack(pady=5)
    
    # Cancel flag
    cancel_flag = {"cancelled": False}
    
    # Cancel button
    def cancel():
        cancel_flag["cancelled"] = True
        dialog.destroy()
    
    tk.Button(dialog, text="Cancel", command=cancel,
              bg="#e74c3c", fg="white", width=10).pack(pady=10)
    
    # Prevent closing with X button
    dialog.protocol("WM_DELETE_WINDOW", cancel)
    
    return dialog, progress_var, status_label, cancel_flag


def open_folder_in_explorer(folder_path: str) -> bool:
    """
    Open folder in system file explorer.
    
    Args:
        folder_path: Path to folder
        
    Returns:
        True if successful
    """
    try:
        folder = os.path.abspath(folder_path)
        
        if sys.platform == 'win32':
            os.startfile(folder)
        elif sys.platform == 'darwin':
            os.system(f'open "{folder}"')
        else:
            os.system(f'xdg-open "{folder}"')
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to open folder {folder_path}: {e}")
        return False


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {directory}: {e}")
        return False


def copy_file_with_backup(src: str, dst: str, max_backups: int = 5) -> bool:
    """
    Copy file with automatic backup of destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        max_backups: Maximum number of backups to keep
        
    Returns:
        True if successful
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        # Create backup if destination exists
        if dst_path.exists():
            backup_dir = dst_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{dst_path.stem}_backup_{timestamp}{dst_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(dst_path, backup_path)
            
            # Clean old backups
            backups = sorted(backup_dir.glob(f"{dst_path.stem}_backup_*"))
            if len(backups) > max_backups:
                for old_backup in backups[:-max_backups]:
                    old_backup.unlink()
        
        # Copy file
        shutil.copy2(src_path, dst_path)
        return True
        
    except Exception as e:
        logging.error(f"Failed to copy file from {src} to {dst}: {e}")
        return False