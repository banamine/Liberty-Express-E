# How Python Extracts M3U Lists & HLS Stream URLs

## 1. EXTRACTION PROCESS (Text Parsing)
```python
import json
import re

# Example: Extract video IDs from text report
report_text = """
1. Channel: Bannons War Room | Video ID: v6zkg9o | Live Viewers: 48521
2. Channel: The Dan Bongino Show | Video ID: v6zkf12 | Live Viewers: 41283
"""

# Use REGEX to extract Video IDs
pattern = r"Video ID: (v[a-z0-9]+)"
video_ids = re.findall(pattern, report_text)
# Result: ['v6zkg9o', 'v6zkf12']
```

## 2. BUILDING HLS URLs
```python
# Rumble HLS pattern: https://rumble.com/live-hls-dvr/{VIDEO_ID_WITHOUT_V}/playlist.m3u8
video_id_with_v = "v6zkg9o"
video_id_clean = video_id_with_v.lstrip('v')  # Remove 'v' prefix
hls_url = f"https://rumble.com/live-hls-dvr/{video_id_clean}/playlist.m3u8"
# Result: https://rumble.com/live-hls-dvr/6zkg9o/playlist.m3u8
```

## 3. BUILDING M3U FORMAT
```python
# M3U format structure:
m3u_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10

#EXTINF:-1 tvg-logo="..." group-title="News", Channel Name
https://rumble.com/live-hls-dvr/6zkg9o/playlist.m3u8

#EXTINF:-1 tvg-logo="..." group-title="News", Another Channel
https://rumble.com/live-hls-dvr/6zkf12/playlist.m3u8
"""
```

## 4. COMPLETE EXTRACTION SCRIPT
```python
import json
import re

def extract_channels_from_text(report_file):
    """Parse text report and extract video IDs"""
    with open(report_file, 'r') as f:
        text = f.read()
    
    # Extract: name, video_id, viewers
    channels = []
    pattern = r"Channel: ([^|]+) \| Video ID: (v[a-z0-9]+) \| Live Viewers: ([0-9,]+)"
    
    for match in re.finditer(pattern, text):
        channel_name = match.group(1).strip()
        video_id = match.group(2)
        viewers = int(match.group(3).replace(',', ''))
        
        video_id_clean = video_id.lstrip('v')
        hls_url = f"https://rumble.com/live-hls-dvr/{video_id_clean}/playlist.m3u8"
        
        channels.append({
            "name": channel_name,
            "video_id": video_id,
            "hls_url": hls_url,
            "viewers": viewers
        })
    
    return channels

# Save as JSON
channels = extract_channels_from_text('report.txt')
with open('channels.json', 'w') as f:
    json.dump(channels, f, indent=2)

# OR convert to M3U
def json_to_m3u(channels_json_file):
    with open(channels_json_file, 'r') as f:
        channels = json.load(f)
    
    m3u_lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    
    for ch in channels:
        extinf = f"#EXTINF:-1 group-title=\"Rumble News\", {ch['name']}"
        m3u_lines.append(extinf)
        m3u_lines.append(ch['hls_url'])
        m3u_lines.append("")
    
    m3u_content = "\n".join(m3u_lines)
    
    with open('playlist.m3u', 'w') as f:
        f.write(m3u_content)

json_to_m3u('channels.json')
```

## KEY POINTS:
- **Text Parsing**: Use REGEX to extract data from reports
- **HLS URLs**: Rumble pattern = `https://rumble.com/live-hls-dvr/{ID_NO_V}/playlist.m3u8`
- **M3U Format**: Playlist standard with #EXTINF tags for each stream
- **LIMITATION**: HLS URLs expire after stream ends (temporary, not persistent)
- **Better Solution**: Use Rumble iframe embeds (persistent, works for VOD & live)
