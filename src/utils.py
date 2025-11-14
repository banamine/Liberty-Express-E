"""
M3U Matrix Pro - Utility Functions
Provides security, validation, and helper functions
"""

import re
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

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


def validate_url(url: str, allowed_schemes: List[str] = None) -> bool:
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


