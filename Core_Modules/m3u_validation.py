"""
M3U Matrix Pro - Utility Functions
Provides security, validation, and helper functions
"""

import re
import os
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any, Tuple
import logging
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

# Optional imports for thumbnail caching
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not installed - thumbnail caching will be disabled")

# ===== SECURITY & VALIDATION =====

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters
    
    Args:
        filename: Original filename
        max_length: Maximum allowed length
        
    Returns:
        Safe filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    # Ensure not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate URL for security
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: http, https)
        
    Returns:
        True if URL is valid and safe
    """
    if not url or not isinstance(url, str):
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in allowed_schemes:
            logger.warning(f"Invalid URL scheme: {parsed.scheme}")
            return False
        
        # Check for localhost/private IPs (optional security measure)
        hostname = parsed.hostname
        if hostname:
            hostname_lower = hostname.lower()
            # Block localhost and private IPs
            if hostname_lower in ['localhost', '127.0.0.1', '0.0.0.0']:
                logger.warning(f"Blocked localhost URL: {url}")
                return False
            
            # Block private IP ranges (optional - uncomment if needed)
            # if hostname.startswith(('192.168.', '10.', '172.')):
            #     return False
        
        return True
        
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False


def validate_file_path(file_path: str, base_dir: Optional[Path] = None) -> bool:
    """
    Validate file path to prevent path traversal attacks
    
    Args:
        file_path: Path to validate
        base_dir: Base directory to constrain to
        
    Returns:
        True if path is safe
    """
    try:
        path = Path(file_path).resolve()
        
        # Check if path exists
        if not path.exists():
            return False
        
        # If base_dir provided, ensure path is within it
        if base_dir:
            base_dir = Path(base_dir).resolve()
            try:
                path.relative_to(base_dir)
            except ValueError:
                logger.warning(f"Path {path} is outside base directory {base_dir}")
                return False
        
        # Check for suspicious patterns
        if '..' in str(file_path):
            logger.warning(f"Suspicious path pattern: {file_path}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newline and tab
    text = ''.join(char for char in text if char >= ' ' or char in '\n\t')
    
    return text.strip()


# ===== PERFORMANCE HELPERS =====

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks for batch processing
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get_nested(data: Dict, keys: List[str], default=None) -> Any:
    """
    Safely get nested dictionary values
    
    Args:
        data: Dictionary
        keys: List of keys to traverse
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


# ===== CACHING HELPERS =====

class SimpleCache:
    """Simple in-memory cache with size limit"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            # Update access order (LRU)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        if key in self.cache:
            self.access_order.remove(key)
        
        self.cache[key] = value
        self.access_order.append(key)
        
        # Remove oldest if over limit
        while len(self.cache) > self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()


# ===== FORMAT VALIDATORS =====

def is_valid_m3u(content: str) -> bool:
    """Check if content looks like valid M3U format"""
    if not content:
        return False
    
    lines = content.strip().split('\n')
    if not lines:
        return False
    
    # Should start with #EXTM3U
    if not lines[0].strip().upper().startswith('#EXTM3U'):
        return False
    
    return True


def extract_safe_text(text: str, max_length: int = 500) -> str:
    """Extract text safely for display"""
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '[URL]', text)
    
    # Remove special chars
    text = re.sub(r'[^\w\s\-.,!?]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


# ===== THUMBNAIL CACHING =====

def download_and_cache_thumbnail(logo_url: str, channel_name: str, thumbnails_dir: Path, timeout: int = 10) -> Tuple[Optional[str], str]:
    """
    Download and cache channel logo/thumbnail
    
    Args:
        logo_url: URL of the logo to download
        channel_name: Name of the channel (for fallback filename)
        thumbnails_dir: Directory to save thumbnails
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (local_file_path, status_message)
        local_file_path is None if download failed
    """
    if not PILLOW_AVAILABLE:
        return None, "Pillow not installed"
    
    if not logo_url or not logo_url.startswith(('http://', 'https://')):
        return None, "Invalid URL"
    
    try:
        # Create hash of URL for unique filename
        url_hash = hashlib.md5(logo_url.encode()).hexdigest()[:12]
        
        # Sanitize channel name for filename
        safe_name = sanitize_filename(channel_name, max_length=50)
        safe_name = re.sub(r'[^\w\-]', '_', safe_name)
        
        # Determine file extension from URL
        ext = '.jpg'
        if logo_url.lower().endswith(('.png', '.gif', '.webp', '.jpeg', '.jpg')):
            ext = os.path.splitext(logo_url.lower())[1]
        
        # Create filename: channelname_hash.ext
        filename = f"{safe_name}_{url_hash}{ext}"
        local_path = thumbnails_dir / filename
        
        # Check if already cached
        if local_path.exists():
            return str(local_path), "Cached"
        
        # Download thumbnail
        response = requests.get(logo_url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Verify it's an image (only if Pillow available)
        try:
            if not PILLOW_AVAILABLE:
                # Skip image verification if Pillow not available
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return str(local_path), "Downloaded (unverified)"
            
            if Image is None:  # type: ignore
                raise ImportError("Pillow Image module not available")
            
            img = Image.open(BytesIO(response.content))  # type: ignore
            img.verify()
            
            # Save to disk
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return str(local_path), "Downloaded"
            
        except Exception as img_error:
            logger.warning(f"Invalid image from {logo_url}: {img_error}")
            return None, "Invalid image"
    
    except requests.Timeout:
        logger.warning(f"Timeout downloading thumbnail: {logo_url}")
        return None, "Timeout"
    
    except requests.RequestException as e:
        logger.warning(f"Failed to download thumbnail {logo_url}: {e}")
        return None, f"Download failed: {str(e)[:50]}"
    
    except Exception as e:
        logger.error(f"Unexpected error caching thumbnail: {e}")
        return None, f"Error: {str(e)[:50]}"


def get_cached_thumbnail_stats(thumbnails_dir: Path) -> Dict[str, Any]:
    """
    Get statistics about cached thumbnails
    
    Args:
        thumbnails_dir: Directory containing cached thumbnails
        
    Returns:
        Dictionary with stats (count, total_size_mb, oldest, newest)
    """
    if not thumbnails_dir.exists():
        return {
            'count': 0,
            'total_size_mb': 0,
            'oldest': None,
            'newest': None
        }
    
    files = list(thumbnails_dir.glob('*'))
    image_files = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']]
    
    if not image_files:
        return {
            'count': 0,
            'total_size_mb': 0,
            'oldest': None,
            'newest': None
        }
    
    total_size = sum(f.stat().st_size for f in image_files)
    mtimes = [f.stat().st_mtime for f in image_files]
    
    return {
        'count': len(image_files),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'oldest': min(mtimes) if mtimes else None,
        'newest': max(mtimes) if mtimes else None
    }


