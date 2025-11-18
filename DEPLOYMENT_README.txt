================================================================================
                   M3U MATRIX ALL-IN-ONE PLATFORM
                     DEPLOYMENT & SETUP GUIDE
================================================================================

Version: Latest Build
Date: November 2025
Platform: Windows, macOS, Linux

Welcome! This package contains everything you need to run the M3U Matrix
platform on your PC.


================================================================================
SYSTEM REQUIREMENTS
================================================================================

Minimum Requirements:
  - Python 3.11 or higher
  - 2GB RAM
  - 500MB disk space
  - Windows 10/11, macOS 10.15+, or Linux

Optional (for advanced features):
  - FFmpeg (for video duration extraction)
  - VLC Media Player (for Video Player Pro)


================================================================================
QUICK START (Windows)
================================================================================

OPTION 1: Automated Installation (Easiest)
--------------------------------------------------------------------------------
1. Extract this ZIP to any folder (e.g., C:\M3U_MATRIX\)
2. Double-click: QUICK_INSTALL.bat
3. Wait for dependencies to install
4. The application will launch automatically!

OPTION 2: Manual Installation
--------------------------------------------------------------------------------
1. Install Python from: https://www.python.org/downloads/
   ⚠️ IMPORTANT: Check "Add Python to PATH" during installation!

2. Open Command Prompt in the extracted folder:
   - Hold Shift + Right-click in the folder
   - Select "Open PowerShell window here" or "Command Prompt"

3. Install dependencies:
   pip install -r requirements.txt

4. Run the application:
   python src\videos\M3U_MATRIX_PRO.py

   Or double-click: run_windows.bat


================================================================================
QUICK START (macOS / Linux)
================================================================================

1. Install Python 3.11+:
   macOS: brew install python@3.11
   Linux: sudo apt install python3.11

2. Open Terminal in the extracted folder

3. Make the script executable:
   chmod +x src/run_m3u_matrix.sh

4. Install dependencies:
   pip3 install -r requirements.txt

5. Run the application:
   python3 src/videos/M3U_MATRIX_PRO.py

   Or: ./src/run_m3u_matrix.sh


================================================================================
FOLDER STRUCTURE
================================================================================

After extraction, you should see:

M3U_MATRIX/
├── src/
│   ├── videos/
│   │   └── M3U_MATRIX_PRO.py      ← Main application (run this!)
│   ├── video_player_app/
│   │   └── run_player.py           ← Video Player Pro
│   ├── page_generator.py           ← Web page generator
│   └── utils.py                    ← Utility functions
│
├── templates/
│   ├── nexus_tv_template.html      ← NEXUS TV player
│   ├── buffer_tv_template.html     ← Buffer TV player
│   ├── multi_channel_template.html ← Multi-Channel viewer
│   ├── rumble_channel_template.html← Rumble player
│   ├── web-iptv-extension/         ← Web IPTV player
│   └── simple-player/              ← Simple player
│
├── generated_pages/
│   └── index.html                  ← Navigation Hub
│
├── START_WEB_SERVER.bat            ← Start web server (Windows)
├── START_WEB_SERVER.py             ← Start web server (cross-platform)
├── QUICK_INSTALL.bat               ← Automated setup (Windows)
├── run_windows.bat                 ← Run M3U Matrix Pro (Windows)
├── requirements.txt                ← Python dependencies
├── AUDIT_REPORT.txt                ← Project audit
└── DEPLOYMENT_README.txt           ← This file


================================================================================
USING THE APPLICATION
================================================================================

1. M3U MATRIX PRO (Desktop Application)
--------------------------------------------------------------------------------
This is the main playlist management tool.

To launch:
  Windows:  Double-click run_windows.bat
            OR: python src\videos\M3U_MATRIX_PRO.py
  
  macOS/Linux: python3 src/videos/M3U_MATRIX_PRO.py

Features:
  ✓ Load and edit M3U/M3U8 playlists
  ✓ Import from URLs
  ✓ Organize channels by groups
  ✓ Validate channel URLs
  ✓ Generate 6 types of web players
  ✓ Smart TV scheduling
  ✓ EPG/TV Guide integration
  ✓ Rumble video support
  ✓ Export to JSON, Redis, and more


2. WEB PLAYERS (Browser-based)
--------------------------------------------------------------------------------
After generating pages in M3U Matrix Pro, view them in your browser:

Step 1: Start the web server
  Windows:  Double-click START_WEB_SERVER.bat
  All:      python START_WEB_SERVER.py

Step 2: Open browser
  Navigate to: http://localhost:5000/

Step 3: Access Navigation Hub
  Click the Navigation Hub link to see all your generated pages

Available Players:
  • NEXUS TV - 24-hour scheduled playback, cyberpunk design
  • Buffer TV - TV player with numeric keypad
  • Multi-Channel - Watch up to 6 channels simultaneously
  • Web IPTV - Full-featured IPTV player
  • Simple Player - Clean, minimalist interface
  • Rumble Channel - Dedicated Rumble video player


3. VIDEO PLAYER PRO (Standalone Video App)
--------------------------------------------------------------------------------
Advanced video player with scheduling and metadata extraction.

To launch:
  python src/video_player_app/run_player.py

Features:
  ✓ Universal file import (M3U, video files, folders)
  ✓ FFmpeg metadata extraction
  ✓ Screenshot capture with thumbnails
  ✓ Advanced scheduling system
  ✓ Auto-save playlists
  ✓ VLC player integration


================================================================================
TROUBLESHOOTING
================================================================================

Problem: "python not recognized" or "pip not found"
Solution:
  - Reinstall Python and check "Add Python to PATH"
  - Or use full path: C:\Python311\python.exe

Problem: "Module not found" errors
Solution:
  - Run: pip install -r requirements.txt
  - Make sure you're in the correct folder

Problem: "Page generator not available" in M3U Matrix Pro
Solution:
  - Make sure you extracted the ENTIRE ZIP, not just the .py file
  - page_generator.py must be in the src/ folder
  - Run from the root folder, not from inside src/

Problem: Web pages won't load
Solution:
  - Make sure START_WEB_SERVER.bat is running
  - Don't double-click HTML files directly
  - Always use http://localhost:5000/

Problem: Port 5000 already in use
Solution:
  - Edit START_WEB_SERVER.py
  - Change: PORT = 5000 to PORT = 8000
  - Use http://localhost:8000/ instead

Problem: Videos won't play in web browser
Solution:
  - Check if the stream URL is valid
  - Try a different browser (Chrome recommended)
  - Check your internet connection for remote streams

Problem: FFmpeg errors in Video Player Pro
Solution:
  - Install FFmpeg from: https://ffmpeg.org/download.html
  - Add FFmpeg to system PATH
  - Restart the application


================================================================================
DEPENDENCIES
================================================================================

Python Packages (auto-installed with pip install -r requirements.txt):
  - tkinterdnd2 (drag & drop support)
  - requests (HTTP requests)
  - Pillow (image processing)

Optional External Tools:
  - FFmpeg (video processing) - https://ffmpeg.org/
  - VLC Media Player - https://www.videolan.org/

Web Server:
  - Node.js serve (optional, included as Python alternative)


================================================================================
CONFIGURATION
================================================================================

Settings are saved automatically in:
  - src/config.json (M3U Matrix Pro settings)
  - src/video_player_app/data/ (Video Player Pro data)

Generated pages are saved to:
  - generated_pages/nexus_tv/
  - generated_pages/buffer_tv/
  - generated_pages/multi_channel/
  - generated_pages/web_iptv/
  - generated_pages/simple_player/
  - generated_pages/rumble_channel/


================================================================================
GETTING STARTED WORKFLOW
================================================================================

Complete Beginner's Guide:

STEP 1: Installation
  1. Extract this ZIP to a folder (e.g., C:\M3U_MATRIX\)
  2. Double-click QUICK_INSTALL.bat (Windows)
     OR run: pip install -r requirements.txt

STEP 2: Run M3U Matrix Pro
  1. Double-click run_windows.bat
     OR run: python src\videos\M3U_MATRIX_PRO.py
  2. The desktop application opens

STEP 3: Load a Playlist
  1. Click "LOAD" button
  2. Select an M3U/M3U8 file
     OR click "URL IMPORT" to load from a URL
  3. Your channels appear in the list

STEP 4: Generate a Web Player
  1. Click "NEXUS TV" (or any other player button)
  2. Enter a page name (e.g., "my_channels")
  3. Click OK
  4. Page is generated in generated_pages/ folder

STEP 5: View in Browser
  1. Double-click START_WEB_SERVER.bat
  2. Open browser to: http://localhost:5000/
  3. Click on your generated page
  4. Enjoy streaming!


================================================================================
ADVANCED FEATURES
================================================================================

Smart TV Scheduler:
  - Click "SMART SCHEDULE" in M3U Matrix Pro
  - Configure 7-day rotating schedule
  - Generate time-based playlists

Rumble Video Support:
  - Import Rumble URLs directly
  - Automatic metadata fetching
  - Dedicated Rumble player template

Multi-Channel Viewer:
  - Watch up to 6 channels simultaneously
  - Smart audio management (one audio at a time)
  - Configurable rotation intervals

Navigation Hub:
  - Central page for all generated players
  - Statistics dashboard
  - Bookmarks export
  - Auto-cleanup for old pages


================================================================================
SUPPORT & DOCUMENTATION
================================================================================

Documentation Files:
  - AUDIT_REPORT.txt - Complete project audit
  - replit.md - Full technical documentation
  - src/M3U_MATRIX_README.md - Core features guide

Feature Guides:
  - TIMESTAMP_GENERATOR.md - Video timestamping
  - THUMBNAIL_CACHING_GUIDE.md - Thumbnail system
  - templates/SIMPLE_PLAYER_USAGE.txt - Simple player guide

For issues or questions:
  - Check AUDIT_REPORT.txt for known issues
  - Review troubleshooting section above
  - Check individual template README files


================================================================================
LICENSE & COPYRIGHT
================================================================================

See LICENSE file for full license information.

This project includes:
  - HLS.js (Apache License 2.0)
  - DASH.js (BSD License)
  - Feather Icons (MIT License)


================================================================================
VERSION HISTORY
================================================================================

Latest Build:
  ✓ Navigation Hub system with splash screen
  ✓ Organized folder structure for generated pages
  ✓ "Back to Hub" button in all templates
  ✓ Bug fixes for file:// protocol compatibility
  ✓ Sample channels library (10 demo videos)
  ✓ Bookmarks export functionality
  ✓ Auto-cleanup system
  ✓ Complete audit report

Previous Features:
  ✓ 6 web player templates
  ✓ M3U Matrix Pro desktop application
  ✓ Video Player Pro standalone app
  ✓ Smart TV Scheduler
  ✓ Rumble integration
  ✓ EPG/TV Guide support
  ✓ Redis export
  ✓ Auto-thumbnail system


================================================================================
THANK YOU FOR USING M3U MATRIX!
================================================================================

Enjoy your personalized IPTV experience!

For updates and more information, check the project repository.

================================================================================
