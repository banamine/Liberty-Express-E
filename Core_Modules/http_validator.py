"""
HTTP Validation Tier for Phase 2
Validates stream availability via HTTP HEAD request + Content-Type verification
"""

import requests
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HTTPValidationResult:
    """Result of HTTP validation"""
    url: str
    is_reachable: bool
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    is_valid_content_type: bool = False
    error_message: Optional[str] = None
    response_time_ms: float = 0.0


class HTTPValidator:
    """HTTP validation for stream availability"""
    
    # Valid content types for video streams
    VALID_CONTENT_TYPES = {
        # Video formats
        'video/mp4', 'video/x-msvideo', 'video/x-matroska',
        'video/quicktime', 'video/x-flv', 'video/webm',
        
        # Streaming formats
        'application/vnd.apple.mpegurl',  # HLS .m3u8
        'application/dash+xml',  # DASH .mpd
        'application/x-mpegURL',  # Alternative HLS
        
        # Generic
        'application/octet-stream',  # Raw stream
        'video/unknown',
    }
    
    def __init__(self, timeout_seconds: int = 5):
        """
        Initialize HTTP validator.
        
        Args:
            timeout_seconds: Timeout for HEAD request
        """
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'M3U-Matrix-Pro/1.0 (FFmpeg-compatible stream validator)'
        })
    
    def _is_valid_content_type(self, content_type: Optional[str]) -> bool:
        """Check if content type is valid for video/stream"""
        if not content_type:
            return True  # Allow unknown (many servers don't set this)
        
        content_type = content_type.lower().split(';')[0].strip()
        
        # Check exact matches
        if content_type in self.VALID_CONTENT_TYPES:
            return True
        
        # Check prefixes
        if any(content_type.startswith(valid) for valid in self.VALID_CONTENT_TYPES):
            return True
        
        return False
    
    def validate_http(self, url: str) -> HTTPValidationResult:
        """
        Validate stream via HTTP HEAD request.
        
        Args:
            url: Stream URL to validate
            
        Returns:
            HTTPValidationResult with reachability info
        """
        result = HTTPValidationResult(url=url, is_reachable=False)
        
        # Skip validation for local files
        if url.startswith('file://'):
            result.is_reachable = True
            result.error_message = "Local file (skipped HTTP check)"
            return result
        
        try:
            # Try HEAD request first (faster)
            try:
                response = self.session.head(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=False  # IPTV streams often have cert issues
                )
                
                result.http_status = response.status_code
                result.content_type = response.headers.get('Content-Type')
                result.response_time_ms = response.elapsed.total_seconds() * 1000
                
                # Check status code
                if response.status_code == 200:
                    result.is_reachable = True
                    result.is_valid_content_type = self._is_valid_content_type(result.content_type)
                    
                    if not result.is_valid_content_type:
                        result.error_message = f"Unexpected content type: {result.content_type}"
                    
                    logger.info(f"HTTP 200 OK: {url[:50]}... ({result.content_type})")
                    return result
                
                elif response.status_code in [301, 302, 303, 307, 308]:
                    # Redirected (should be followed by allow_redirects=True)
                    result.error_message = f"HTTP {response.status_code} Redirect"
                    result.is_reachable = True  # Server is responding
                    return result
                
                else:
                    result.error_message = f"HTTP {response.status_code}"
                    return result
            
            except requests.Timeout:
                # HEAD request timed out, try GET with stream (for some IPTV streams)
                try:
                    response = self.session.get(
                        url,
                        timeout=self.timeout,
                        stream=True,
                        allow_redirects=True,
                        verify=False
                    )
                    
                    result.http_status = response.status_code
                    result.content_type = response.headers.get('Content-Type')
                    result.response_time_ms = response.elapsed.total_seconds() * 1000
                    
                    if response.status_code == 200:
                        result.is_reachable = True
                        result.is_valid_content_type = self._is_valid_content_type(result.content_type)
                        logger.info(f"HTTP 200 OK (GET): {url[:50]}...")
                        return result
                    
                except:
                    pass
                
                result.error_message = "HTTP timeout"
                return result
        
        except requests.ConnectionError as e:
            result.error_message = f"Connection error: {str(e)[:40]}"
            logger.warning(f"Connection error for {url}: {e}")
            return result
        
        except requests.RequestException as e:
            result.error_message = f"Request error: {str(e)[:40]}"
            logger.warning(f"Request error for {url}: {e}")
            return result
        
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)[:40]}"
            logger.error(f"Unexpected error validating {url}: {e}")
            return result
    
    def __del__(self):
        """Cleanup session"""
        try:
            self.session.close()
        except:
            pass


def validate_http_quick(url: str, timeout_seconds: int = 5) -> HTTPValidationResult:
    """Quick HTTP validation wrapper"""
    validator = HTTPValidator(timeout_seconds=timeout_seconds)
    return validator.validate_http(url)
