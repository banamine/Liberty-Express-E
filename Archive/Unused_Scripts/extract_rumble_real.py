#!/usr/bin/env python3
"""
Extract REAL playable HLS streams from Rumble using yt-dlp
No scraping. No fake URLs. Actual working video streams.
"""

import subprocess
import json
import os

VIDEO_IDS = {
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

def extract_stream_with_ytdlp(video_id, name):
    """Use yt-dlp to extract REAL playable HLS stream"""
    url = f"https://rumble.com/v{video_id}"
    
    print(f"[{name}]", end=" ", flush=True)
    
    try:
        # yt-dlp extracts the actual playable format
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "best[ext=m3u8]/best",
                "--get-url",
                url
            ],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if result.returncode == 0 and result.stdout.strip():
            stream_url = result.stdout.strip().split('\n')[0]
            if stream_url.startswith('http'):
                print(f"✅ REAL STREAM")
                return stream_url
        else:
            # Fallback: try to get video info
            info_result = subprocess.run(
                [
                    "yt-dlp",
                    "-j",
                    "--no-warnings",
                    url
                ],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if info_result.returncode == 0:
                try:
                    info = json.loads(info_result.stdout)
                    # Try to find HLS format
                    if 'formats' in info:
                        for fmt in info['formats']:
                            if fmt.get('ext') == 'm3u8' or 'hls' in fmt.get('format_id', ''):
                                if 'url' in fmt:
                                    print(f"✅ HLS FORMAT")
                                    return fmt['url']
                    # Last resort: use direct URL
                    if 'url' in info:
                        print(f"✅ DIRECT URL")
                        return info['url']
                except:
                    pass
        
        print("⚠️ NO STREAM FOUND")
        return None
        
    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT")
        return None
    except FileNotFoundError:
        print("❌ yt-dlp not installed")
        return None
    except Exception as e:
        print(f"❌ {str(e)[:30]}")
        return None

def main():
    print("=" * 70)
    print("RUMBLE REAL STREAM EXTRACTION (yt-dlp)")
    print("=" * 70)
    print()
    
    streams = {}
    successful = 0
    
    for video_id, name in VIDEO_IDS.items():
        stream_url = extract_stream_with_ytdlp(video_id, name)
        if stream_url:
            streams[video_id] = stream_url
            successful += 1
    
    print()
    print(f"✅ Extracted {successful}/{len(VIDEO_IDS)} REAL streams")
    print()
    
    if streams:
        # Generate M3U with real URLs
        m3u = "#EXTM3U\n"
        for video_id, name in VIDEO_IDS.items():
            if video_id in streams:
                url = streams[video_id]
                m3u += f"#EXTINF:-1,{name}\n{url}\n"
        
        # Save both directories
        os.makedirs("generated_pages", exist_ok=True)
        os.makedirs("M3U_Matrix_Output", exist_ok=True)
        
        for path in ["generated_pages/rumble_real.m3u", "M3U_Matrix_Output/rumble_real.m3u"]:
            with open(path, 'w') as f:
                f.write(m3u)
            print(f"✅ Saved: {path}")
        
        print()
        print("=== FIRST 3 CHANNELS ===")
        for line in m3u.split('\n')[:6]:
            if line.strip():
                print(line[:80])
        print()
        print("✅ READY TO USE IN VLC OR WEB PLAYER")

if __name__ == "__main__":
    main()
