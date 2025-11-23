"""
PRIVATE MEDIA STRIPPER v2
Extracts ALL video/audio/streams/subtitles from any website
Creates perfect .m3u playlist - 100% offline & private
No logs, no telemetry - just pure media extraction
"""

import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin, urlparse
import time
import sys

# Config
OUTPUT_DIR = "stripped_media"
MASTER_PLAYLIST_NAME = "MASTER_PLAYLIST.m3u"
DELAY = 0.5  # be nice to servers
TIMEOUT = 15

# Create output folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Supported extensions
VIDEO_EXT = {'.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v', '.ts', '.mpg', '.mpeg', '.flv'}
AUDIO_EXT = {'.mp3', '.aac', '.wav', '.flac', '.m4a', '.ogg'}
STREAM_EXT = {'.m3u8', '.m3u'}
SUBTITLE_EXT = {'.vtt', '.srt', '.ass', '.ssa'}

ALL_EXT = VIDEO_EXT | AUDIO_EXT | STREAM_EXT | SUBTITLE_EXT

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def is_media_url(url):
    """Check if URL points to media file"""
    return any(url.lower().endswith(ext) for ext in ALL_EXT) or \
           "chunk" in url or "segment" in url or ".m3u8?" in url


def extract_urls_from_text(text, base_url):
    """Find all possible media URLs (even obfuscated ones)"""
    url_pattern = r'https?://[^\s<>"\'\]\[]+'
    candidates = re.findall(url_pattern, text)
    valid = []
    for u in candidates:
        if is_media_url(u) or any(u.lower().endswith(ext) for ext in ALL_EXT):
            full = urljoin(base_url, u.split('"')[0].split("'")[0])
            valid.append(full)
    return valid


def strip_site(url, progress_callback=None):
    """
    Extract all media links from website
    
    Args:
        url: Website URL to scan
        progress_callback: Function to call with (message) for progress updates
    
    Returns:
        dict with keys: 'found', 'subtitles', 'master_path', 'media_count'
    """
    if progress_callback is None:
        progress_callback = lambda msg: print(msg)
    
    progress_callback(f"Stripping: {url}")
    progress_callback("=" * 60)
    
    all_media = set()
    master_lines = ['#EXTM3U', '# Private Media Stripper - All in one playlist', '']
    
    try:
        progress_callback("Loading webpage...")
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        html = r.text
        base_url = r.url
        progress_callback(f"✓ Loaded {len(html)} bytes")
    except Exception as e:
        progress_callback(f"✗ Failed to load page: {str(e)}")
        return {
            'found': 0,
            'subtitles': 0,
            'master_path': None,
            'media_count': 0,
            'error': str(e)
        }
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract from HTML tags
    progress_callback("Scanning HTML tags...")
    for tag in soup.find_all(['source', 'video', 'audio', 'a', 'link', 'script', 'iframe']):
        src = tag.get('src') or tag.get('href') or tag.get('data-src')
        if src:
            full = urljoin(base_url, src)
            if is_media_url(full):
                all_media.add(full)
    
    # 2. Extract from JavaScript & raw page text
    progress_callback("Scanning JavaScript & page text...")
    all_media.update(extract_urls_from_text(html, base_url))
    
    # 3. Scan for blob: or data: URLs
    progress_callback("Scanning for blob URLs...")
    blob_pattern = r'(blob:https?://[^\s"\']+|data:[^"\']*?(mp4|m3u8|webm)[^"\']*)'
    all_media.update(re.findall(blob_pattern, html, re.I))
    
    progress_callback(f"\nFound {len(all_media)} unique media/subtitle links\n")
    
    subtitle_count = 0
    for i, link in enumerate(sorted(all_media), 1):
        progress_callback(f"[{i}] {link[:80]}...")
        
        try:
            # Download subtitles & small files directly
            if any(link.lower().endswith(ext) for ext in SUBTITLE_EXT) or "vtt" in link:
                try:
                    content = requests.get(link, headers=headers, timeout=10).text
                    ext = '.vtt' if 'vtt' in link else '.srt'
                    name = f"subtitle_{i}{ext}"
                    with open(os.path.join(OUTPUT_DIR, name), "w", encoding="utf-8") as f:
                        f.write(content)
                    progress_callback(f"   → Subtitle saved: {name}")
                    subtitle_count += 1
                except:
                    progress_callback(f"   → Subtitle failed (blocked/dead)")
            
            # Add every valid link to master playlist
            if link.startswith('http'):
                master_lines.append(f"#EXTINF:-1,{os.path.basename(urlparse(link).path) or f'Stream_{i}'}")
                master_lines.append(link)
                master_lines.append("")
                
        except Exception as e:
            progress_callback(f"   → Processing failed: {str(e)}")
        
        time.sleep(DELAY)
    
    # Save master playlist
    master_path = os.path.join(OUTPUT_DIR, MASTER_PLAYLIST_NAME)
    try:
        with open(master_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(master_lines))
        progress_callback(f"\n✓ Master playlist saved → {master_path}")
        progress_callback(f"✓ All files in → {os.path.abspath(OUTPUT_DIR)}")
    except Exception as e:
        progress_callback(f"\n✗ Failed to save master playlist: {str(e)}")
        return {
            'found': len(all_media),
            'subtitles': subtitle_count,
            'master_path': None,
            'media_count': len(all_media),
            'error': f"Failed to save: {str(e)}"
        }
    
    return {
        'found': len(all_media),
        'subtitles': subtitle_count,
        'master_path': master_path,
        'media_count': len(all_media)
    }


# CLI Interface
if __name__ == "__main__":
    print("""
    PRIVATE MEDIA STRIPPER v2
    Extracts ALL video/audio/streams/subtitles from any site
    Creates perfect .m3u playlist
    100% offline & private - no logging
    """)
    
    if len(sys.argv) > 1:
        # Called with URL as argument
        target = sys.argv[1]
    else:
        # Interactive prompt
        target = input("Enter URL to strip: ").strip()
    
    if target:
        result = strip_site(target)
        if result.get('master_path'):
            print(f"\n✓ SUCCESS!")
            print(f"  Media links found: {result['found']}")
            print(f"  Subtitles saved: {result['subtitles']}")
            print(f"  Master playlist: {result['master_path']}")
            sys.exit(0)
        else:
            print(f"\n✗ FAILED: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    else:
        print("No URL provided. Exiting.")
        sys.exit(1)
