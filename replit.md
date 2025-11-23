# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade playout scheduler for 24/7 broadcasting, designed for various applications including campus TV stations, hotels, YouTube live channels, and local broadcasters. Its primary purpose is to provide unattended, continuous video content delivery through intelligent drag-and-drop scheduling, an auto-filler system, category balancing, and multi-week planning with recurring events. The system includes a REST API for remote control and a web-based dashboard, offering professional export capabilities to industry-standard playout engines (e.g., CasparCG, OBS, vMix).

## User Preferences
- **Communication Style:** Please use clear, simple language and avoid overly technical jargon where possible.
- **Workflow:** I prefer an iterative development approach. Please propose changes and discuss them with me before implementing major modifications.
- **Interaction:** Ask for my approval before making any significant changes to the project structure or core functionalities. Provide detailed explanations for proposed solutions or complex logic.
- **Codebase Changes:**
    - Do not make changes to the `Sample Playlists/` folder.
    - Do not make changes to the `M3U_MATRIX_README.md` file.
    - Ensure all changes are well-documented within the code.
- **Code Audit:** Under-claim, never hallucinate. Verify before claiming functionality works.
- **Documentation Discipline:** **UPDATE DOCUMENTATION WITH EVERY EDIT GOING FORWARD.** This file (replit.md) must reflect current state at all times.

## Week 1: Modularization + API Layer (✅ COMPLETE - Nov 23, 2025)

**DELIVERED:**
- ✅ **Modular Architecture:** Split monolithic M3U_MATRIX_PRO.py into:
  - `src/core/models.py` - Data structures (Channel, Schedule, ScheduleEntry, ValidationResult)
  - `src/core/scheduler.py` - Scheduling engine (intelligent playlist rotation)
  - `src/core/file_handler.py` - M3U parsing and file operations
  - `src/core/validator.py` - Channel validation with HTTP checks
  - `src/core/__init__.py` - Clean public API

- ✅ **FastAPI Server (Port 3000):**
  - GET `/api/system-version` - Version info
  - GET `/api/status` - Application status
  - GET `/api/channels` - List channels
  - POST `/api/channels` - Add channel
  - POST `/api/channels/import` - Import M3U file
  - GET/POST `/api/schedule` - Schedule management
  - POST `/api/schedule/create` - Generate intelligent schedule
  - POST `/api/validate` - Start channel validation (async)
  - GET `/api/validate/results` - Validation results
  - POST `/api/export/m3u` - Export to M3U format
  - Full Swagger docs at http://localhost:3000/docs

- ✅ **Communication Layer:** Node.js API (port 5000) now proxies to FastAPI (port 3000)
  - Single source of truth in Python
  - Clean separation of concerns
  - REST API fully operational
  - Verified working: `GET /api/system-version` returns 200 ✓

**WORKFLOWS:**
- `ScheduleFlow API Server` (port 5000, Node.js) - RUNNING ✓
- `ScheduleFlow FastAPI Server` (port 3000, Python) - RUNNING ✓

**DEPENDENCIES ADDED:**
- fastapi>=0.104.0
- uvicorn>=0.24.0
- pydantic>=2.0.0
- axios (Node.js)

## Week 2: File Management (✅ COMPLETE - Nov 23, 2025)

**DELIVERED:**
- ✅ **File Versioning System** (`src/core/versioning.py`):
  - Track M3U file changes with version history
  - SHA256 content hashing to prevent duplicate versions
  - Version rollback to any previous state
  - Diff generation between two versions
  - Automatic cleanup of old versions (keep N most recent)

- ✅ **Backup Manager** (`src/core/backup.py`):
  - Automated compressed backups (gzip format)
  - Configurable retention policy (default: 30 days)
  - Manual backup creation and restoration
  - Backup statistics (total size, count, oldest/newest)
  - Automatic cleanup of expired backups

- ✅ **Cross-Platform Path Handling** (`src/core/paths.py`):
  - Windows, macOS, Linux path compatibility
  - Platform-specific app data directory (AppData, ~/Library, ~/.local)
  - Platform-specific cache directory
  - Safe path operations (prevent directory traversal)
  - Platform info detection

- ✅ **FastAPI Endpoints (10 new endpoints)**:
  - **Versioning:** POST/GET `/api/versions/*` - create, list, restore, diff
  - **Backups:** POST/GET/DELETE `/api/backup/*` - create, list, restore, cleanup
  - **Platform:** GET `/api/platform/info` - system info and directories

**WORKFLOWS:**
- Both servers restart successfully with new modules ✓
- All endpoints tested and responding ✓

**NEXT STEPS (Week 3-4):**
- Week 3: Media Stripper overhaul (Selenium, robots.txt, retry logic)
- Week 4: UX improvements (wizard, progress bar, help tooltips)

## GitHub & Updates Status (Phase 1 vs 2)

**Phase 1 (Current):** ✅ READY
- GET /api/system-version - Check current version (2.0.0)
- GitHub repo for code storage
- GitHub Actions for CI/CD

**Phase 2 (Complete):** ✅ ENDPOINTS + DASHBOARD DONE
- GET /api/version-check - Check for available updates ✅
- POST /api/update-from-github - Admin can trigger updates ✅
- Admin dashboard UI for non-devs ✅ (admin-update-panel.html)
- Auto-update webhook for zero-downtime deployments (Phase 2.1)

**For Non-Developers:** Dashboard button to check/install updates. Still uses API key auth.  
**Access:** http://your-app/admin-update-panel  
**See:** PHASE_2_COMPLETION_SUMMARY.md for complete Phase 2 details.

## Media Stripper (NEW)

**What It Is:** Private media extraction tool that scans any website and creates playable .m3u playlists

**How It Works:**
1. User provides any website URL
2. Stripper silently scans the page (like F12 → Network or Elements)
3. Extracts all media files: .mp4, .m3u8, .m3u, .ts, .mp3, .mkv, .webm, .aac, etc.
4. Also extracts subtitles: .vtt, .srt, .ass
5. Saves `MASTER_PLAYLIST.m3u` with all links
6. Saves subtitles to `stripped_media/` folder

**Features:**
- ✅ 100% offline after initial scan (no background calling home)
- ✅ Zero logging/telemetry (completely private)
- ✅ Extracts from HTML tags, JavaScript, blob URLs
- ✅ Works with any website (video sites, streaming services, etc.)
- ✅ Supports direct files (.mp4) and streaming (.m3u8)
- ✅ Progress tracking in UI
- ✅ One-click folder open

**Access:** `MEDIA STRIPPER` button in M3U Matrix Pro GUI (Row 3, magenta color)

**Output:** `stripped_media/MASTER_PLAYLIST.m3u` (playable in VLC, MPC-HC, any player)

## System Architecture: Hub-and-Spoke Model

### Core Truth: M3U_MATRIX_PRO.py Is The Central Hub
M3U_MATRIX_PRO.py is the **singular source of truth** for all system state and operations. It's the "heart under the hood" that wires the entire project together. It can operate in two modes:

**Mode 1: Advanced Mode (GUI)**
- Tkinter interface for direct user interaction
- Content creators, developers, and power users
- Visual feedback, real-time editing
- Full feature access

**Mode 2: Silent Background Mode (Daemon)**
- Headless operation (no GUI window)
- Controlled via REST API, Control Dashboard, Numeric Keypad
- 24/7 broadcast operations, non-developer operators
- Lightweight, scriptable, automation-ready

### Wiring Diagram: How Components Connect
```
M3U_MATRIX_PRO.py (Hub)
    ├─ Input: GUI (Advanced) / API (Silent) / Keypad / Dashboard
    ├─ Processing: M3U parsing, scheduling, exports
    ├─ State: JSON configs, M3U files
    └─ Output: Generated pages, API responses, file updates
         ↓
    Consumer Applications
         ├─ scheduleflow_carousel.html (video playback)
         ├─ NEXUS TV, Buffer TV, etc. (players)
         ├─ api_server.js (REST endpoints)
         └─ Control Dashboard (operator UI)
```

All commands flow through M3U_MATRIX_PRO.py's methods. Whether via GUI click, API call, keypad press, or scheduled task, the system always updates through the central hub, ensuring consistency and single point of truth for all state.

### How to Run Each Mode

**Advanced Mode (GUI):**
```bash
python src/videos/M3U_MATRIX_PRO.py
# or simply double-click M3U_MATRIX_PRO.py (desktop)
```
- Tkinter window opens
- Direct visual control
- For: Content creators, developers, power users

**Silent Background Mode (Daemon):**
```bash
python src/videos/M3U_MATRIX_PRO.py --headless
# or as background service: nohup python src/videos/M3U_MATRIX_PRO.py --headless &
```
- No GUI window
- 24/7 continuous operation
- Controlled via REST API, web dashboard, numeric keypad
- For: Broadcast centers, automated operations, non-technical operators
- Logging: `src/videos/logs/m3u_matrix.log`

**Help:**
```bash
python src/videos/M3U_MATRIX_PRO.py --help
```

See `HEADLESS_MODE_IMPLEMENTATION.md` for complete technical details.

### UI/UX Decisions
The project incorporates a modern design for ScheduleFlow with a professional blue accent. Other components feature diverse aesthetics, including a neon cyberpunk theme for NEXUS TV, a minimalist UI for Simple Player, a purple gradient for Rumble Channel, a grid-based viewer for Multi-Channel Viewer, and a blue-to-red gradient with a numeric keypad and TV Guide overlay for Buffer TV. The Interactive Hub uses bubble navigation for managing playlists, schedules, and exports.

### Technical Implementations
Core scheduling logic includes intelligent drag-and-drop, auto-filling, category balancing, multi-week planning, and recurring events. Video playback is handled by native HTML5 video, HLS.js, and DASH.js. Data persistence uses `localStorage` for client-side and JSON files for server-side. Video validation includes HTTP 200 checks, FFprobe metadata, and HLS segment validation. Lazy loading is implemented for resource efficiency. The system features automated GitHub Pages deployment and a production-ready validation engine for imports and exports, covering schema validation, UTC timestamp parsing, duplicate detection (MD5), and conflict detection. A 48-hour cooldown enforces unique video plays.

### Feature Specifications
ScheduleFlow offers M3U parsing, channel validation, EPG fetching, settings management, and NDI Output Control Center integration. **NEW: Private Media Stripper** extracts video/audio/stream links from any website, creates playable .m3u playlists, works 100% offline after initial scan, with zero logging/telemetry for complete privacy. NEXUS TV provides dynamic content scheduling and auto-thumbnail generation. The Multi-Channel Viewer supports advanced multi-viewing with smart audio. Buffer TV focuses on buffering optimization and a TV Guide. Advanced player controls include skip functions, volume control, fullscreen toggles, and timestamp-based clipping. The import/export system supports XML (TVGuide format) and JSON, with comprehensive validation and error reporting. The Interactive Hub features modals for import, schedule, and export, an interactive calendar, and a status dashboard.

### System Design Choices
The architecture follows a dual-component design, separating playlist management (desktop application) from web-based content consumption. Player templates are static HTML/CSS/JavaScript files. A central `index.html` acts as a navigation hub. Data is persisted using JSON files for desktop applications and `localStorage` for web applications. The system is configured for Replit Autoscale and GitHub Pages deployment. Standalone pages with embedded playlist data ensure offline functionality. All imports undergo rigorous validation including schema validation, UTC timestamp normalization, and cryptographic hash-based duplicate and conflict detection.

## External Dependencies

### Python Application
- **requests:** For HTTP requests.
- **beautifulsoup4:** For HTML parsing in Media Stripper feature.
- **Pillow (PIL Fork):** For image processing.
- **tkinterdnd2:** For drag-and-drop in Tkinter.
- **PyInstaller:** For creating standalone executables.
- **FFmpeg:** For video processing, metadata, and screenshots.
- **VLC Media Player:** For embedded video playback.
- **Rumble oEmbed API:** For fetching video metadata.
- **Python Standard Library:** (e.g., `xml.etree.ElementTree`, `datetime`, `hashlib`, `uuid`, `json`, `pathlib`) for core functionalities.

### Web Applications
- **HLS.js:** For HLS playback.
- **dash.js:** For DASH playback.
- **Feather Icons:** For scalable vector icons.
- **express-rate-limit:** For API rate limiting.