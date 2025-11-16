VIDEO PLAYER PRO - Standalone Python Application
================================================

DESCRIPTION:
Advanced video player application with playlist management, scheduling,
and metadata extraction capabilities.

FEATURES:
✓ Advanced Video Playback (uses system default player)
✓ Smart Scheduling System with time predictions
✓ Screenshot & Metadata Capture with JSON export
✓ Playlist Management with copy/paste support
✓ Video Metadata Extraction (duration, resolution, codec, file size)
✓ Automatic Thumbnail Generation
✓ Folder scanning for batch video import
✓ Schedule export and visualization

REQUIREMENTS:
- Python 3.7+
- FFmpeg (for video metadata extraction and screenshots)
- Pillow (PIL) - for image/thumbnail processing
- tkinterdnd2 (optional - for drag & drop support)

INSTALLATION:

1. Install Python dependencies:
   pip install pillow

2. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: sudo apt install ffmpeg
   - macOS: brew install ffmpeg

USAGE:

1. Run the application:
   python run_player.py
   
   or
   
   python main_launcher.py

2. Click "LAUNCH PLAYER" to open the workbench

3. Add videos:
   - Click blue "📂 Load" button for advanced import
   - File menu > Open Video(s)
   - File menu > Open Folder
   - Drag and drop support (if tkinterdnd2 installed)

3a. Advanced Import with "Load" button:
   - Supports M3U/M3U8 playlists
   - Supports TXT files with URL extraction
   - Supports video/audio files directly
   - Supports folder scanning (recursive)
   - Automatically extracts URLs from any text file

4. Playback:
   - Double-click a video in the playlist to play
   - Use Previous/Next buttons for navigation
   - Videos play in system default player

5. Screenshots:
   - Click "Screenshot" button while video is selected
   - Screenshots saved to: screenshots/ folder
   - Includes JSON metadata and thumbnail

6. Scheduling:
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

NOTES:
- Videos are played using the system's default video player
- FFmpeg must be installed for metadata extraction and screenshots
- All data is stored locally in the application folder
- Playlist auto-saves on changes

TROUBLESHOOTING:
- If metadata extraction fails, ensure FFmpeg is installed and in PATH
- If screenshots don't work, check FFmpeg installation
- For playback issues, check your system's default video player settings
