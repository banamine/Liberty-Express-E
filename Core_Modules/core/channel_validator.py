"""
Channel Validator - Validates channel URLs and connectivity
"""

import socket
import logging
import requests
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
import threading


class ChannelValidator:
    """
    Validates channel URLs to check if they are working, broken, or timing out.
    Supports HTTP, HTTPS, RTMP, and RTSP protocols.
    """
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the channel validator.
        
        Args:
            timeout: Default timeout for connection attempts in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.results = {}
        self._cancel_flag = False
    
    def validate_channels(self, channels: List[Dict[str, Any]], 
                         progress_callback: Optional[callable] = None) -> Dict[str, int]:
        """
        Validate multiple channels and return results.
        
        Args:
            channels: List of channel dictionaries
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with counts of working, broken, and timeout channels
        """
        self.results = {
            "working": 0,
            "broken": 0,
            "timeout": 0,
            "total": len(channels)
        }
        
        self._cancel_flag = False
        
        for i, channel in enumerate(channels):
            if self._cancel_flag:
                self.logger.info("Channel validation cancelled")
                break
            
            status = self.validate_single_channel(channel)
            self.results[status] += 1
            
            # Update channel status
            channel['status'] = status
            channel['last_checked'] = datetime.now()
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, len(channels), channel, status, self.results)
            
            # Small delay to avoid overwhelming servers
            if i < len(channels) - 1:
                threading.Event().wait(0.1)
        
        return self.results
    
    def validate_single_channel(self, channel: Dict[str, Any]) -> str:
        """
        Validate a single channel's URL and metadata.
        
        Args:
            channel: Channel dictionary containing URL and metadata
            
        Returns:
            Status string: "working", "broken", or "timeout"
        """
        url = channel.get("url", "")
        
        if not url:
            return "broken"
        
        # Validate URL format
        if not self._is_valid_url_format(url):
            return "broken"
        
        # Determine validation method based on protocol
        if url.startswith(('http://', 'https://')):
            return self._validate_http_stream(url)
        elif url.startswith(('rtmp://', 'rtmps://')):
            return self._validate_rtmp_stream(url)
        elif url.startswith('rtsp://'):
            return self._validate_rtsp_stream(url)
        elif url.startswith('file://') or url.startswith('/'):
            return self._validate_local_file(url)
        else:
            self.logger.debug(f"Unsupported protocol for URL: {url}")
            return "broken"
    
    def _is_valid_url_format(self, url: str) -> bool:
        """
        Check if URL has valid format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid format
        """
        valid_prefixes = ('http://', 'https://', 'rtmp://', 'rtmps://', 'rtsp://', 'file://', '/')
        return url.startswith(valid_prefixes)
    
    def _validate_http_stream(self, url: str) -> str:
        """
        Validate HTTP/HTTPS stream URLs.
        
        Args:
            url: HTTP/HTTPS URL
            
        Returns:
            Status string
        """
        try:
            # Try GET with range request first (more reliable than HEAD)
            try:
                response = requests.get(
                    url, 
                    timeout=self.timeout,
                    allow_redirects=True,
                    headers={'Range': 'bytes=0-1024'},
                    stream=True
                )
                
                # Accept various success codes
                if response.status_code in (200, 206, 403):
                    return "working"
                else:
                    self.logger.debug(f"HTTP stream returned status {response.status_code}: {url}")
                    return "broken"
                    
            except requests.exceptions.RequestException:
                # Fallback to HEAD request
                try:
                    response = requests.head(
                        url,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    if response.status_code in (200, 403):
                        return "working"
                    else:
                        return "broken"
                        
                except:
                    return "broken"
                    
        except requests.exceptions.Timeout:
            self.logger.debug(f"HTTP stream timeout: {url}")
            return "timeout"
        except Exception as e:
            self.logger.debug(f"HTTP stream validation error for {url}: {e}")
            return "broken"
    
    def _validate_rtmp_stream(self, url: str) -> str:
        """
        Validate RTMP/RTMPS stream URLs.
        
        Args:
            url: RTMP/RTMPS URL
            
        Returns:
            Status string
        """
        try:
            parsed = urlparse(url)
            protocol = parsed.scheme.lower()
            hostname = parsed.hostname
            
            if not hostname:
                return "broken"
            
            # Default port for RTMP
            default_port = 1935 if protocol in ('rtmp', 'rtmps') else 1935
            port = parsed.port or default_port
            
            # Try socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            try:
                # Attempt connection
                sock.connect((hostname, port))
                
                # For RTMP, connection success is usually enough
                # Full RTMP handshake is complex and not necessary for basic validation
                sock.close()
                return "working"
                
            except socket.timeout:
                return "timeout"
            except (socket.error, OSError):
                return "broken"
            finally:
                try:
                    sock.close()
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"RTMP validation failed for {url}: {e}")
            return "broken"
    
    def _validate_rtsp_stream(self, url: str) -> str:
        """
        Validate RTSP stream URLs with OPTIONS request.
        
        Args:
            url: RTSP URL
            
        Returns:
            Status string
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            if not hostname:
                return "broken"
            
            # Default port for RTSP
            port = parsed.port or 554
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            try:
                # Connect to RTSP server
                sock.connect((hostname, port))
                
                # Send OPTIONS request
                options_request = f"OPTIONS {url} RTSP/1.0\r\nCSeq: 1\r\n\r\n"
                sock.sendall(options_request.encode('utf-8'))
                
                # Try to receive response
                sock.settimeout(2)
                try:
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Check for valid RTSP response
                    if 'RTSP/1.0' in response or 'RTSP/2.0' in response:
                        sock.close()
                        return "working"
                        
                except socket.timeout:
                    # No response but connection worked - likely valid
                    sock.close()
                    return "working"
                    
            except socket.timeout:
                return "timeout"
            except (socket.error, OSError):
                return "broken"
            finally:
                try:
                    sock.close()
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"RTSP validation failed for {url}: {e}")
            return "broken"
    
    def _validate_local_file(self, url: str) -> str:
        """
        Validate local file paths.
        
        Args:
            url: Local file path or file:// URL
            
        Returns:
            Status string
        """
        try:
            from pathlib import Path
            
            # Handle file:// URLs
            if url.startswith('file://'):
                path = url[7:]  # Remove 'file://' prefix
            else:
                path = url
            
            # Check if file exists
            if Path(path).exists():
                return "working"
            else:
                return "broken"
                
        except Exception as e:
            self.logger.debug(f"Local file validation failed for {url}: {e}")
            return "broken"
    
    def cancel_validation(self) -> None:
        """Cancel ongoing validation process"""
        self._cancel_flag = True
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics.
        
        Returns:
            Dictionary with validation statistics
        """
        total = self.results.get('total', 0)
        working = self.results.get('working', 0)
        
        return {
            'total': total,
            'working': working,
            'broken': self.results.get('broken', 0),
            'timeout': self.results.get('timeout', 0),
            'success_rate': (working / total * 100) if total > 0 else 0
        }
    
    def validate_batch_async(self, channels: List[Dict[str, Any]], 
                            batch_size: int = 10,
                            callback: Optional[callable] = None) -> None:
        """
        Validate channels in batches asynchronously.
        
        Args:
            channels: List of channels to validate
            batch_size: Number of channels to validate simultaneously
            callback: Callback function for completion
        """
        import concurrent.futures
        
        def validate_batch(batch):
            results = []
            for channel in batch:
                status = self.validate_single_channel(channel)
                channel['status'] = status
                channel['last_checked'] = datetime.now()
                results.append((channel, status))
            return results
        
        # Split channels into batches
        batches = [channels[i:i+batch_size] for i in range(0, len(channels), batch_size)]
        
        # Process batches
        all_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(validate_batch, batch) for batch in batches]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                except Exception as e:
                    self.logger.error(f"Batch validation failed: {e}")
        
        # Update results
        self.results = {
            "working": sum(1 for _, status in all_results if status == "working"),
            "broken": sum(1 for _, status in all_results if status == "broken"),
            "timeout": sum(1 for _, status in all_results if status == "timeout"),
            "total": len(channels)
        }
        
        # Call callback if provided
        if callback:
            callback(self.results)