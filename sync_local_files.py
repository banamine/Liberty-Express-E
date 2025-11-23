#!/usr/bin/env python3
"""
ScheduleFlow Local Sync Tool
Sync generated pages from Replit to your local machine
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Configuration
REPLIT_URL = "http://localhost:5000"  # Change if deployed
LOCAL_DIR = Path.home() / "Videos" / "ScheduleFlow"  # Change as needed
PAGES_TO_SYNC = [
    "index.html",
    "demo.html",
    "m3u_scheduler.html",
    "calendar_demo.html",
    "interactive_hub.html",
    "file_manager.html",
    "large_playlist_handler.html",
    "internet_radio.html",
    "FILE_BROWSER_README.html",
    "minified_player.html",
    "local_minified_player.html",
    "simple_player.html",
    "multi_channel.html",
]

def download_file(url: str, output_path: Path) -> bool:
    """Download a file from URL to local path"""
    try:
        print(f"  Downloading: {url}")
        urllib.request.urlretrieve(url, output_path)
        size = output_path.stat().st_size / 1024  # KB
        print(f"  ✓ Saved: {output_path.name} ({size:.1f} KB)")
        return True
    except urllib.error.URLError as e:
        print(f"  ✗ Failed: {url} - {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def sync_pages():
    """Download all pages from Replit"""
    print("\n" + "="*60)
    print("📥 ScheduleFlow Local Sync")
    print("="*60)
    
    # Create directories
    pages_dir = LOCAL_DIR / "generated_pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Target Directory: {pages_dir}")
    
    # Download each page
    print(f"\n🔄 Syncing {len(PAGES_TO_SYNC)} pages...")
    success_count = 0
    
    for page in PAGES_TO_SYNC:
        url = f"{REPLIT_URL}/{page}"
        output = pages_dir / page
        
        if download_file(url, output):
            success_count += 1
    
    print(f"\n✓ Synced {success_count}/{len(PAGES_TO_SYNC)} pages")
    
    return pages_dir

def create_offline_index(pages_dir: Path):
    """Create an offline index file"""
    print("\n📋 Creating offline index...")
    
    index_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>ScheduleFlow - Offline Index</title>
    <meta charset="UTF-8">
    <style>
        body {{ background: #000; color: #00ff00; font-family: monospace; padding: 20px; }}
        h1 {{ color: #ffff00; }}
        a {{ color: #00ff00; text-decoration: none; }}
        a:hover {{ color: #ffff00; }}
        .file-list {{ background: #1a1a1a; padding: 15px; border-radius: 6px; margin: 20px 0; }}
        .file-item {{ padding: 8px; margin: 5px 0; background: #000; border-left: 3px solid #ffff00; }}
    </style>
</head>
<body>
    <h1>🎬 ScheduleFlow - Offline Access</h1>
    <p>Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>📺 Players & Tools</h2>
    <div class="file-list">
        <div class="file-item"><a href="index.html">🏠 Main Dashboard</a></div>
        <div class="file-item"><a href="demo.html">▶️ Demo Player</a></div>
        <div class="file-item"><a href="m3u_scheduler.html">📅 M3U Scheduler</a></div>
        <div class="file-item"><a href="internet_radio.html">🎙️ Internet Radio</a></div>
        <div class="file-item"><a href="calendar_demo.html">📆 Calendar</a></div>
        <div class="file-item"><a href="interactive_hub.html">🎮 Hub</a></div>
        <div class="file-item"><a href="file_manager.html">📁 File Manager</a></div>
        <div class="file-item"><a href="large_playlist_handler.html">📊 Large Playlists</a></div>
    </div>
    
    <h2>📝 Documentation</h2>
    <div class="file-list">
        <div class="file-item"><a href="FILE_BROWSER_README.html">📋 File Browser</a></div>
    </div>
    
    <h2>💾 How to Use</h2>
    <pre>1. Open index.html in your browser (no server needed!)
2. All pages work offline
3. Load local M3U files or paste URLs
4. Use internet_radio.html for music scheduling
5. Schedule content with m3u_scheduler.html</pre>
    
    <hr style="border-color: #00ff00;">
    <p style="color: #888; font-size: 0.9em;">Synced from ScheduleFlow Replit Project</p>
</body>
</html>
"""
    
    index_file = pages_dir.parent / "OFFLINE_INDEX.html"
    with open(index_file, 'w') as f:
        f.write(index_content)
    
    print(f"✓ Created: {index_file.name}")

def create_git_commands(pages_dir: Path):
    """Generate Git commands to push to GitHub"""
    print("\n📤 Git Commands (Optional)")
    print("="*60)
    print("\nTo push to GitHub:")
    print(f"  cd {pages_dir.parent}")
    print("  git add generated_pages/")
    print(f'  git commit -m "Update: Generated pages - {datetime.now().strftime("%Y-%m-%d %H:%M")}"')
    print("  git push origin main")
    print("\nTo clone on another machine:")
    print("  git clone <your-repo-url>")
    print("  cd <repo-name>")
    print("  # Then open generated_pages/OFFLINE_INDEX.html in browser")

def main():
    """Main sync function"""
    try:
        # Test connection
        print("🔌 Testing connection to Replit...")
        try:
            urllib.request.urlopen(f"{REPLIT_URL}/index.html", timeout=5)
            print("✓ Connected!")
        except:
            print(f"✗ Could not connect to {REPLIT_URL}")
            print("\n💡 Make sure Replit servers are running:")
            print("   - Node.js API Server on port 5000")
            print("   - Python FastAPI Server on port 5001")
            print("\nOr update REPLIT_URL in this script for deployed version")
            sys.exit(1)
        
        # Sync pages
        pages_dir = sync_pages()
        
        # Create offline index
        create_offline_index(pages_dir)
        
        # Show Git commands
        create_git_commands(pages_dir)
        
        print("\n" + "="*60)
        print("✅ Sync Complete!")
        print("="*60)
        print(f"\n📂 Files saved to: {pages_dir}")
        print(f"\n🌐 Open offline: {pages_dir.parent / 'OFFLINE_INDEX.html'}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Sync cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
