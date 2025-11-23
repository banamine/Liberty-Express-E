#!/usr/bin/env python3
import urllib.request
from pathlib import Path

REPLIT_URL = "http://localhost:5000"
LOCAL_DIR = r"C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE\Liberty-Express-"
PAGES = ["index.html", "demo.html", "m3u_scheduler.html", "calendar_demo.html", "interactive_hub.html", "file_manager.html", "large_playlist_handler.html", "internet_radio.html", "FILE_BROWSER_README.html", "minified_player.html", "local_minified_player.html", "simple_player.html", "multi_channel.html"]

pages_dir = Path(LOCAL_DIR) / "generated_pages"
pages_dir.mkdir(parents=True, exist_ok=True)

print("\n📥 Downloading pages...")
for page in PAGES:
    try:
        url = f"{REPLIT_URL}/{page}"
        output = pages_dir / page
        urllib.request.urlretrieve(url, output)
        print(f"✓ {page}")
    except Exception as e:
        print(f"✗ {page} - {e}")

print(f"\n✅ Done! Files in: {pages_dir}")