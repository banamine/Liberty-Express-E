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

class NexusTVPageGenerator:
    def __init__(self, template_path="templates/nexus_tv_template.html"):
        self.template_path = Path(template_path)
        self.output_dir = Path("generated_pages")
        self.output_dir.mkdir(exist_ok=True)
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
                
                title = name_match.group(1).strip() if name_match else 'Unknown'
                if logo_match and logo_match.group(1):
                    logo = logo_match.group(1)
                else:
                    # Generate placeholder logo
                    short_title = title[:20].replace(' ', '+')
                    logo = f"https://placehold.co/300x169/1a1a2a/00f3ff?text={short_title}"
                
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
        
        # Output filename
        if not output_filename:
            safe_name = re.sub(r'[^a-z0-9]+', '_', channel_name.lower())
            output_filename = f"{safe_name}.html"
        
        output_path = self.output_dir / output_filename
        
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
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Orbitron', sans-serif;
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
        
        selector_path = self.output_dir / "index.html"
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(selector_html)
        
        return selector_path

if __name__ == "__main__":
    # Example usage
    generator = NexusTVPageGenerator()
    print("NEXUS TV Page Generator initialized")
    print(f"Output directory: {generator.output_dir}")
