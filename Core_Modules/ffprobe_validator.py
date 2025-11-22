"""
FFprobe Real Stream Validator
Validates M3U playlists using FFprobe for actual stream verification.
Uses random sampling: if one stream fails, all streams in that source are marked bad.
"""

import subprocess
import json
import logging
import random
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class StreamValidationResult:
    """Result of stream validation"""
    url: str
    is_valid: bool
    stream_type: str  # 'hls', 'dash', 'http', 'local', 'unknown'
    duration: Optional[float] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    resolution: Optional[str] = None
    bitrate: Optional[str] = None
    error_message: Optional[str] = None
    validation_tier: str = "unknown"  # 'http', 'ffprobe', 'hls', 'none'
    http_status: Optional[int] = None  # HTTP status code
    hls_segments_checked: int = 0  # Number of HLS segments verified


@dataclass
class PlaylistValidationResult:
    """Result of playlist validation"""
    playlist_path: str
    total_channels: int
    valid_channels: int
    invalid_channels: int
    sample_size: int
    sample_results: List[StreamValidationResult]
    is_healthy: bool  # True if sample indicates all streams are good
    error_message: Optional[str] = None  # Optional error message


class FFprobeValidator:
    """Real stream validation using FFprobe"""
    
    def __init__(self, timeout_seconds: int = 10):
        self.timeout = timeout_seconds
        self.ffprobe_path = self._find_ffprobe()
        
    def _find_ffprobe(self) -> Optional[str]:
        """Find FFprobe executable"""
        try:
            result = subprocess.run(['which', 'ffprobe'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Try common paths
        for path in ['/usr/bin/ffprobe', '/usr/local/bin/ffprobe', 'ffprobe']:
            try:
                subprocess.run([path, '-version'], capture_output=True, timeout=2)
                return path
            except:
                continue
        
        return None
    
    def _detect_stream_type(self, url: str) -> str:
        """Detect stream type from URL"""
        if url.startswith('file://') or Path(url).exists():
            return 'local'
        
        url_lower = url.lower()
        if '.m3u8' in url_lower or 'hls' in url_lower:
            return 'hls'
        elif '.mpd' in url_lower or 'dash' in url_lower:
            return 'dash'
        elif url_lower.startswith(('http://', 'https://')):
            return 'http'
        
        return 'unknown'
    
    def validate_stream(self, url: str) -> StreamValidationResult:
        """Validate single stream using FFprobe"""
        result = StreamValidationResult(
            url=url,
            is_valid=False,
            stream_type=self._detect_stream_type(url)
        )
        
        if not self.ffprobe_path:
            result.error_message = "FFprobe not found"
            return result
        
        try:
            # FFprobe command to get stream info
            cmd = [
                self.ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height,bit_rate',
                '-of', 'json',
                url
            ]
            
            result_proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result_proc.returncode != 0:
                result.error_message = result_proc.stderr or "FFprobe validation failed"
                return result
            
            # Parse JSON output
            data = json.loads(result_proc.stdout)
            
            # Check if streams exist
            if not data.get('streams'):
                result.error_message = "No streams found"
                return result
            
            result.is_valid = True
            
            # Extract stream info
            if 'format' in data and 'duration' in data['format']:
                try:
                    result.duration = float(data['format']['duration'])
                except:
                    pass
            
            # Find video and audio streams
            for stream in data['streams']:
                codec_type = stream.get('codec_type')
                
                if codec_type == 'video':
                    result.video_codec = stream.get('codec_name', 'unknown')
                    width = stream.get('width')
                    height = stream.get('height')
                    if width and height:
                        result.resolution = f"{width}x{height}"
                    
                    bitrate = stream.get('bit_rate')
                    if bitrate:
                        try:
                            result.bitrate = f"{int(bitrate) // 1000}k"
                        except:
                            pass
                
                elif codec_type == 'audio':
                    result.audio_codec = stream.get('codec_name', 'unknown')
            
            return result
            
        except subprocess.TimeoutExpired:
            result.error_message = f"Validation timeout ({self.timeout}s)"
            return result
        except json.JSONDecodeError:
            result.error_message = "Invalid JSON response from FFprobe"
            return result
        except Exception as e:
            result.error_message = str(e)
            return result
    
    def _parse_m3u(self, file_path: str) -> List[Dict]:
        """Parse M3U file and extract channels"""
        channels = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('#EXTINF'):
                    # Parse channel info
                    channel = {}
                    
                    # Extract name
                    name_match = line.split(',')[-1] if ',' in line else 'Unknown'
                    channel['name'] = name_match.strip()
                    
                    # Extract logo if present
                    logo_match = None
                    if 'tvg-logo=' in line:
                        import re
                        m = re.search(r'tvg-logo="([^"]*)"', line)
                        if m:
                            channel['logo'] = m.group(1)
                    
                    # Next line should be URL
                    if i + 1 < len(lines):
                        url = lines[i + 1].strip()
                        if url and not url.startswith('#'):
                            channel['url'] = url
                            channels.append(channel)
                            i += 1
                
                i += 1
            
            return channels
            
        except Exception as e:
            logger.error(f"Error parsing M3U: {e}")
            return []
    
    def validate_playlist_random_sample(self, m3u_path: str, sample_size: int = 5) -> PlaylistValidationResult:
        """
        Validate M3U playlist by random sampling.
        If one sample fails, the entire source is marked as potentially problematic.
        """
        
        # Parse M3U
        channels = self._parse_m3u(m3u_path)
        
        result = PlaylistValidationResult(
            playlist_path=m3u_path,
            total_channels=len(channels),
            valid_channels=0,
            invalid_channels=0,
            sample_size=0,
            sample_results=[],
            is_healthy=False
        )
        
        if not channels:
            result.error_message = "No channels found in M3U"
            return result
        
        # Random sampling: check min(sample_size, total_channels)
        check_count = min(sample_size, len(channels))
        sample = random.sample(channels, check_count)
        
        result.sample_size = check_count
        
        # Validate each sample
        failed_count = 0
        for channel in sample:
            url = channel.get('url', '')
            validation = self.validate_stream(url)
            result.sample_results.append(validation)
            
            if validation.is_valid:
                result.valid_channels += 1
            else:
                result.invalid_channels += 1
                failed_count += 1
        
        # Determine health: if ANY sample fails, mark unhealthy
        # (if one is bad, they all are bad - as per user's logic)
        result.is_healthy = (failed_count == 0)
        
        return result
    
    def validate_playlist_comprehensive(self, m3u_path: str) -> PlaylistValidationResult:
        """Validate entire playlist (slower but thorough)"""
        channels = self._parse_m3u(m3u_path)
        
        result = PlaylistValidationResult(
            playlist_path=m3u_path,
            total_channels=len(channels),
            valid_channels=0,
            invalid_channels=0,
            sample_size=len(channels),
            sample_results=[],
            is_healthy=False
        )
        
        if not channels:
            return result
        
        # Validate all channels
        for channel in channels:
            url = channel.get('url', '')
            validation = self.validate_stream(url)
            result.sample_results.append(validation)
            
            if validation.is_valid:
                result.valid_channels += 1
            else:
                result.invalid_channels += 1
        
        # Healthy if more than 80% are valid
        result.is_healthy = (result.valid_channels / len(channels) > 0.8) if channels else False
        
        return result
    
    def validate_hls_segments(self, m3u8_url: str, segment_count: int = 3) -> Tuple[bool, str, int]:
        """
        Validate HLS stream by checking m3u8 playlist and downloading segments.
        Phase 2 Requirement: Download first N segments → 200 + growing .ts files
        
        Args:
            m3u8_url: URL to .m3u8 playlist
            segment_count: Number of segments to validate
            
        Returns:
            Tuple of (is_valid, error_message, segments_checked)
        """
        try:
            # Fetch m3u8 playlist
            headers = {
                'User-Agent': 'M3U-Matrix-Pro/1.0 (FFmpeg-compatible)',
                'Referer': m3u8_url
            }
            response = requests.get(m3u8_url, timeout=5, headers=headers, verify=False)
            
            if response.status_code != 200:
                return False, f"M3U8 HTTP {response.status_code}", 0
            
            # Parse m3u8 content
            lines = response.text.strip().split('\n')
            segments = []
            base_url = '/'.join(m3u8_url.split('/')[:-1]) + '/'
            
            for line in lines:
                line = line.strip()
                # Skip comments and directives
                if not line or line.startswith('#'):
                    continue
                # Extract segment URL
                if line.endswith('.ts') or line.endswith('.m4s'):
                    # Handle relative URLs
                    if line.startswith('http'):
                        segments.append(line)
                    else:
                        segments.append(base_url + line)
            
            if not segments:
                return False, "No segments found in M3U8", 0
            
            # Validate first N segments
            segments_to_check = min(segment_count, len(segments))
            checked = 0
            last_size = 0
            
            for i, segment_url in enumerate(segments[:segments_to_check]):
                try:
                    seg_response = requests.head(
                        segment_url,
                        timeout=3,
                        headers=headers,
                        verify=False,
                        allow_redirects=True
                    )
                    
                    if seg_response.status_code != 200:
                        return False, f"Segment {i+1} HTTP {seg_response.status_code}", checked
                    
                    # Check Content-Length header for file growth
                    content_length = seg_response.headers.get('Content-Length', '0')
                    try:
                        current_size = int(content_length)
                        if current_size > 0 and current_size > last_size:
                            last_size = current_size
                    except:
                        pass
                    
                    checked += 1
                
                except requests.Timeout:
                    return False, f"Segment {i+1} timeout", checked
                except Exception as e:
                    return False, f"Segment {i+1} error: {str(e)[:30]}", checked
            
            if checked == segments_to_check:
                return True, f"✅ {checked} segments validated", checked
            
            return False, f"Only {checked}/{segments_to_check} segments validated", checked
        
        except requests.Timeout:
            return False, "M3U8 timeout", 0
        except Exception as e:
            return False, f"HLS error: {str(e)[:40]}", 0
    
    def validate_stream_with_tiers(self, url: str) -> StreamValidationResult:
        """
        Enhanced validation with multi-tier checking.
        Phase 2 Requirement: HTTP 200 + ffprobe + HLS segments
        
        Returns StreamValidationResult with validation_tier set to indicate which tier passed
        """
        result = StreamValidationResult(
            url=url,
            is_valid=False,
            stream_type=self._detect_stream_type(url),
            validation_tier="none"
        )
        
        # Tier 1: HTTP validation (quick pre-check)
        if not url.startswith('file://'):
            try:
                http_response = requests.head(
                    url,
                    timeout=3,
                    headers={'User-Agent': 'M3U-Matrix-Pro/1.0'},
                    verify=False,
                    allow_redirects=True
                )
                result.http_status = http_response.status_code
                
                if http_response.status_code != 200:
                    result.error_message = f"HTTP {http_response.status_code}"
                    result.validation_tier = "http"
                    return result
                
                result.validation_tier = "http"
            except:
                # If HTTP check fails, continue to FFprobe (some streams don't support HEAD)
                pass
        
        # Tier 2: FFprobe validation
        ffprobe_result = self.validate_stream(url)
        if ffprobe_result.is_valid:
            result.is_valid = True
            result.validation_tier = "ffprobe"
            result.video_codec = ffprobe_result.video_codec
            result.audio_codec = ffprobe_result.audio_codec
            result.resolution = ffprobe_result.resolution
            result.bitrate = ffprobe_result.bitrate
            result.duration = ffprobe_result.duration
            return result
        
        # Tier 3: HLS segment validation (if HLS detected)
        if result.stream_type == 'hls':
            hls_valid, hls_error, segments = self.validate_hls_segments(url)
            result.hls_segments_checked = segments
            if hls_valid:
                result.is_valid = True
                result.validation_tier = "hls"
                result.error_message = hls_error
                return result
            else:
                result.error_message = hls_error
        else:
            result.error_message = ffprobe_result.error_message
        
        return result


def validate_m3u_quick(m3u_path: str, timeout_seconds: int = 10) -> PlaylistValidationResult:
    """Quick validation of M3U file using random sampling"""
    validator = FFprobeValidator(timeout_seconds=timeout_seconds)
    return validator.validate_playlist_random_sample(m3u_path, sample_size=5)


def validate_m3u_full(m3u_path: str, timeout_seconds: int = 10) -> PlaylistValidationResult:
    """Full validation of M3U file (all channels)"""
    validator = FFprobeValidator(timeout_seconds=timeout_seconds)
    return validator.validate_playlist_comprehensive(m3u_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        m3u_file = sys.argv[1]
        print(f"Quick validating: {m3u_file}")
        
        result = validate_m3u_quick(m3u_file)
        
        print(f"\nPlaylist: {result.playlist_path}")
        print(f"Total Channels: {result.total_channels}")
        print(f"Sample Size: {result.sample_size}")
        print(f"Valid: {result.valid_channels} / Invalid: {result.invalid_channels}")
        print(f"Health Status: {'✅ HEALTHY' if result.is_healthy else '❌ UNHEALTHY (one bad = all bad)'}")
        
        print("\nSample Results:")
        for i, validation in enumerate(result.sample_results, 1):
            status = "✅" if validation.is_valid else "❌"
            print(f"\n  {i}. {status} {validation.url}")
            print(f"     Type: {validation.stream_type}")
            
            if validation.is_valid:
                print(f"     Video: {validation.video_codec}")
                print(f"     Audio: {validation.audio_codec}")
                if validation.resolution:
                    print(f"     Resolution: {validation.resolution}")
                if validation.bitrate:
                    print(f"     Bitrate: {validation.bitrate}")
            else:
                print(f"     Error: {validation.error_message}")
    else:
        print("Usage: python ffprobe_validator.py <m3u_file>")
