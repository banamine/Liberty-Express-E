#!/usr/bin/env python3
"""
NEXUS TV Page Generator
Generates individual NEXUS TV channel pages from M3U playlists
With FFmpeg timestamp extraction support for accurate show timing
"""

import re
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import unquote, urlparse


def clean_title(raw_title):
    """
    Clean up titles from URL-encoded filenames or full URLs
    Examples:
      - "Hogan%27s%20Heroes_S03E10.mp4" → "Hogan's Heroes S03E10"
      - "https://archive.org/.../movie.mp4" → "movie"
      - "My_Movie_2024.mkv" → "My Movie 2024"
    """
    if not raw_title:
        return 'Unknown'
    
    # URL decode first (convert %27 → ', %20 → space, etc.)
    title = unquote(raw_title)
    
    # If it's a full URL, extract just the filename
    if title.startswith('http://') or title.startswith('https://'):
        parsed = urlparse(title)
        title = Path(parsed.path).name
    
    # Remove common video file extensions
    for ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m3u8', '.ts']:
        if title.lower().endswith(ext):
            title = title[:-len(ext)]
            break
    
    # Replace underscores with spaces
    title = title.replace('_', ' ')
    
    # Clean up multiple spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title if title else 'Unknown'


def sanitize_directory_name(name):
    """
    Sanitize a string to be safe for directory names on all OS platforms
    - URL decodes first (%20 → space, %27 → apostrophe)
    - Removes or replaces invalid characters
    - Ensures Windows compatibility
    - Blocks Windows reserved device names
    """
    if not name:
        return 'unknown'
    
    # URL decode first to handle %20, %27, etc.
    name = unquote(str(name))
    
    # Replace problematic characters that are invalid in Windows paths
    # Windows disallows: < > : " | ? * \ / and control chars 0-31
    # Also replace % to avoid issues with partially encoded strings
    invalid_chars = '<>:"|?*\\/\0%'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Remove control characters
    name = ''.join(char for char in name if ord(char) >= 32)
    
    # Replace multiple spaces/underscores with single underscore
    name = re.sub(r'[\s_]+', '_', name)
    
    # Remove leading/trailing underscores and dots (Windows limitation)
    name = name.strip('_.').strip()
    
    # Limit length to 255 chars (filesystem limit)
    if len(name) > 255:
        name = name[:255]
    
    # Check for Windows reserved device names
    # These names are reserved in Windows and cannot be used as filenames
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    # Check if the name (without extension) matches a reserved name
    name_upper = name.upper().split('.')[0]
    if name_upper in reserved_names:
        name = f"_{name}"  # Prefix with underscore to make it valid
    
    # If empty after cleaning, use fallback
    if not name:
        name = 'unknown'
    
    return name


class NexusTVPageGenerator:
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "nexus_tv.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('nexus_tv')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "nexus_tv"
            self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.ffprobe_available = shutil.which('ffprobe') is not None
    
    def extract_video_duration(self, video_url):
        """
        Extract precise video duration using FFmpeg/ffprobe
        Returns duration in minutes, or None if extraction fails
        """
        if not self.ffprobe_available:
            return None
        
        try:
            # Only try ffprobe for local files
            if video_url.startswith('http://') or video_url.startswith('https://'):
                return None
            
            video_path = Path(video_url)
            if not video_path.exists():
                return None
            
            # Use ffprobe to get duration
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                duration_seconds = float(result.stdout.strip())
                duration_minutes = int(duration_seconds / 60)
                return duration_minutes if duration_minutes > 0 else 1
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, FileNotFoundError):
            pass
        
        return None
    
    def extract_segment_markers(self, video_url, interval_seconds=300):
        """
        Extract segment markers at regular intervals using FFmpeg
        Returns list of timestamps in seconds for key frames
        """
        if not self.ffprobe_available:
            return []
        
        try:
            if not (video_url.startswith('http://') or video_url.startswith('https://')):
                video_path = Path(video_url)
                if not video_path.exists():
                    return []
                
                # Get keyframe timestamps
                cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'frame=pts_time,pict_type',
                    '-of', 'csv=p=0',
                    str(video_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    markers = []
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split(',')
                        if len(parts) == 2 and parts[1] == 'I':
                            try:
                                timestamp = float(parts[0])
                                if timestamp > 0 and timestamp % interval_seconds < 10:
                                    markers.append(int(timestamp))
                            except ValueError:
                                continue
                    return markers[:10]
        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return []
        
    def parse_m3u_to_schedule(self, m3u_content, channel_name="Channel", use_ffmpeg=False):
        """Parse M3U content and convert to NEXUS TV schedule format"""
        lines = m3u_content.strip().split('\n')
        schedule = []
        current_time = datetime.strptime("00:00", "%H:%M")
        default_duration = 30  # minutes
        
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                # Parse channel info
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                name_match = re.search(r',(.+)$', line)
                
                raw_title = name_match.group(1).strip() if name_match else 'Unknown'
                title = clean_title(raw_title)
                if logo_match and logo_match.group(1):
                    logo = logo_match.group(1)
                else:
                    # No logo available - use empty string for offline compatibility
                    logo = ""
                
                current_entry = {
                    'title': title,
                    'logo': logo,
                    'video': '',
                    'start_time': current_time.strftime("%H:%M"),
                    'end_time': ''
                }
                
            elif line and not line.startswith('#'):
                # This is the video URL
                if current_entry:
                    current_entry['video'] = line
                    
                    # Try to extract accurate duration using FFmpeg if enabled
                    duration = default_duration
                    if use_ffmpeg:
                        extracted_duration = self.extract_video_duration(line)
                        if extracted_duration:
                            duration = extracted_duration
                            current_entry['duration_seconds'] = duration * 60
                    
                    # Calculate end time
                    end_time = current_time + timedelta(minutes=duration)
                    if end_time.day > current_time.day:
                        end_time = datetime.strptime("23:59", "%H:%M")
                    
                    current_entry['end_time'] = end_time.strftime("%H:%M")
                    
                    # Extract segment markers if FFmpeg is enabled
                    if use_ffmpeg:
                        markers = self.extract_segment_markers(line)
                        if markers:
                            current_entry['segment_markers'] = markers
                    
                    schedule.append(current_entry)
                    
                    # Move to next slot
                    current_time = end_time
                    if current_time >= datetime.strptime("23:59", "%H:%M"):
                        break
                    
                    current_entry = {}
        
        return schedule
    
    def generate_page(self, m3u_content, channel_name, output_filename=None):
        """Generate a NEXUS TV page from M3U content"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Embed HLS.js, DASH.js, and Thumbnail System libraries inline for offline support
        libs_path = Path(__file__).resolve().parent.parent / "templates" / "web-iptv-extension" / "js" / "libs"
        templates_path = Path(__file__).resolve().parent.parent / "templates"
        
        # Read HLS.js (required for offline support)
        hls_js_path = libs_path / "hls.min.js"
        if not hls_js_path.exists():
            raise FileNotFoundError(f"HLS.js library required for offline support not found at: {hls_js_path}")
        
        with open(hls_js_path, 'r', encoding='utf-8') as f:
            hls_js_content = f.read()
        template = template.replace('// PLACEHOLDER_HLS_JS', hls_js_content)
        
        # Read DASH.js (required for offline support)
        dash_js_path = libs_path / "dash.all.min.js"
        if not dash_js_path.exists():
            raise FileNotFoundError(f"DASH.js library required for offline support not found at: {dash_js_path}")
        
        with open(dash_js_path, 'r', encoding='utf-8') as f:
            dash_js_content = f.read()
        template = template.replace('// PLACEHOLDER_DASH_JS', dash_js_content)
        
        # Read Thumbnail System (required for auto-screenshot feature)
        thumbnail_js_path = templates_path / "thumbnail-system.js"
        if not thumbnail_js_path.exists():
            raise FileNotFoundError(f"Thumbnail system required for auto-screenshot feature not found at: {thumbnail_js_path}")
        
        with open(thumbnail_js_path, 'r', encoding='utf-8') as f:
            thumbnail_js_content = f.read()
        template = template.replace('// PLACEHOLDER_THUMBNAIL_SYSTEM_JS', thumbnail_js_content)
        
        # Parse M3U to schedule
        schedule = self.parse_m3u_to_schedule(m3u_content, channel_name)
        
        if not schedule:
            raise ValueError("No valid entries found in M3U content")
        
        # Convert schedule to JavaScript array with proper escaping
        schedule_js = json.dumps(schedule, indent=12, ensure_ascii=False)
        
        # Sanitize any potential HTML/JS breaking characters
        schedule_js = schedule_js.replace('</script>', '<\\/script>')
        
        # Find and replace the schedule_data array
        # Split at the marker and rebuild to ensure clean replacement
        start_marker = 'let schedule_data = ['
        end_marker = '];'
        
        start_idx = template.find(start_marker)
        if start_idx == -1:
            raise ValueError("Template does not contain 'let schedule_data = [' marker")
        
        # Find the closing bracket and semicolon
        # Count brackets to handle nested arrays
        bracket_count = 0
        search_start = start_idx + len(start_marker) - 1  # -1 to include the opening [
        end_idx = -1
        
        for i in range(search_start, len(template)):
            if template[i] == '[':
                bracket_count += 1
            elif template[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # Found the matching closing bracket
                    if i + 1 < len(template) and template[i + 1] == ';':
                        end_idx = i + 2  # Include the semicolon
                        break
        
        if end_idx == -1:
            raise ValueError("Could not find matching end of schedule_data array")
        
        # Rebuild the HTML with new schedule data
        modified_html = (
            template[:start_idx] +
            f'let schedule_data = {schedule_js};' +
            template[end_idx:]
        )
        
        # Update channel name in title and display
        modified_html = modified_html.replace(
            '<title>NEXUS TV - Classic Movies Channel</title>',
            f'<title>NEXUS TV - {channel_name}</title>'
        )
        
        # Replace HUB_LINK with correct relative path
        # Since nexus_tv pages are in generated_pages/nexus_tv/[channel]/player.html
        # They need to go back two levels to reach index.html
        modified_html = modified_html.replace('{{HUB_LINK}}', '../../index.html')
        
        # Create output directory structure
        output_name = output_filename if output_filename else channel_name
        safe_name = re.sub(r'[^a-z0-9]+', '_', output_name.lower())
        page_dir = self.output_dir / safe_name
        page_dir.mkdir(exist_ok=True)
        
        output_path = page_dir / "player.html"
        
        # Write generated page
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        return output_path
    
    def generate_from_file(self, m3u_file, channel_name=None):
        """Generate page from M3U file"""
        m3u_path = Path(m3u_file)
        
        if not m3u_path.exists():
            raise FileNotFoundError(f"M3U file not found: {m3u_file}")
        
        with open(m3u_path, 'r', encoding='utf-8', errors='ignore') as f:
            m3u_content = f.read()
        
        if not channel_name:
            channel_name = m3u_path.stem.replace('_', ' ').title()
        
        return self.generate_page(m3u_content, channel_name)
    
    def generate_channel_selector(self, generated_pages):
        """Generate a channel selector splash page"""
        selector_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS TV - Channel Selector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', 'Arial Black', 'Impact', sans-serif;
            font-weight: 700;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0a0a0f 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 243, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
            animation: bgPulse 10s ease-in-out infinite;
            z-index: 0;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        .container {
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 60px;
            padding: 30px;
            background: rgba(0, 0, 0, 0.5);
            border: 2px solid #00f3ff;
            border-radius: 20px;
            box-shadow: 0 0 40px rgba(0, 243, 255, 0.3);
        }
        
        h1 {
            font-size: 4em;
            font-weight: 900;
            background: linear-gradient(90deg, #00f3ff, #ff00ff, #00f3ff);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient 3s linear infinite;
            text-shadow: 0 0 30px rgba(0, 243, 255, 0.5);
            margin-bottom: 10px;
        }
        
        @keyframes gradient {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }
        
        .subtitle {
            font-size: 1.2em;
            color: #00f3ff;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        
        .channels-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            padding: 20px;
        }
        
        .channel-card {
            background: rgba(0, 0, 0, 0.6);
            border: 2px solid #00f3ff;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .channel-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 243, 255, 0.1), transparent);
            transform: rotate(45deg);
            transition: all 0.5s;
        }
        
        .channel-card:hover {
            transform: translateY(-10px);
            border-color: #ff00ff;
            box-shadow: 0 0 40px rgba(255, 0, 255, 0.5);
        }
        
        .channel-card:hover::before {
            left: 100%;
        }
        
        .channel-icon {
            font-size: 3em;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #00f3ff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .channel-name {
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .channel-info {
            font-size: 0.9em;
            color: #888;
            margin-bottom: 15px;
        }
        
        .watch-btn {
            display: inline-block;
            background: linear-gradient(90deg, #00f3ff, #ff00ff);
            color: #fff;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .watch-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.8);
        }
        
        .stats {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            border: 1px solid #00f3ff;
        }
        
        .stats h3 {
            color: #00f3ff;
            font-size: 1.3em;
            margin-bottom: 10px;
        }
        
        .stats p {
            color: #888;
        }
    </style>
</head>
<body>
    <div class="animated-bg"></div>
    
    <div class="container">
        <header>
            <h1>📺 NEXUS TV</h1>
            <p class="subtitle">Choose Your Channel</p>
        </header>
        
        <div class="channels-grid" id="channelsGrid">
            <!-- Channels will be inserted here -->
        </div>
        
        <div class="stats">
            <h3><i class="fas fa-broadcast-tower"></i> Network Status</h3>
            <p><span id="channelCount">0</span> channels available • 24/7 streaming</p>
        </div>
    </div>
    
    <script>
        const channels = ''' + json.dumps([
            {
                'name': page['name'],
                'file': page['file'],
                'programs': page.get('programs', 0)
            } for page in generated_pages
        ], indent=12) + ''';
        
        const grid = document.getElementById('channelsGrid');
        const channelCount = document.getElementById('channelCount');
        
        channels.forEach((channel, index) => {
            const card = document.createElement('div');
            card.className = 'channel-card';
            card.innerHTML = `
                <div class="channel-icon"><i class="fas fa-tv"></i></div>
                <div class="channel-name">${channel.name}</div>
                <div class="channel-info">${channel.programs} programs available</div>
                <a href="${channel.file}" class="watch-btn">
                    <i class="fas fa-play"></i> Watch Now
                </a>
            `;
            grid.appendChild(card);
        });
        
        channelCount.textContent = channels.length;
    </script>
</body>
</html>'''
        
        # Save hub to root of pages_dir, not in subdirectory
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            selector_path = manager.pages_dir / "index.html"
        except ImportError:
            # Fallback to root of generated_pages
            selector_path = self.output_dir.parent / "index.html"
        
        # Ensure the directory exists
        selector_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path

class WebIPTVGenerator:
    """
    Web-IPTV-Extension Page Generator
    Generates a Web IPTV player with channel list from M3U playlists
    """
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "templates" / "web-iptv-extension"
        self.template_dir = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('web_iptv')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "web_iptv"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel information"""
        channels = []
        lines = m3u_content.strip().split('\n')
        current_channel = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                # Extract channel info
                name_match = re.search(r'tvg-name="([^"]*)"', line)
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                title_match = re.search(r',(.+)$', line)
                
                raw_name = name_match.group(1) if name_match else (title_match.group(1) if title_match else 'Unknown')
                current_channel = {
                    'name': clean_title(raw_name),
                    'logo': logo_match.group(1) if logo_match else '',
                    'url': ''
                }
            elif line and not line.startswith('#') and current_channel.get('name'):
                current_channel['url'] = line
                channels.append({**current_channel})
                current_channel = {}
        
        return channels
    
    def generate_page(self, m3u_content, channel_name, output_filename=None):
        """
        Generate a Web IPTV player page from M3U content
        
        Args:
            m3u_content: M3U playlist content as string
            channel_name: Name for the channel/playlist
            output_filename: Optional custom filename (defaults to channel_name)
        
        Returns:
            Path to the generated player HTML file
        """
        # Parse channels
        channels = self.parse_m3u_to_channels(m3u_content)
        
        if not channels:
            raise ValueError("No valid channels found in M3U content")
        
        # Use channel_name as folder name if no custom filename specified
        output_name = output_filename if output_filename else channel_name
        
        # Create output directory with sanitized name
        safe_dir_name = sanitize_directory_name(output_name)
        page_dir = self.output_dir / safe_dir_name
        page_dir.mkdir(exist_ok=True)
        
        # Copy template files
        import shutil
        
        # Copy CSS
        css_dir = page_dir / "css"
        css_dir.mkdir(exist_ok=True)
        if (self.template_dir / "css" / "styles.css").exists():
            shutil.copy(self.template_dir / "css" / "styles.css", css_dir / "styles.css")
        
        # Copy JS
        js_dir = page_dir / "js"
        js_dir.mkdir(exist_ok=True)
        if (self.template_dir / "js" / "app.js").exists():
            shutil.copy(self.template_dir / "js" / "app.js", js_dir / "app.js")
        
        # Copy JS libraries (HLS.js, DASH.js, Feather, Thumbnail System, etc) for offline use
        libs_dir = js_dir / "libs"
        libs_dir.mkdir(exist_ok=True)
        if (self.template_dir / "js" / "libs").exists():
            for lib_file in (self.template_dir / "js" / "libs").glob("*.js"):
                shutil.copy(lib_file, libs_dir / lib_file.name)
        
        # Copy thumbnail-system.js from templates root
        thumbnail_system_src = Path(__file__).resolve().parent.parent / "templates" / "thumbnail-system.js"
        if thumbnail_system_src.exists():
            shutil.copy(thumbnail_system_src, libs_dir / "thumbnail-system.js")
        
        # Copy icons if they exist
        icons_dir = page_dir / "icons"
        icons_dir.mkdir(exist_ok=True)
        if (self.template_dir / "icons").exists():
            for icon_file in (self.template_dir / "icons").glob("*.png"):
                shutil.copy(icon_file, icons_dir / icon_file.name)
        
        # Generate channel list HTML
        channel_html = ""
        for i, channel in enumerate(channels):
            channel_html += f'''
                <div class="channel-item" data-index="{i}">
                    <div class="channel-name">{channel['name']}</div>
                    <div class="channel-url">{channel['url'][:50]}...</div>
                </div>
            '''
        
        # Read template
        template_file = self.template_dir / "player.html"
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template_html = f.read()
        
        # Inject channel data into template
        # Use cleaned channel data (JSON) instead of raw M3U to preserve clean titles
        channels_json = json.dumps(channels, ensure_ascii=False)
        output_html = template_html.replace('__CHANNEL_DATA__', channels_json)
        
        # Write output file
        output_file = page_dir / "player.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_html)
        
        # Copy manifest and background.js for Chrome extension
        for file_name in ["manifest.json", "background.js"]:
            src_file = self.template_dir / file_name
            if src_file.exists():
                shutil.copy(src_file, page_dir / file_name)
        
        return output_file
    
    def generate_selector_page(self, generated_pages):
        """
        Generate a selector/index page listing all generated players
        
        Args:
            generated_pages: List of dicts with 'name' and 'file' keys
        
        Returns:
            Path to the selector HTML file
        """
        selector_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web IPTV Player - Channel Selector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 40px;
            font-size: 2.5rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }
        .card {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h2 {
            color: #333;
            margin-bottom: 12px;
        }
        .card p {
            color: #666;
            margin-bottom: 16px;
        }
        .btn {
            display: inline-block;
            background: #667eea;
            color: #fff;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Web IPTV Player</h1>
        <div class="grid" id="grid"></div>
    </div>
    <script>
        const channels = ''' + json.dumps([
            {
                'name': page['name'],
                'file': page['file'],
                'channels': page.get('channels', 0)
            } for page in generated_pages
        ], indent=12) + ''';
        
        const grid = document.getElementById('grid');
        channels.forEach(channel => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h2>${channel.name}</h2>
                <p>${channel.channels} channels available</p>
                <a href="${channel.file}" class="btn">Watch Now</a>
            `;
            grid.appendChild(card);
        });
    </script>
</body>
</html>'''
        
        selector_path = self.output_dir / "index.html"
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path

class SimplePlayerGenerator:
    """
    Simple Player Generator
    Generates a clean, responsive player with playlist support
    """
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "templates" / "simple-player"
        self.template_dir = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('simple_player')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "simple_player"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel information with group support"""
        channels = []
        lines = m3u_content.strip().split('\n')
        current_channel = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                name_match = re.search(r'tvg-name="([^"]*)"', line)
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                group_match = re.search(r'group-title="([^"]*)"', line)
                title_match = re.search(r',(.+)$', line)
                
                raw_name = name_match.group(1) if name_match else (title_match.group(1) if title_match else 'Unknown')
                current_channel = {
                    'name': clean_title(raw_name),
                    'logo': logo_match.group(1) if logo_match else '',
                    'group': group_match.group(1) if group_match else 'Uncategorized',
                    'url': ''
                }
            elif line and not line.startswith('#') and current_channel.get('name'):
                current_channel['url'] = line
                channels.append({**current_channel})
                current_channel = {}
        
        return channels
    
    def generate_page(self, m3u_content, channel_name, output_filename=None):
        """
        Generate a Simple Player page from M3U content
        
        Args:
            m3u_content: M3U playlist content as string
            channel_name: Name for the channel/playlist
            output_filename: Optional custom filename (defaults to channel_name)
        
        Returns:
            Path to the generated player HTML file
        """
        channels = self.parse_m3u_to_channels(m3u_content)
        
        if not channels:
            raise ValueError("No valid channels found in M3U content")
        
        output_name = output_filename if output_filename else channel_name
        safe_dir_name = sanitize_directory_name(output_name)
        page_dir = self.output_dir / safe_dir_name
        page_dir.mkdir(exist_ok=True)
        
        # Copy CSS
        css_dir = page_dir / "css"
        css_dir.mkdir(exist_ok=True)
        if (self.template_dir / "css" / "styles.css").exists():
            shutil.copy(self.template_dir / "css" / "styles.css", css_dir / "styles.css")
        
        # Copy JS
        js_dir = page_dir / "js"
        js_dir.mkdir(exist_ok=True)
        if (self.template_dir / "js" / "app.js").exists():
            shutil.copy(self.template_dir / "js" / "app.js", js_dir / "app.js")
        
        # Copy JS libraries (HLS.js, DASH.js, Feather, Thumbnail System, etc) for offline use
        libs_dir = js_dir / "libs"
        libs_dir.mkdir(exist_ok=True)
        if (self.template_dir / "js" / "libs").exists():
            for lib_file in (self.template_dir / "js" / "libs").glob("*.js"):
                shutil.copy(lib_file, libs_dir / lib_file.name)
        
        # Copy thumbnail-system.js from templates root
        thumbnail_system_src = Path(__file__).resolve().parent.parent / "templates" / "thumbnail-system.js"
        if thumbnail_system_src.exists():
            shutil.copy(thumbnail_system_src, libs_dir / "thumbnail-system.js")
        
        # Read template
        template_file = self.template_dir / "player.html"
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholders
        channels_data = {'channels': channels}
        channels_json = json.dumps(channels_data, ensure_ascii=False)
        html_content = html_content.replace('__PLAYLIST_NAME__', channel_name)
        html_content = html_content.replace("window.PLAYLIST_DATA = '__PLAYLIST_JSON__';", 
                                           f"window.PLAYLIST_DATA = {channels_json};")
        
        # Write output
        output_path = page_dir / "player.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_selector_page(self, generated_pages):
        """Generate a selector page with all generated players"""
        selector_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Player - Channel Selector</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #000 0%, #1a1a2e 100%); 
            color: #ffff00; 
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 40px; 
            font-size: 2.5em; 
            text-shadow: 0 0 20px rgba(255, 255, 0, 0.5);
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 30px; 
        }}
        .card {{ 
            background: rgba(0, 0, 50, 0.8); 
            padding: 30px; 
            border-radius: 10px; 
            border: 2px solid #00f;
            transition: all 0.3s;
            text-align: center;
        }}
        .card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 10px 30px rgba(0, 0, 255, 0.5);
            border-color: #ffff00;
        }}
        .card h2 {{ color: #ffff00; margin-bottom: 15px; font-size: 1.5em; }}
        .card p {{ color: #ccc; margin-bottom: 20px; }}
        .btn {{ 
            display: inline-block;
            background: rgba(0, 0, 200, 0.8); 
            color: #ffff00; 
            padding: 12px 30px; 
            text-decoration: none; 
            border-radius: 5px;
            font-weight: bold;
            border: 1px solid #00f;
            transition: all 0.2s;
        }}
        .btn:hover {{ 
            background: rgba(0, 0, 255, 0.9); 
            box-shadow: 0 0 15px rgba(0, 0, 255, 0.6);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 Simple Player - Select Channel</h1>
        <div class="grid" id="grid"></div>
    </div>
    <script>
        const channels = ''' + json.dumps([
            {
                'name': page['name'],
                'file': page['file'],
                'channels': page.get('channels', 0)
            } for page in generated_pages
        ], indent=12) + ''';
        
        const grid = document.getElementById('grid');
        channels.forEach(channel => {{
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h2>${{channel.name}}</h2>
                <p>${{channel.channels}} channels available</p>
                <a href="${{channel.file}}" class="btn">▶ Watch Now</a>
            `;
            grid.appendChild(card);
        }});
    </script>
</body>
</html>'''
        
        selector_path = self.output_dir / "index.html"
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path

class RumbleChannelGenerator:
    """Generate standalone Rumble Channel player pages from playlists with Rumble videos"""
    
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "rumble_channel.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('rumble_channel')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "rumble_channel"
            self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize Rumble Helper for URL normalization and metadata enrichment
        try:
            from services.rumble_helper import RumbleHelper
            self.rumble_helper = RumbleHelper()
        except Exception as e:
            print(f"Warning: Could not load RumbleHelper: {e}")
            self.rumble_helper = None
    
    def generate_page(self, channels, page_name="rumble_channel"):
        """
        Generate Rumble Channel player page from playlist
        
        Args:
            channels: List of channel dicts with Rumble video info
            page_name: Name for the generated page folder
            
        Returns:
            Path to generated HTML file
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        # Filter only Rumble channels
        rumble_channels = []
        for ch in channels:
            custom_tags = ch.get('custom_tags', {})
            if custom_tags.get('PROVIDER') == 'RUMBLE':
                rumble_channels.append(ch)
        
        if not rumble_channels:
            raise ValueError("No Rumble videos found in playlist")
        
        # Create page folder
        safe_dir_name = sanitize_directory_name(page_name)
        page_folder = self.output_dir / safe_dir_name
        page_folder.mkdir(exist_ok=True, parents=True)
        
        # Build playlist JSON for template
        playlist_data = []
        for idx, ch in enumerate(rumble_channels):
            custom_tags = ch.get('custom_tags', {})
            url = ch.get('url', '')
            
            # Try to use RumbleHelper for automatic URL normalization and metadata enrichment
            if self.rumble_helper and url:
                try:
                    # Enrich channel data with helper (normalizes URL, fetches metadata, looks up pub codes)
                    enriched = self.rumble_helper.enrich_channel_data(url, ch.get('name'))
                    
                    video_entry = {
                        'title': enriched.get('title', ch.get('name', f'Rumble Video {idx + 1}')),
                        'embed_url': enriched.get('embed_url', url),
                        'thumbnail': enriched.get('metadata', {}).get('thumbnail_url', ch.get('logo', '')),
                        'video_id': enriched.get('metadata', {}).get('video_id', custom_tags.get('VIDEO_ID', '')),
                        'pub_code': enriched.get('metadata', {}).get('pub_code', custom_tags.get('PUB_CODE', '')),
                        'width': enriched.get('metadata', {}).get('width', custom_tags.get('WIDTH', 640)),
                        'height': enriched.get('metadata', {}).get('height', custom_tags.get('HEIGHT', 360))
                    }
                except Exception as e:
                    print(f"Warning: RumbleHelper enrichment failed for {url}: {e}")
                    # Fallback to custom_tags
                    video_entry = {
                        'title': ch.get('name', f'Rumble Video {idx + 1}'),
                        'embed_url': custom_tags.get('EMBED_URL', url),
                        'thumbnail': ch.get('logo', ''),
                        'video_id': custom_tags.get('VIDEO_ID', ''),
                        'pub_code': custom_tags.get('PUB_CODE', ''),
                        'width': custom_tags.get('WIDTH', 640),
                        'height': custom_tags.get('HEIGHT', 360)
                    }
            else:
                # Fallback: use custom_tags if RumbleHelper not available
                video_entry = {
                    'title': ch.get('name', f'Rumble Video {idx + 1}'),
                    'embed_url': custom_tags.get('EMBED_URL', url),
                    'thumbnail': ch.get('logo', ''),
                    'video_id': custom_tags.get('VIDEO_ID', ''),
                    'pub_code': custom_tags.get('PUB_CODE', ''),
                    'width': custom_tags.get('WIDTH', 640),
                    'height': custom_tags.get('HEIGHT', 360)
                }
            
            # Final embed URL validation
            if not video_entry['embed_url'] and video_entry['video_id']:
                # Fallback: construct embed URL from video_id and pub_code
                if video_entry['pub_code']:
                    video_entry['embed_url'] = f"https://rumble.com/embed/{video_entry['video_id']}/?pub={video_entry['pub_code']}"
                else:
                    video_entry['embed_url'] = f"https://rumble.com/embed/{video_entry['video_id']}/"
            
            playlist_data.append(video_entry)
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders with proper escaping
        # Escape HTML in page title
        safe_title = page_name.replace('_', ' ').title().replace('<', '&lt;').replace('>', '&gt;')
        html_content = template.replace('{PAGE_TITLE}', safe_title)
        html_content = html_content.replace('{TOTAL_VIDEOS}', str(len(playlist_data)))
        
        # Safely embed JSON - escape </script> to prevent script breakout
        playlist_json = json.dumps(playlist_data, indent=2).replace('</script>', '<\\/script>')
        html_content = html_content.replace('{PLAYLIST_JSON}', playlist_json)
        
        # Write HTML file
        html_path = page_folder / f"{page_name}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create README
        readme_path = page_folder / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""Rumble Channel Player: {page_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a standalone Rumble video player page.

Videos: {len(playlist_data)}

Features:
• Sequential playback with next/previous controls
• Playlist sidebar with thumbnails
• Keyboard navigation (← → arrows)
• Responsive design for mobile and desktop
• 100% offline (metadata embedded)

To use:
1. Open {page_name}.html in any modern web browser
2. Click any video in the playlist to start
3. Use keyboard arrows or on-screen buttons to navigate
4. Videos will play in embedded Rumble iframes

Note: Videos require internet connection to stream from Rumble.
All metadata is embedded offline, but video content streams from Rumble.com
""")
        
        return html_path
    
    def generate_selector(self, generated_pages):
        """Generate a selector/index page for multiple Rumble Channel pages"""
        selector_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rumble Channel Selector</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff; 
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 40px; 
            font-size: 2.5em; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 30px; 
        }}
        .card {{ 
            background: rgba(0, 0, 0, 0.4); 
            padding: 30px; 
            border-radius: 15px; 
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
            border-color: #fff;
        }}
        .card h2 {{ margin-bottom: 15px; font-size: 1.5em; }}
        .card p {{ color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; }}
        .btn {{ 
            display: inline-block;
            background: #667eea; 
            color: #fff; 
            padding: 12px 30px; 
            text-decoration: none; 
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .btn:hover {{ 
            background: #5568d3; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 Rumble Channels</h1>
        <div class="grid" id="grid"></div>
    </div>
    <script>
        const channels = ''' + json.dumps([
            {
                'name': page['name'],
                'file': page['file'],
                'videos': page.get('videos', 0)
            } for page in generated_pages
        ], indent=12) + ''';
        
        const grid = document.getElementById('grid');
        channels.forEach(channel => {{
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h2>${{channel.name}}</h2>
                <p>${{channel.videos}} videos available</p>
                <a href="${{channel.file}}" class="btn">▶ Watch Now</a>
            `;
            grid.appendChild(card);
        }});
    </script>
</body>
</html>'''
        
        selector_path = self.output_dir / "rumble_index.html"
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path


class MultiChannelGenerator:
    """Generate standalone Multi-Channel Viewer pages with 1-6 simultaneous video channels"""
    
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "multi_channel.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('multi_channel')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "multi_channel"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_page(self, channels, page_name="multi_channel", default_channel_count=1):
        """
        Generate Multi-Channel Viewer page from playlist
        
        Args:
            channels: List of channel dicts with video info
            page_name: Name for the generated page folder
            default_channel_count: Default number of channels to show (1-6)
            
        Returns:
            Path to generated HTML file
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        if not channels:
            raise ValueError("No channels provided")
        
        # Validate default channel count
        if default_channel_count not in [1, 2, 3, 4, 6]:
            default_channel_count = 1
        
        # Create page folder
        safe_dir_name = sanitize_directory_name(page_name)
        page_folder = self.output_dir / safe_dir_name
        page_folder.mkdir(exist_ok=True, parents=True)
        
        # Build playlist JSON for template
        playlist_data = []
        for idx, ch in enumerate(channels):
            video_entry = {
                'title': ch.get('name', f'Channel {idx + 1}'),
                'url': ch.get('url', ''),
                'logo': ch.get('logo', ''),
                'group': ch.get('group', 'Other'),
                'duration': ch.get('duration', 0)
            }
            playlist_data.append(video_entry)
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders with proper escaping
        safe_title = page_name.replace('_', ' ').title().replace('<', '&lt;').replace('>', '&gt;')
        html_content = template.replace('{PAGE_TITLE}', safe_title)
        html_content = html_content.replace('{TOTAL_CHANNELS}', str(len(playlist_data)))
        
        # Safely embed JSON - escape </script> to prevent script breakout
        playlist_json = json.dumps(playlist_data, indent=2).replace('</script>', '<\\/script>')
        html_content = html_content.replace('{PLAYLIST_JSON}', playlist_json)
        
        # Set default channel count
        html_content = html_content.replace('value="1">1 Channel</option>', 
                                           f'value="1"{"selected" if default_channel_count==1 else ""}>1 Channel</option>')
        html_content = html_content.replace('value="2">2 Channels</option>', 
                                           f'value="2"{"selected" if default_channel_count==2 else ""}>2 Channels</option>')
        html_content = html_content.replace('value="3">3 Channels</option>', 
                                           f'value="3"{"selected" if default_channel_count==3 else ""}>3 Channels</option>')
        html_content = html_content.replace('value="4">4 Channels</option>', 
                                           f'value="4"{"selected" if default_channel_count==4 else ""}>4 Channels</option>')
        html_content = html_content.replace('value="6">6 Channels</option>', 
                                           f'value="6"{"selected" if default_channel_count==6 else ""}>6 Channels</option>')
        
        # Write HTML file
        html_path = page_folder / f"{page_name}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create README
        readme_path = page_folder / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""Multi-Channel Viewer: {page_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a standalone multi-channel video player page.

Channels Available: {len(playlist_data)}
Default Layout: {default_channel_count} channel(s)

Features:
• Support for 1 to 6 simultaneous video channels
• Responsive CSS Grid layout that adapts to screen size
• Smart audio management (only one channel plays audio at a time)
• Click any channel to make it the active audio source
• Time-based rotation with configurable intervals (5-60 minutes)
• Focus mode: Click ⛶ to expand any channel to fullscreen
• Keyboard shortcuts:
  - Press 1-6 to switch active audio to that channel
  - Press SPACE to play/pause all channels
  - Press ESC to exit focus mode
• HLS and DASH stream support
• Mobile-responsive design

Controls:
• Channel Count Selector: Choose 1, 2, 3, 4, or 6 channels
• Rotation Controls: Start/stop automatic channel switching
• Interval Selector: Set rotation time (5-60 min)
• Play All / Pause All: Control all channels at once
• Mute All: Silence all channels

To use:
1. Open {page_name}.html in any modern web browser
2. Select the number of channels you want to view
3. Optionally enable rotation for automatic channel switching
4. Click any channel to make it the active audio source
5. Use ⛶ button to focus/expand any channel to fullscreen

Note: Only one channel plays audio at a time (indicated by 🔊 AUDIO indicator).
The active channel has a green border and glowing effect.
""")
        
        return html_path
    
    def generate_selector(self, generated_pages):
        """Generate a selector/index page for multiple Multi-Channel pages"""
        selector_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Channel Viewer Selector</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff; 
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 40px; 
            font-size: 2.5em; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 30px; 
        }}
        .card {{ 
            background: rgba(0, 0, 0, 0.4); 
            padding: 30px; 
            border-radius: 15px; 
            border: 2px solid rgba(74, 144, 226, 0.5);
            transition: all 0.3s;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
            border-color: #4a90e2;
        }}
        .card h2 {{ margin-bottom: 15px; font-size: 1.5em; }}
        .card p {{ color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; }}
        .btn {{ 
            display: inline-block;
            background: #4a90e2; 
            color: #fff; 
            padding: 12px 30px; 
            text-decoration: none; 
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .btn:hover {{ 
            background: #357abd; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(74, 144, 226, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 Multi-Channel Viewers</h1>
        <div class="grid" id="grid"></div>
    </div>
    <script>
        const pages = ''' + json.dumps([
            {
                'name': page['name'],
                'file': page['file'],
                'channels': page.get('channels', 0)
            } for page in generated_pages
        ], indent=12) + ''';
        
        const grid = document.getElementById('grid');
        pages.forEach(page => {{
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h2>${{page.name}}</h2>
                <p>${{page.channels}} channels available</p>
                <a href="${{page.file}}" class="btn">▶ Open Viewer</a>
            `;
            grid.appendChild(card);
        }});
    </script>
</body>
</html>'''
        
        selector_path = self.output_dir / "multichannel_index.html"
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path


class BufferTVGenerator:
    """
    Buffer TV Generator
    Generates TV player pages with buffering controls and numeric keypad
    """
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "buffer_tv.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('buffer_tv')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "buffer_tv"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel information"""
        channels = []
        lines = m3u_content.strip().split('\n')
        current_channel = {}
        channel_number = 1
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                name_match = re.search(r'tvg-name="([^"]*)"', line)
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                group_match = re.search(r'group-title="([^"]*)"', line)
                title_match = re.search(r',(.+)$', line)
                
                raw_name = name_match.group(1) if name_match else (title_match.group(1) if title_match else 'Unknown')
                current_channel = {
                    'number': channel_number,
                    'name': clean_title(raw_name),
                    'category': group_match.group(1) if group_match else 'General',
                    'urls': []
                }
            elif line and not line.startswith('#') and current_channel.get('name'):
                current_channel['urls'].append(line)
                channels.append({**current_channel})
                current_channel = {}
                channel_number += 1
        
        return channels
    
    def generate_page(self, m3u_content, page_name="buffer_tv"):
        """
        Generate Buffer TV player page from M3U content
        
        Args:
            m3u_content: M3U playlist content as string
            page_name: Name for the generated page folder
            
        Returns:
            Path to generated HTML file
        """
        channels = self.parse_m3u_to_channels(m3u_content)
        
        if not channels:
            raise ValueError("No valid channels found in M3U content")
        
        # Create page folder
        safe_dir_name = sanitize_directory_name(page_name)
        page_folder = self.output_dir / safe_dir_name
        page_folder.mkdir(exist_ok=True)
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace title placeholder
        safe_title = page_name.replace('_', ' ').title().replace('<', '&lt;').replace('>', '&gt;')
        html_content = template.replace('<title>TV Player with Improved Buffering</title>', 
                                       f'<title>{safe_title}</title>')
        
        # Safely embed JSON - escape </script> to prevent script breakout
        channels_json = json.dumps(channels, indent=16).replace('</script>', '<\\/script>')
        html_content = html_content.replace('const channels = [];', 
                                           f'const channels = {channels_json};')
        
        # Write HTML file
        html_path = page_folder / f"{page_name}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create README
        readme_path = page_folder / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""Buffer TV: {page_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a standalone TV player page with buffering controls.

Channels Available: {len(channels)}

Features:
• HLS.js integration for m3u8 streams
• Numeric keypad for channel selection (0-9, +10, +20)
• Advanced buffering controls:
  - Load timeout adjustment (5-30 seconds)
  - Retry delay configuration (1-10 seconds)
  - Real-time buffering indicator
• TV Guide overlay with all channels
• Quick channel categories (Movies, Entertainment, Documentary, Music)
• Full video controls (play/pause, volume, seek, fullscreen)
• Progress bar with time display
• Previous/Next channel navigation
• CORS proxy support for remote streams
• Blue to red gradient design (#003366 to #990000)

Controls:
• Click TV Guide button to see all channels
• Click Keypad button for numeric channel entry
• Use +10 and +20 buttons to jump channels quickly
• Adjust buffer settings in the control panel
• Use Previous/Next buttons to surf channels

To use:
1. Open {page_name}.html in any modern web browser
2. Use the TV Guide or keypad to select a channel
3. Adjust buffer settings if streams are slow to load
4. Use quick category buttons for instant channel access

Note: Buffering controls help optimize streaming for your connection speed.
The player automatically retries failed streams and moves to the next channel.
""")
        
        return html_path


class ClassicTVGenerator:
    """
    Classic TV Player Generator
    Generates edge-to-edge video player with gold theme and sliding sidebars
    """
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "classic_tv.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('classic_tv')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "classic_tv"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel data"""
        channels = []
        lines = m3u_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF'):
                # Extract channel info
                channel = {}
                
                # Get channel name
                name_match = re.search(r',(.+)$', line)
                channel['name'] = clean_title(name_match.group(1)) if name_match else 'Unknown Channel'
                
                # Get logo from tvg-logo attribute
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                channel['logo'] = logo_match.group(1) if logo_match else ''
                
                # Get next line as URL
                if i + 1 < len(lines) and not lines[i + 1].startswith('#'):
                    url = lines[i + 1].strip()
                    channel['url'] = url
                    
                    # Determine stream type
                    if '.m3u8' in url or 'hls' in url.lower():
                        channel['type'] = 'hls'
                    elif '.mpd' in url:
                        channel['type'] = 'dash'
                    else:
                        channel['type'] = 'mp4'
                    
                    channels.append(channel)
                    i += 1
            
            i += 1
        
        return channels
    
    def generate_page(self, m3u_content, page_name="classic_tv_player", playlist_title="Classic TV"):
        """Generate Classic TV player page from M3U content"""
        
        # Parse M3U to get channels
        channels = self.parse_m3u_to_channels(m3u_content)
        
        if not channels:
            raise ValueError("No valid channels found in M3U content")
        
        # Create page folder
        safe_dir_name = sanitize_directory_name(page_name)
        page_folder = self.output_dir / safe_dir_name
        page_folder.mkdir(exist_ok=True)
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Get HLS.js and DASH.js libraries
        hls_js = ""
        dash_js = ""
        
        hls_path = Path(__file__).resolve().parent.parent / "Web_Players" / "libs" / "hls.min.js"
        if hls_path.exists():
            with open(hls_path, 'r', encoding='utf-8') as f:
                hls_js = f.read()
        
        dash_path = Path(__file__).resolve().parent.parent / "Web_Players" / "libs" / "dash.all.min.js"
        if dash_path.exists():
            with open(dash_path, 'r', encoding='utf-8') as f:
                dash_js = f.read()
        
        # Build playlist data
        playlist_data = []
        for ch in channels:
            playlist_data.append({
                'name': ch['name'],
                'logo': ch.get('logo', ''),
                'url': ch['url'],
                'type': ch.get('type', 'mp4')
            })
        
        # Get hub link
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            hub_path = Path("../index.html")
            hub_link = str(hub_path)
        except:
            hub_link = "../index.html"
        
        # Replace placeholders
        html = template.replace('{{PLAYLIST_TITLE}}', playlist_title)
        html = html.replace('{{HUB_LINK}}', hub_link)
        html = html.replace('{{HLS_JS}}', hls_js)
        html = html.replace('{{DASH_JS}}', dash_js)
        html = html.replace('{{PLAYLIST_DATA}}', json.dumps(playlist_data, indent=2))
        
        # Write the HTML file
        output_file = page_folder / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"""
✓ Classic TV Player Generated Successfully!

• Location: {output_file}
• Channels: {len(channels)}
• Page Name: {page_name}

Features:
• Edge-to-edge fullscreen video display
• Gold-themed UI with sliding sidebars
• Playlist sidebar with channel thumbnails
• Settings sidebar with volume control
• Bottom control bar (previous/next/play/mute/fullscreen)
• Keyboard shortcuts (Space=play/pause, Arrow=navigate, M=mute, F=fullscreen)
• Auto-play next video on end
• HLS and DASH streaming support

To use:
1. Open index.html in any modern web browser
2. Click menu button (☰) to show playlist
3. Click settings button (⚙) to adjust volume
4. Use keyboard shortcuts for quick control
5. Hover to show bottom controls

Note: Videos play edge-to-edge for cinematic viewing experience.
Gold theme provides elegant, professional appearance.
""")
        
        return str(output_file), len(channels)


class StreamHubGenerator:
    """
    Stream Hub Generator
    Generates broadcast-quality live TV player with glass-morphism UI
    """
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "Web_Players" / "stream_hub.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('stream_hub')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "stream_hub"
            self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel information"""
        channels = []
        lines = m3u_content.strip().split('\n')
        current_channel = {}
        channel_number = 1
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                name_match = re.search(r'tvg-name="([^"]*)"', line)
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                group_match = re.search(r'group-title="([^"]*)"', line)
                title_match = re.search(r',(.+)$', line)
                
                raw_name = name_match.group(1) if name_match else (title_match.group(1) if title_match else 'Unknown')
                current_channel = {
                    'number': channel_number,
                    'name': clean_title(raw_name),
                    'logo': logo_match.group(1) if logo_match else '',
                    'group': group_match.group(1) if group_match else 'General'
                }
                channel_number += 1
                
            elif line and not line.startswith('#'):
                if current_channel:
                    current_channel['url'] = line
                    channels.append(current_channel)
                    current_channel = {}
        
        return channels
    
    def generate_page(self, m3u_content, page_name="Stream Hub Live"):
        """Generate a complete Stream Hub page from M3U content"""
        
        # Parse channels from M3U
        channels = self.parse_m3u_to_channels(m3u_content)
        
        if not channels:
            raise ValueError("No valid channels found in M3U content")
        
        # Create page folder
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in page_name).strip()
        safe_name = safe_name.replace(" ", "_")
        page_folder = self.output_dir / safe_name
        page_folder.mkdir(exist_ok=True)
        
        # Read template
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholders
        safe_title = page_name.replace("'", "\\'")
        html_content = html_content.replace('{{page_name}}', safe_title)
        html_content = html_content.replace('<title>{{page_name}} - Stream Hub Live TV</title>',
                                           f'<title>{safe_title} - Stream Hub Live TV</title>')
        
        # Create playlist JSON
        playlist_data = {
            'name': page_name,
            'channels': channels,
            'generated': datetime.now().isoformat(),
            'total': len(channels)
        }
        
        # Safely embed JSON
        playlist_json = json.dumps(playlist_data, indent=4).replace('</script>', '<\\/script>')
        html_content = html_content.replace('{{playlist_json}}', playlist_json)
        
        # Write HTML file
        html_path = page_folder / f"{safe_name}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create README
        readme_path = page_folder / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""Stream Hub: {page_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a professional broadcast-quality IPTV player with glass-morphism design.

Channels Available: {len(channels)}

Features:
• Glass-morphism UI with animated gradient backgrounds
• HLS.js primary player for m3u8 streams
• Automatic fallback: HLS → MP4 → Audio-only
• Smart connection retry with exponential backoff
• Live channel grid with real-time status
• Auto-detected channel categories
• Multi-timezone digital clock
• Numeric keypad for direct channel entry
• Search-as-you-type channel finder
• Smooth channel transitions with animations
• Audio visualizer for audio-only streams
• Quality badges (HD, FHD, 4K, SD)

Visual Design:
• Animated gradient background (purple/blue spectrum)
• Glass-morphism containers with blur effects
• Pulsing LIVE indicators
• Loading shimmer effects
• Channel transition animations
• Error state animations

Controls:
• Previous/Next channel buttons
• Play/Pause toggle
• Volume slider
• Fullscreen mode
• Numeric keypad (0-9 + OK)
• Category filters
• Real-time search

Keyboard Shortcuts:
• Space: Play/Pause
• ← →: Previous/Next channel
• 0-9: Direct channel number entry
• F: Toggle fullscreen
• ESC: Close dialogs

To use:
1. Open {safe_name}.html in any modern web browser
2. Channels auto-load on startup
3. Click any channel in the grid to play
4. Use numeric keypad for direct access
5. Filter by categories or search

Note: The player includes intelligent fallback mechanisms.
If HLS streaming fails, it automatically tries MP4 format.
If video fails completely, it falls back to audio-only mode
with a visual audio spectrum analyzer.
""")
        
        return html_path


class StandaloneSecurePageGenerator:
    """
    Standalone Secure Page Generator
    Generates completely self-contained HTML pages with:
    - All dependencies embedded inline (no external files)
    - Hidden URLs (never displayed in UI)
    - Smart chunking for large playlists (20% at a time)
    - Base64 encoded playlist data for obfuscation
    """
    
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).resolve().parent.parent / "templates" / "standalone_secure_player.html"
        self.template_path = Path(template_path)
        
        # Use OutputManager for organized directory structure
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            self.output_dir = manager.get_page_output_dir('standalone')
        except ImportError:
            # Fallback if OutputManager not available
            self.output_dir = Path("M3U_Matrix_Output") / "generated_pages" / "standalone"
            self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load HLS.js library for embedding
        self.hls_library = self._load_hls_library()
    
    def _load_hls_library(self):
        """Load HLS.js library content for embedding"""
        try:
            # Try to load HLS.js from templates directory
            hls_path = Path(__file__).resolve().parent.parent / "templates" / "simple-player" / "js" / "libs" / "hls.min.js"
            if hls_path.exists():
                with open(hls_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Fallback: Use a minimal HLS.js placeholder
            return "/* HLS.js library will be embedded here */"
        except Exception as e:
            print(f"Warning: Could not load HLS.js: {e}")
            return "/* HLS.js library placeholder */"
    
    def parse_m3u_to_channels(self, m3u_content):
        """Parse M3U content and extract channel information without exposing URLs"""
        channels = []
        lines = m3u_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF:'):
                # Parse channel info
                name_match = re.search(r',(.+)$', line)
                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                group_match = re.search(r'group-title="([^"]+)"', line)
                
                channel = {
                    'name': name_match.group(1) if name_match else 'Channel',
                    'logo': logo_match.group(1) if logo_match else '',
                    'group': group_match.group(1) if group_match else 'General'
                }
                
                # Get URL from next line but store internally
                i += 1
                if i < len(lines) and not lines[i].startswith('#'):
                    channel['_src'] = lines[i].strip()
                    channels.append(channel)
            
            i += 1
        
        return channels
    
    def generate_page(self, m3u_content, page_name="Secure Player", metadata=None):
        """
        Generate a completely self-contained HTML page
        
        Args:
            m3u_content: M3U playlist content
            page_name: Name for the page
            metadata: Optional metadata dictionary
        
        Returns:
            Path to generated HTML file
        """
        try:
            # Read template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Parse channels
            channels = self.parse_m3u_to_channels(m3u_content)
            
            if not channels:
                print("Warning: No valid channels found in playlist")
                return None
            
            # Prepare playlist data for embedding
            # We'll recreate a minimal M3U structure with only essential data
            playlist_lines = ['#EXTM3U']
            for channel in channels:
                # Include channel info but URL will be stored internally
                extinf_line = f'#EXTINF:-1 group-title="{channel["group"]}"'
                if channel.get('logo'):
                    extinf_line += f' tvg-logo="{channel["logo"]}"'
                extinf_line += f',{channel["name"]}'
                playlist_lines.append(extinf_line)
                playlist_lines.append(channel.get('_src', ''))
            
            # Base64 encode the playlist data for obfuscation
            import base64
            playlist_str = '\n'.join(playlist_lines)
            encoded_playlist = base64.b64encode(playlist_str.encode('utf-8')).decode('utf-8')
            
            # Generate safe filename
            safe_name = re.sub(r'[^\w\-_]', '_', page_name.lower())[:50]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_name}_{timestamp}.html"
            
            # Replace placeholders in template
            html_content = template.replace('{{PAGE_TITLE}}', page_name)
            html_content = html_content.replace('{{PLAYLIST_DATA}}', encoded_playlist)
            html_content = html_content.replace('{{HLS_LIBRARY}}', self.hls_library)
            
            # Add metadata if provided
            if metadata:
                meta_json = json.dumps(metadata, indent=2)
                html_content = html_content.replace('{{METADATA}}', meta_json)
            else:
                html_content = html_content.replace('{{METADATA}}', '{}')
            
            # Write output file
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Generated standalone secure page: {output_path}")
            print(f"   • {len(channels)} channels embedded")
            print(f"   • URLs hidden from display")
            print(f"   • 20% chunked loading enabled")
            print(f"   • Completely self-contained (no external dependencies)")
            
            # Create README for GitHub Pages
            self._create_github_pages_readme()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating standalone page: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_github_pages_readme(self):
        """Create README with GitHub Pages deployment instructions"""
        readme_content = """# Standalone Secure Player - GitHub Pages Deployment

## Quick Setup

1. **Create GitHub Repository**
   - Go to GitHub.com and create a new repository
   - Name it (e.g., `my-iptv-player`)
   - Make it PUBLIC (required for free GitHub Pages)

2. **Upload Generated Files**
   - Upload all files from `generated_pages/standalone/` folder
   - Make sure `index.html` is in the root (rename one of your players if needed)

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main (or master)
   - Folder: / (root)
   - Click Save

4. **Access Your Player**
   - Wait 2-5 minutes for deployment
   - Your site will be available at: `https://YOUR-USERNAME.github.io/REPO-NAME/`

## Features
- ✅ Completely self-contained (no server needed)
- ✅ URLs hidden from user view
- ✅ Smart loading (20% chunks for large playlists)
- ✅ Works offline once loaded
- ✅ Mobile responsive

## Multiple Players
You can host multiple players:
- `index.html` - Main player (accessible at root)
- `player2.html` - Additional player
- `player3.html` - Another player

Access them at:
- `https://YOUR-USERNAME.github.io/REPO-NAME/`
- `https://YOUR-USERNAME.github.io/REPO-NAME/player2.html`
- `https://YOUR-USERNAME.github.io/REPO-NAME/player3.html`

## Custom Domain (Optional)
1. Create file named `CNAME` with your domain
2. Configure DNS at your domain provider
3. Enable HTTPS in GitHub Pages settings

## Updates
Simply upload new HTML files to update your players. Changes go live in 1-2 minutes.
"""
        
        readme_path = self.output_dir / "README_GITHUB_PAGES.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📝 Created GitHub Pages deployment guide: {readme_path}")


if __name__ == "__main__":
    # Example usage
    generator = NexusTVPageGenerator()
    print("NEXUS TV Page Generator initialized")
    print(f"Output directory: {generator.output_dir}")
