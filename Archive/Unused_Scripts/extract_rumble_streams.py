#!/usr/bin/env python3
"""
Extract Rumble HLS streaming URLs and generate VLC-compatible M3U playlist
"""

import subprocess
import json
import sys

# Rumble channels with video IDs
CHANNELS = [
    ("ALEX JONES NETWORK FEED: LIVE 247!", "v66kw07"),
    ("Patriot News Outlet Live", "v6xsfsw"),
    ("HOME OF REAL NEWS", "v70rj00"),
    ("NEWSMAX2 LIVE", "v60552h"),
    ("RT News | Livestream 24/7", "v35waq4"),
    ("RT DE LIVE-TV", "v7215zc"),
    ("The Alex Jones Show", "v723rn4"),
    ("Infowars Network Feed: LIVE 247", "v6xkx0a"),
    ("His Glory TV 24/7", "v71yfdc"),
    ("ALEX JONES - INFOWARS LIVE", "v71b46y"),
]

def extract_m3u8_url(video_id):
    """Extract HLS m3u8 URL from Rumble video using yt-dlp"""
    url = f"https://rumble.com/v{video_id}"
    
    try:
        # Use yt-dlp to extract the streaming URL
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "best[ext=m3u8]/best",
                "--get-url",
                url
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            streaming_url = result.stdout.strip().split('\n')[0]
            if streaming_url.startswith('http'):
                return streaming_url
    except Exception as e:
        print(f"Error extracting {video_id}: {e}")
    
    return None

def generate_m3u(channels, output_file):
    """Generate M3U playlist with extracted streaming URLs"""
    playlist = "#EXTM3U\n"
    
    for idx, (name, video_id) in enumerate(channels, 1):
        print(f"[{idx}/{len(channels)}] Extracting: {name} ({video_id})...", end=" ", flush=True)
        
        m3u8_url = extract_m3u8_url(video_id)
        
        if m3u8_url:
            playlist += f"#EXTINF:-1,{name}\n{m3u8_url}\n"
            print("✅")
        else:
            # Fallback to embed URL if yt-dlp fails
            fallback = f"https://rumble.com/embed/{video_id}/?pub=4"
            playlist += f"#EXTINF:-1,{name}\n{fallback}\n"
            print("⚠️ (fallback)")
    
    # Write M3U file
    with open(output_file, 'w') as f:
        f.write(playlist)
    
    print(f"\n✅ M3U playlist saved to: {output_file}")
    
    # Show preview
    print("\n=== M3U Preview ===")
    lines = playlist.split('\n')
    for line in lines[:15]:
        if line.strip():
            print(line[:80])

if __name__ == "__main__":
    output = "scheduleflow_vlc.m3u"
    
    print("Extracting Rumble HLS streams for VLC...")
    print("=" * 50)
    
    generate_m3u(CHANNELS, output)
    
    print("\n✅ VLC Instructions:")
    print("1. Open VLC Media Player")
    print("2. Media → Open File → Select scheduleflow_vlc.m3u")
    print("3. Playlist loads all channels")
    print("4. Click channel to play")
