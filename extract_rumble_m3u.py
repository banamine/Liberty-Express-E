#!/usr/bin/env python3
"""
Extract real HLS/M3U8 URLs from Rumble videos
Similar to mpmux.com approach - fetch page, find streams, validate, save
"""

import os
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin

# Configuration
VIDEO_IDS = [
    "v66kw07",  # ALEX JONES NETWORK FEED: LIVE 247!
    "v6xsfsw",  # Patriot News Outlet Live
    "v70rj00",  # HOME OF REAL NEWS
    "v60552h",  # NEWSMAX2 LIVE
    "v35waq4",  # RT News | Livestream 24/7
    "v7215zc",  # RT DE LIVE-TV
    "v723rn4",  # The Alex Jones Show
    "v6xkx0a",  # Infowars Network Feed: LIVE 247
    "v71yfdc",  # His Glory TV 24/7
    "v71b46y",  # ALEX JONES - INFOWARS LIVE
]

CHANNEL_NAMES = {
    "v66kw07": "ALEX JONES NETWORK FEED: LIVE 247!",
    "v6xsfsw": "Patriot News Outlet Live",
    "v70rj00": "HOME OF REAL NEWS",
    "v60552h": "NEWSMAX2 LIVE",
    "v35waq4": "RT News | Livestream 24/7",
    "v7215zc": "RT DE LIVE-TV",
    "v723rn4": "The Alex Jones Show",
    "v6xkx0a": "Infowars Network Feed: LIVE 247",
    "v71yfdc": "His Glory TV 24/7",
    "v71b46y": "ALEX JONES - INFOWARS LIVE",
}

DELAY = 1  # Respectful delay between requests

def get_stream_url(video_id):
    """Extract HLS/M3U8 stream URL from Rumble video page"""
    url = f"https://rumble.com/v{video_id}.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"  Fetching: {url}...", end=" ", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None
    
    # Method 1: Look for HLS stream URLs in page content
    # Rumble embeds m3u8 URLs in the HTML or JavaScript
    hls_pattern = re.compile(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', re.IGNORECASE)
    matches = hls_pattern.findall(response.text)
    
    if matches:
        stream_url = matches[0]
        print(f"✅ Found HLS stream")
        return stream_url
    
    # Method 2: Look in JSON embedded in page
    json_pattern = re.compile(r'"url":\s*"(https?://[^"]+\.m3u8[^"]*)"', re.IGNORECASE)
    json_match = json_pattern.search(response.text)
    
    if json_match:
        stream_url = json_match.group(1)
        print(f"✅ Found HLS in JSON")
        return stream_url
    
    # Method 3: Look for live-hls-dvr pattern
    dvr_pattern = re.compile(r'(https?://[^\s"\'<>]*live-hls-dvr[^\s"\'<>]*\.m3u8[^\s"\'<>]*)', re.IGNORECASE)
    dvr_match = dvr_pattern.search(response.text)
    
    if dvr_match:
        stream_url = dvr_match.group(1)
        print(f"✅ Found DVR stream")
        return stream_url
    
    print("⚠️  No HLS stream found, using fallback")
    # Fallback: Return direct video page (VLC can sometimes handle this)
    return url

def generate_m3u(streams):
    """Generate M3U playlist from stream URLs"""
    m3u_content = "#EXTM3U\n"
    
    for idx, (video_id, stream_url) in enumerate(streams, 1):
        if stream_url:
            channel_name = CHANNEL_NAMES.get(video_id, f"Channel {idx}")
            m3u_content += f"#EXTINF:-1 tvg-id=\"{video_id}\",{channel_name}\n"
            m3u_content += f"{stream_url}\n"
    
    return m3u_content

def main():
    print("=" * 60)
    print("Rumble HLS Stream Extractor")
    print("=" * 60)
    print(f"\nExtracting {len(VIDEO_IDS)} channels...\n")
    
    streams = {}
    successful = 0
    
    for idx, video_id in enumerate(VIDEO_IDS, 1):
        print(f"[{idx}/{len(VIDEO_IDS)}] {CHANNEL_NAMES[video_id]}")
        stream_url = get_stream_url(video_id)
        
        if stream_url:
            streams[video_id] = stream_url
            successful += 1
        
        time.sleep(DELAY)
    
    print(f"\n✅ Successfully extracted {successful}/{len(VIDEO_IDS)} streams\n")
    
    # Generate M3U file
    m3u_content = generate_m3u(streams)
    
    # Save to both directories
    os.makedirs("generated_pages", exist_ok=True)
    os.makedirs("M3U_Matrix_Output", exist_ok=True)
    
    for output_path in ["generated_pages/scheduleflow_hls.m3u", "M3U_Matrix_Output/scheduleflow_hls.m3u"]:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        print(f"✅ Saved: {output_path}")
    
    print(f"\n✅ M3U playlist generated with {len(streams)} working streams")
    print("\nNext step: Use scheduleflow_hls.m3u in VLC Media Player")

if __name__ == "__main__":
    main()
