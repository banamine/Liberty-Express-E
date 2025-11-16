VIDEO PLAYER PRO - VLC EMBEDDED EDITION
=========================================

DESCRIPTION:
Advanced video player with EMBEDDED VLC VIDEO PLAYBACK, intelligent scheduling,
live screenshot capture, and real-time video information display.

✨ NEW: EMBEDDED VLC PLAYER ✨
Videos now play INSIDE the application window with full playback controls!

KEY FEATURES:
✓ Embedded VLC Video Player - Watch videos directly in the app
✓ Live Screenshot Capture - Capture exact frame at current playback position
✓ Real-Time Video Info - See codec, resolution, bitrate while playing
✓ Time-Stamping - All screenshots include exact playback timestamp
✓ Smart Scheduling System with time predictions
✓ Playlist Management with copy/paste support
✓ Video Metadata Extraction (duration, resolution, codec, file size)
✓ Automatic Thumbnail Generation
✓ Folder scanning for batch video import
✓ Auto-Advance - Automatically plays next video when current ends
✓ Universal Import - Accepts ANY file type and extracts URLs/content

REQUIREMENTS:

REQUIRED:
- Python 3.7+
- VLC Media Player (for embedded video playback)
- python-vlc (installed automatically via pip)
- FFmpeg (for metadata extraction)
- Pillow (PIL) - for image/thumbnail processing

INSTALLATION:

1. Install VLC Media Player (REQUIRED for embedded playback):

   Windows:
   - Download from: https://www.videolan.org/vlc/
   - Install VLC (64-bit recommended)
   - VLC libraries will be auto-detected

   Mac:
   - Download VLC.app from videolan.org, OR
   - Install via Homebrew: brew install --cask vlc

   Linux:
   - Ubuntu/Debian: sudo apt install vlc
   - Fedora: sudo dnf install vlc
   - Arch: sudo pacman -S vlc

2. Install Python dependencies:
   pip install python-vlc Pillow

3. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - Mac: brew install ffmpeg
   - Linux: sudo apt install ffmpeg

USAGE:

1. Run the application:
   python run_player.py
   
   or
   
   python main_launcher.py

2. Click "LAUNCH PLAYER" to open the workbench

3. Add videos:
   - Click blue "📂 Load" button (FIRST BUTTON) for universal import
   - File menu > Open Video(s)
   - File menu > Open Folder

4. Universal Import with "📂 Load" button:
   - ACCEPTS ANY FILE TYPE
   - Automatically extracts URLs from TXT, HTML, XML, JSON, LOG files
   - Supports M3U/M3U8 playlists (including non-standard formats)
   - Supports video/audio files (MP4, MKV, AVI, MP3, WAV, etc.)
   - Supports folder scanning (recursive search)
   - Extracts: HTTP, HTTPS, RTMP, RTSP, file:// URLs, Windows paths

5. Playback (EMBEDDED VLC MODE):
   - Double-click a video in the playlist to play
   - Video plays INSIDE the app window
   - Use Play/Pause button to control playback
   - Use Previous/Next buttons for navigation
   - See real-time playback position and video info

6. Screenshots (LIVE CAPTURE):
   - Click "📸 Screenshot" button while video is playing
   - Captures exact frame at current playback position
   - Screenshots saved to: screenshots/ folder
   - Includes JSON metadata with playback time and position
   - Auto-generates thumbnail

7. Scheduling:
   - Schedule menu > Generate Schedule
   - Set start time and show duration
   - View/Export schedule as JSON

FILE OPERATIONS:
- Copy/Paste: Select videos and use Ctrl+C / Ctrl+V
- Delete: Select videos and press Delete key
- Save/Load: File menu > Save/Load Playlist (JSON format)

DATA STORAGE:
- screenshots/: Screenshots, thumbnails, and metadata
- data/: Playlist auto-save and application data

KEYBOARD SHORTCUTS:
- Ctrl+O: Open videos
- Ctrl+C: Copy selected videos
- Ctrl+V: Paste videos
- Delete: Remove selected videos

VLC EMBEDDED MODE vs FALLBACK MODE:

EMBEDDED MODE (VLC Installed):
✓ Videos play inside the app window
✓ Live screenshot capture at exact playback position
✓ Real-time codec/resolution/bitrate display
✓ Accurate time-stamping with playback position
✓ Full playback controls (play/pause/seek)
✓ Auto-advance to next video

FALLBACK MODE (No VLC):
- Videos open in external system player
- Screenshots use FFmpeg (5-second default position)
- Basic metadata display only
- Limited playback control

NOTES:
- For best experience, install VLC Media Player
- python-vlc is installed automatically via pip
- FFmpeg is required for metadata extraction
- All data is stored locally in the application folder
- Playlist auto-saves on changes

TROUBLESHOOTING:

"VLC Not Available" message on startup:
- Install VLC Media Player from videolan.org
- Restart the application

Metadata extraction fails:
- Ensure FFmpeg is installed and in PATH

Screenshot capture not working:
- VLC mode: Ensure VLC is installed and video is playing
- Fallback mode: Check FFmpeg installation

Video not playing:
- VLC mode: Check VLC installation
- Fallback mode: Check system default video player settings
