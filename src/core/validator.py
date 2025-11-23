"""
Channel validation for ScheduleFlow

Extracted from M3U_MATRIX_PRO.py validation methods.
"""

import requests
import logging
from typing import Optional
from datetime import datetime
import asyncio

from .models import Channel, ValidationResult

logger = logging.getLogger(__name__)


class ChannelValidator:
    """Validates channel URLs and their accessibility"""
    
    def __init__(self, timeout: int = 5):
        """
        Initialize validator.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.logger = logger
    
    def validate_channel(self, channel: Channel) -> ValidationResult:
        """
        Validate a single channel URL.
        
        Args:
            channel: Channel to validate
        
        Returns:
            ValidationResult with status and details
        """
        if not channel.url:
            return ValidationResult(
                channel_uuid=channel.uuid,
                channel_name=channel.name,
                status="broken",
                error_message="No URL provided"
            )
        
        try:
            response = requests.head(
                channel.url,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True
            )
            
            # Accept 200, 206 (partial content), 403 (exists but restricted)
            if response.status_code in (200, 206, 403):
                status = "working"
            else:
                status = "broken"
            
            return ValidationResult(
                channel_uuid=channel.uuid,
                channel_name=channel.name,
                status=status,
                status_code=response.status_code,
                response_time_ms=response.elapsed.total_seconds() * 1000
            )
        except requests.exceptions.Timeout:
            return ValidationResult(
                channel_uuid=channel.uuid,
                channel_name=channel.name,
                status="timeout",
                error_message="Request timeout"
            )
        except requests.exceptions.ConnectionError as e:
            return ValidationResult(
                channel_uuid=channel.uuid,
                channel_name=channel.name,
                status="broken",
                error_message=f"Connection error: {str(e)}"
            )
        except Exception as e:
            return ValidationResult(
                channel_uuid=channel.uuid,
                channel_name=channel.name,
                status="broken",
                error_message=str(e)
            )
    
    def validate_channels_batch(
        self,
        channels: list,
        progress_callback: Optional[callable] = None
    ) -> list:
        """
        Validate multiple channels.
        
        Args:
            channels: List of Channel objects
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of ValidationResult objects
        """
        results = []
        for i, channel in enumerate(channels):
            result = self.validate_channel(channel)
            results.append(result)
            
            if progress_callback:
                progress_callback({
                    'current': i + 1,
                    'total': len(channels),
                    'channel': channel.name,
                    'status': result.status
                })
        
        return results
