#!/usr/bin/env python3
"""
NDI Output Module for M3U Matrix Pro
Provides Network Device Interface (NDI) output capabilities for professional broadcast
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import logging

# Video processing libraries
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

class NDIOutputStream:
    """Manages NDI output stream for a single video source"""
    
    def __init__(self, source_name: str = "M3U Matrix Channel", 
                 resolution: Tuple[int, int] = (1920, 1080),
                 framerate: int = 30):
        """
        Initialize NDI output stream
        
        Args:
            source_name: Name that appears in NDI network
            resolution: Output resolution (width, height)
            framerate: Output framerate
        """
        self.source_name = source_name
        self.resolution = resolution
        self.framerate = framerate
        self.is_active = False
        self.output_thread = None
        
        # NDI settings
        self.ndi_groups = ""  # Empty for public
        self.ndi_clock_audio = True
        self.ndi_clock_video = True
        
        # Performance metrics
        self.frames_sent = 0
        self.start_time = None
        self.bandwidth_mbps = 0
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def start_vlc_ndi_output(self, input_url: str) -> bool:
        """
        Start VLC with NDI output plugin
        
        Args:
            input_url: Video source URL or file path
            
        Returns:
            True if started successfully
        """
        try:
            # Build VLC command with NDI output
            vlc_cmd = [
                "vlc",
                input_url,
                "--intf", "dummy",  # No interface
                "--no-video-title-show",
                "--no-audio",  # Mute local audio
                
                # NDI output configuration
                "--sout", f"#transcode{{vcodec=h264,vb=8000,scale=1,acodec=mp3,ab=128,channels=2,samplerate=44100}}:ndi{{ndi-name={self.source_name},ndi-groups={self.ndi_groups}}}",
                
                # Performance settings
                "--network-caching=1000",
                "--live-caching=300",
                "--file-caching=1000"
            ]
            
            # Start VLC process
            self.vlc_process = subprocess.Popen(
                vlc_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.is_active = True
            self.start_time = time.time()
            
            # Start monitoring thread
            self.output_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.output_thread.start()
            
            self.logger.info(f"NDI output started: {self.source_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start VLC NDI output: {e}")
            return False
    
    def start_opencv_ndi_output(self, video_capture) -> bool:
        """
        Start NDI output using OpenCV frame capture (for future NDI SDK integration)
        
        Args:
            video_capture: OpenCV VideoCapture object
            
        Returns:
            True if started successfully
        """
        if not CV2_AVAILABLE:
            self.logger.error("OpenCV not available for NDI output")
            return False
        
        try:
            self.is_active = True
            self.start_time = time.time()
            
            # Start frame sending thread
            self.output_thread = threading.Thread(
                target=self._send_frames_opencv,
                args=(video_capture,),
                daemon=True
            )
            self.output_thread.start()
            
            self.logger.info(f"NDI frame output started: {self.source_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start OpenCV NDI output: {e}")
            return False
    
    def _send_frames_opencv(self, video_capture):
        """Send frames via NDI (placeholder for NDI SDK implementation)"""
        while self.is_active:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # Resize frame if needed
            if frame.shape[:2][::-1] != self.resolution:
                frame = cv2.resize(frame, self.resolution)
            
            # TODO: Send frame via NDI SDK when available
            # For now, this is a placeholder showing the structure
            # ndi_send_video(self.ndi_sender, frame)
            
            self.frames_sent += 1
            
            # Calculate bandwidth
            frame_size_mb = (frame.nbytes / 1024 / 1024)
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.bandwidth_mbps = (self.frames_sent * frame_size_mb * 8) / elapsed
            
            # Frame rate limiting
            time.sleep(1.0 / self.framerate)
    
    def _monitor_output(self):
        """Monitor VLC process output"""
        if hasattr(self, 'vlc_process'):
            while self.is_active:
                if self.vlc_process.poll() is not None:
                    # Process ended
                    self.is_active = False
                    break
                time.sleep(1)
    
    def stop(self):
        """Stop NDI output"""
        self.is_active = False
        
        # Stop VLC process if running
        if hasattr(self, 'vlc_process'):
            try:
                self.vlc_process.terminate()
                self.vlc_process.wait(timeout=5)
            except:
                self.vlc_process.kill()
        
        # Wait for thread to finish
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=2)
        
        self.logger.info(f"NDI output stopped: {self.source_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current NDI stream status"""
        status = {
            "source_name": self.source_name,
            "is_active": self.is_active,
            "resolution": f"{self.resolution[0]}x{self.resolution[1]}",
            "framerate": self.framerate,
            "frames_sent": self.frames_sent,
            "bandwidth_mbps": round(self.bandwidth_mbps, 2)
        }
        
        if self.start_time:
            status["uptime_seconds"] = int(time.time() - self.start_time)
        
        return status


class NDIManager:
    """Manages multiple NDI output streams"""
    
    def __init__(self):
        """Initialize NDI Manager"""
        self.streams = {}  # source_name -> NDIOutputStream
        self.config = self.load_config()
        self.logger = logging.getLogger(__name__)
        
        # Check for NDI tools
        self.ndi_tools_path = self._find_ndi_tools()
        
    def _find_ndi_tools(self) -> Optional[Path]:
        """Find NDI tools installation"""
        possible_paths = [
            Path("C:/Program Files/NDI/NDI 6 Tools"),
            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/NDI 6 Tools"),
            Path("/usr/local/ndi"),
            Path.home() / "NDI"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.logger.info(f"Found NDI tools: {path}")
                return path
        
        return None
    
    def load_config(self) -> Dict[str, Any]:
        """Load NDI configuration"""
        config_file = Path("ndi_config.json")
        default_config = {
            "enabled": True,
            "default_resolution": [1920, 1080],
            "default_framerate": 30,
            "default_bitrate": 8000,
            "use_vlc_plugin": True,  # Use VLC NDI plugin vs SDK
            "auto_start": False,
            "channel_prefix": "M3U_",
            "max_streams": 8
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save NDI configuration"""
        config_file = Path("ndi_config.json")
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_stream(self, channel_name: str, source_url: str,
                     resolution: Optional[Tuple[int, int]] = None,
                     framerate: Optional[int] = None) -> bool:
        """
        Create a new NDI output stream
        
        Args:
            channel_name: Name for the NDI source
            source_url: Video source URL or file path
            resolution: Optional output resolution
            framerate: Optional output framerate
            
        Returns:
            True if stream created successfully
        """
        # Use defaults if not specified
        if resolution is None:
            resolution = tuple(self.config["default_resolution"])
        if framerate is None:
            framerate = self.config["default_framerate"]
        
        # Add prefix to channel name
        ndi_name = f"{self.config['channel_prefix']}{channel_name}"
        
        # Check max streams limit
        if len(self.streams) >= self.config["max_streams"]:
            self.logger.warning(f"Maximum NDI streams limit reached ({self.config['max_streams']})")
            return False
        
        # Create stream
        stream = NDIOutputStream(ndi_name, resolution, framerate)
        
        # Start output based on configuration
        if self.config["use_vlc_plugin"] and VLC_AVAILABLE:
            success = stream.start_vlc_ndi_output(source_url)
        elif CV2_AVAILABLE:
            # Try OpenCV method (for future NDI SDK)
            cap = cv2.VideoCapture(source_url)
            if cap.isOpened():
                success = stream.start_opencv_ndi_output(cap)
            else:
                success = False
        else:
            self.logger.error("No suitable NDI output method available")
            return False
        
        if success:
            self.streams[ndi_name] = stream
            self.logger.info(f"Created NDI stream: {ndi_name}")
            return True
        
        return False
    
    def stop_stream(self, stream_name: str) -> bool:
        """
        Stop an NDI output stream
        
        Args:
            stream_name: Name of the stream to stop
            
        Returns:
            True if stopped successfully
        """
        if stream_name in self.streams:
            self.streams[stream_name].stop()
            del self.streams[stream_name]
            self.logger.info(f"Stopped NDI stream: {stream_name}")
            return True
        
        return False
    
    def stop_all_streams(self):
        """Stop all active NDI streams"""
        for stream_name in list(self.streams.keys()):
            self.stop_stream(stream_name)
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get status of all NDI streams"""
        status_list = []
        for stream in self.streams.values():
            status_list.append(stream.get_status())
        return status_list
    
    def get_stream_count(self) -> int:
        """Get number of active streams"""
        return len(self.streams)
    
    def is_ndi_available(self) -> bool:
        """Check if NDI output is available"""
        return VLC_AVAILABLE or CV2_AVAILABLE


# Global NDI manager instance
_ndi_manager = None

def get_ndi_manager() -> NDIManager:
    """Get or create the global NDI manager instance"""
    global _ndi_manager
    if _ndi_manager is None:
        _ndi_manager = NDIManager()
    return _ndi_manager