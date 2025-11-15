# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This is a dual-component project combining a **professional M3U playlist manager** (Python desktop app) with a **futuristic streaming TV player** (web interface). Together, they provide a complete IPTV solution for managing, organizing, and playing streaming content.

**Status:** Fully configured and running on Replit
**Last Updated:** November 12, 2025

## Project Components

### 1. M3U MATRIX PRO (Python Desktop Application)
A powerful Tkinter-based playlist management tool for organizing and validating M3U/M3U8 playlists.

**Main File:** `M3U_MATRIX_PRO.py`

**Features:**
- Drag & drop channel reordering
- Live channel validation (checks if URLs work)
- Smart playlist organization (remove duplicates, normalize groups)
- EPG/TV Guide integration with XMLTV support
- Cut/Copy/Paste channel operations
- CSV export for spreadsheet analysis
- Remote URL import
- Regex-powered search
- Inline editing
- Multi-file playlist merging
- Custom tag support

**How to Run:**
```bash
./run_m3u_matrix.sh
```
Or:
```bash
python3 M3U_MATRIX_PRO.py
```

**Directory Structure:**
- `logs/` - Application logs
- `exports/` - Saved M3U files and CSV exports
- `backups/` - Backup copies
- `thumbnails/` - Channel logo cache
- `epg_data/` - EPG XML data cache
- `temp/` - Temporary files

### 2. NEXUS TV (Web Streaming Player)
A sophisticated 24-hour streaming television channel with a futuristic neon cyberpunk interface.

**Main File:** `index.html`

**Features:**
- 24-hour auto-scheduled playback
- Neon cyberpunk UI with animations
- M3U playlist loading
- World timezone clocks
- Thumbnail carousel (previous/current/next programs)
- Fullscreen video player
- Volume controls
- Program schedule splash screen
- Midnight auto-refresh

**Access:** Via Replit webview on port 5000

## Project Structure

```
M3U_MATRIX_ALL_IN_ONE/
├── M3U_MATRIX_PRO.py           # Python playlist manager
├── run_m3u_matrix.sh           # Launch script for Python app
├── index.html                  # NEXUS TV web player (2036 lines)
├── manifest.json               # PWA manifest
├── service-worker.js           # Service worker for offline
├── M3U_MATRIX_README.md        # Detailed Python app docs
│
├── Sample Playlists/
│   ├── *.m3u                   # Various M3U playlist files
│   └── *.m3u8                  # HLS playlist files
│
├── Project Directories/
│   ├── logs/                   # M3U Matrix logs
│   ├── exports/                # Exported playlists
│   ├── backups/                # Backup files
│   ├── thumbnails/             # Logo cache
│   ├── epg_data/               # TV guide data
│   └── temp/                   # Temporary files
│
└── Configuration/
    ├── package.json            # Node.js dependencies
    ├── pyproject.toml          # Python dependencies
    ├── .gitignore              # Git ignore patterns
    └── .replit                 # Replit configuration
```

## Typical Workflow

### Complete Integrated Workflow (NEW!)
1. **Launch M3U Matrix Pro:** `./run_m3u_matrix.sh`
2. **Load playlists:** Click **LOAD** and select M3U files
3. **Organize:** Click **ORGANIZE** to clean and sort channels
4. **Validate:** Click **CHECK** to test channel URLs
5. **Generate Pages:** Click **GENERATE PAGES** button
   - Choose "Yes" to generate by group (creates separate channel for each category)
   - Choose "No" to create one mega-channel with all programs
6. **View Results:** Open browser to see channel selector
7. **Browse Channels:** Click any channel card to watch

### Managing Playlists with M3U Matrix Pro
1. Launch the Python app: `./run_m3u_matrix.sh`
2. Click **LOAD** and select M3U files
3. Click **ORGANIZE** to clean and sort channels
4. Click **CHECK** to validate channel URLs
5. Edit channels by double-clicking cells
6. Drag rows to reorder channels
7. Click **SAVE** to export organized playlist
8. Optionally **EXPORT CSV** for analysis

### Playing Content with NEXUS TV
1. Web server automatically runs on port 5000
2. Access via Replit webview to see channel selector
3. Click any channel card to open that channel
4. Splash screen shows daily schedule
5. Videos play automatically based on schedule
6. Fullscreen player with neon cyberpunk interface
7. Automatic midnight refresh for new schedule

## Technical Stack

### Python Application
- **Language:** Python 3.11
- **GUI:** Tkinter (native)
- **HTTP:** requests library
- **Images:** Pillow
- **Data:** JSON, CSV
- **Logging:** Python logging module

### Web Application
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Video:** Native HTML5 video element
- **Fonts:** Orbitron (Google Fonts)
- **Icons:** Font Awesome 6.4.0
- **Server:** Static file server (serve npm package)

## Running the Project

### Web Server (NEXUS TV)
The web server runs automatically:
```
npx serve -l 5000 --no-clipboard
```
Access via Replit webview.

### Python App (M3U Matrix Pro)
Launch manually when needed:
```bash
./run_m3u_matrix.sh
```

## Dependencies

### Python Packages (auto-installed)
- requests
- pillow

### Node Packages (auto-installed)
- serve

## Key Files Explained

### M3U_MATRIX_PRO.py
Complete Python application with:
- Tkinter UI builder
- M3U parser (handles EXTINF, EXTGRP, custom tags)
- Channel validator (checks HTTP/RTMP/RTSP URLs)
- EPG fetcher (XMLTV format support)
- Settings manager (JSON persistence)
- Logging system
- Error handling

### index.html
Self-contained web player with:
- Embedded CSS (neon cyberpunk theme)
- Embedded JavaScript (schedule engine, playlist parser)
- Video player with HLS/DASH support
- M3U playlist loader
- Timezone clock widget
- Responsive controls

### Sample M3U Files
Test playlists including:
- `Flux.m3u8` - Test streaming playlist
- `All Loonie Toons.m3u` - Classic cartoons
- `Ancient Aliens 1-18.m3u` - Documentary series
- And more...

## M3U Playlist Format

Both applications support standard M3U format:
```m3u
#EXTM3U
#EXTINF:-1 tvg-id="ch1" tvg-name="Channel 1" tvg-logo="http://logo.png" group-title="Movies",Channel 1
http://stream.url/video.m3u8
#EXTGRP:Movies
#CUSTOM-TAG:value
```

**Supported Tags:**
- `#EXTM3U` - Header
- `#EXTINF` - Channel information
- `#EXTGRP` - Group name
- `tvg-id` - EPG channel ID
- `tvg-name` - Display name
- `tvg-logo` - Logo URL
- `group-title` - Category
- Custom tags (preserved by M3U Matrix Pro)

## Recent Changes

### November 15, 2025 - Safe UX Improvements (Version 3)
**Non-Breaking Enhancements:**
- ✨ **Auto-Save System**: Automatic backups every 5 minutes to `backups/` folder
- 📊 **Progress Bars**: Visual feedback for CHECK and other long operations
- ⚠️ **Better Error Messages**: User-friendly dialogs with contextual suggestions
- 💾 **Exit Protection**: Prompts to save unsaved changes before closing
- 📝 **Change Tracking**: System monitors modifications to trigger autosave
- 🧠 **Smart Scheduler**: Added 4 intelligent scheduling modes (balanced, random, weighted, sequential)

**Files Modified:**
- `src/M3U_MATRIX_PRO.py`: 2,551 lines (+152 new features)
- New documentation: `IMPROVEMENTS_V3.md`

### November 13, 2025 - Enhanced File Management & GitHub Integration
**Major Update: Drag-and-Drop + GitHub Ready! 🚀**

**File Management Enhancements:**
- ✨ **Drag & Drop**: Drop M3U files directly into the app window
- 🖱️ **Double-Click**: Open files from list instantly
- 📋 **Copy/Paste**: Right-click menu with file operations
- 📁 **Open Location**: Quick access to file folders
- 🔄 **Auto-Load**: Dropped files load automatically

**GitHub Integration:**
- Created comprehensive README.md (400+ lines)
- Created GITHUB_SETUP.md with step-by-step guides
- Updated .gitignore for clean repository
- Created requirements.txt for easy dependency install
- Ready to push to GitHub and collaborate

**Page Generator Integration:**
- Created NexusTVPageGenerator class with M3U playlist injection
- Parses M3U playlists and extracts program metadata
- Generates 24-hour auto-scheduled playback system
- Creates professional NEXUS TV channel pages (74KB each)
- Generates beautiful channel selector with cyberpunk aesthetic
- Handles 100+ channels capability

**M3U Matrix Pro Updates:**
- Added "GENERATE PAGES" button to toolbar
- Integrated tkinterdnd2 for drag-and-drop support
- Enhanced file list with interactive features
- Improved threading for smooth UX
- Moved app to src/ directory for better organization

**Project Structure:**
- Reorganized: src/ (Python apps), templates/ (NEXUS TV template), generated_pages/ (output)
- Successfully generated 5 test channel pages from sample playlists
- Created channel selector index page (7.6K) with grid layout
- Each channel page includes full 24-hour schedule with auto-playback

**Documentation:**
- README.md: Complete project documentation
- GITHUB_SETUP.md: GitHub sync instructions
- requirements.txt: Python dependencies
- .gitignore: Clean repository setup

### November 12, 2025 - Complete Setup
**Web Player (NEXUS TV):**
- Deployed complete NEXUS TV template (2036 lines)
- Configured static file server on port 5000
- Set up PWA manifest and service worker
- Updated .gitignore for Node.js

**Python App (M3U Matrix Pro):**
- Created complete M3U_MATRIX_PRO.py (45KB, 1000+ lines)
- Set up directory structure (logs, exports, backups, etc.)
- Installed Python 3.11 and dependencies (requests, pillow)
- Created launcher script (run_m3u_matrix.sh)
- Updated .gitignore for Python
- Created comprehensive README (M3U_MATRIX_README.md)

## User Preferences
None recorded yet.

## Deployment

### Web Player
Configured for Replit Autoscale deployment:
- Stateless architecture
- All assets embedded in single HTML
- No database required
- Production-ready static server

### Python App
Desktop application:
- Runs locally in Replit environment
- Requires X11/GUI support (Replit provides VNC)
- Settings persist to JSON files
- Logs to `logs/` directory

## Future Development Plans

### Phase 1: Dynamic Page Generation (Next)
- Python script to inject playlists into NEXUS TV template
- Generate 100+ individual channel pages
- Create channel selector/splash page
- Automated playlist-to-page pipeline

### Phase 2: Integration
- M3U Matrix Pro exports → NEXUS TV imports
- Unified launcher
- Cross-application playlist sync
- Web-based playlist manager

### Phase 3: Advanced Features
- Recording/timeshift capabilities
- Multi-channel support in NEXUS TV
- Cloud playlist sync
- Auto-update broken channels
- User authentication
- Custom themes

## Troubleshooting

### Python App Won't Start
- Ensure in Replit environment with Python 3.11
- Check `logs/m3u_matrix.log` for errors
- Verify dependencies: `python3 -m pip list`

### Web Player Issues
- Check Web Server workflow is running
- Verify port 5000 is accessible
- Clear browser cache and reload
- Check browser console for JavaScript errors

### Playlist Loading Issues
- Verify M3U format is valid
- Check file encoding (UTF-8 recommended)
- Test URLs in standalone player
- Review parser error messages

## Documentation

- **M3U_MATRIX_README.md** - Comprehensive Python app guide
- **LICENSE** - Project license
- **replit.md** - This file (project overview)

## Notes

- Both apps can run simultaneously
- M3U Matrix Pro for organization, NEXUS TV for playback
- Settings are persisted locally
- Logs help with debugging
- Sample M3U files included for testing

---

**M3U MATRIX ALL-IN-ONE** - Professional IPTV Management & Streaming Platform
