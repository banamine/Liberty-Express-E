# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade playout scheduler for 24/7 broadcasting, designed for continuous video content delivery. It supports intelligent drag-and-drop scheduling, an auto-filler system, category balancing, multi-week planning with recurring events, and professional export to industry-standard playout engines. The system includes a REST API for remote control and a web-based dashboard, targeting applications such as campus TV, hotels, YouTube live channels, and local broadcasters, aiming for continuous video content delivery.

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

## Critical Technical Notes
- **NEVER hardcode external URLs** (especially archive.org) - they cause CORS failures and "Stream unavailable" errors
- **Always use local /attached_assets/ paths** for user-uploaded files or reliable public CDN sources (Google, W3Schools)
- Archive.org videos fail in HTML5 players due to CORS restrictions - avoid completely
- Hardcoded URLs break when external sources change - use local files instead
- **Desktop App Button Overflow Fixed:** Reduced toolbar button widths from 14→10 and padx from 4→2; all 36 button commands verified and wired correctly
- **Clean Exit on Close:** safe_exit() now gracefully closes all child windows, hides main window, and exits silently without errors

## System Architecture
The core system operates in either an Advanced (GUI) or Silent Background (Daemon) mode, processing inputs from various sources including a GUI, REST API, numeric keypad, and a web dashboard.

**UI/UX Decisions:** ScheduleFlow features a professional black, green, and yellow theme for high-contrast and readability. Other components utilize diverse aesthetics like neon cyberpunk or minimalist designs. A professional web dashboard provides a UI for non-technical users.

**Technical Implementations:**
The system is built on a modular Python architecture using FastAPI for the backend and a Node.js proxy as the public gateway. Key modules handle scheduling, validation, cross-platform file operations, versioning, backups, media stripping, progress tracking, and response caching. Core scheduling logic includes intelligent drag-and-drop, auto-filling, category balancing, multi-week planning, and recurring events. Video playback utilizes native HTML5 video, HLS.js, and DASH.js. Data persistence uses `localStorage` for client-side and SQLite and JSON files for server-side. The system supports automated GitHub Pages deployment and includes a production-ready validation engine covering schema validation, UTC timestamp parsing, duplicate detection (MD5), and conflict detection. A 48-hour cooldown enforces unique video plays. Authentication includes JWT, user management, role-based access control, and audit logging. A template system for large HLS/M3U8 playlists incorporates server-side sliding windows, client-side buffer management, and delta updates.

**Feature Specifications:**
ScheduleFlow offers M3U parsing, channel validation, EPG fetching, settings management, and NDI Output Control Center integration. A Private Media Stripper extracts video/audio/stream links from any website. Advanced player controls include skip functions, volume control, fullscreen toggles, and timestamp-based clipping. The import/export system supports XML (TVGuide format) and JSON, with comprehensive validation and error reporting. The Interactive Hub features modals for import, schedule, and export, an interactive calendar, and a status dashboard. The scheduler includes a file manager, drag-and-drop upload, and an intelligent auto-schedule feature with series detection. The demo player features an embedded priority playlist with auto-rotating 5-minute clips rotating between 2-4 shows, requiring no user interaction for playlist selection.

**Scheduler Enhancements:**
- **Universal File Import:** Accepts M3U, JSON, XML, HTML, plain text - any file format containing HTTP/HTTPS links
- **Smart Title Extraction:** Prioritizes M3U metadata titles; for URLs (especially archive.org), extracts filename and decodes %20/%2D/etc for readable display while preserving original link encoding
- **Series Detection:** Recognizes formats like "Breaking Bad S01E01", "The Office Season 2 Episode 5", "Show 1x03"
- **Intelligent Auto-Schedule:** Groups content by series, sorts episodes correctly, uses round-robin distribution to prevent binge-watching, fills 24 hours efficiently
- **Conflict Detection:** Prevents duplicate episodes, detects time overlaps, identifies out-of-order episodes with visual indicators and auto-fix suggestions
- **Manual + Auto Workflows:** Supports "auto-first then manual adjust" and "manual-first then auto-fill" workflows

**Large Playlist Optimizer (Universal Format Support):**
- **File Upload:** Drag-and-drop or click to upload ANY file format (.m3u, .json, .xml, .html, .txt, etc.)
- **Format Auto-Detection:** Automatically detects and parses:
  - M3U/M3U8 playlists (with #EXTM3U metadata)
  - JSON files (recursive URL extraction from all fields)
  - XML/EPG files (attribute and text node extraction)
  - Plain text files (regex-based URL extraction)
  - HTML pages (link extraction from content)
- **Link Extraction:** Single click "Extract Links" button to find all HTTP/HTTPS URLs in uploaded content
- **Smart Loading:** Attempts to load first valid URL from extracted list
- **Status Reporting:** Clear feedback on number of URLs found and loading progress

**Demo Player Features:**
- **Embedded Priority Playlist:** Pre-loaded with 3 shows (Mayday, Documentary Collection, Classic Films) - no selection needed
- **Auto-Rotating Clips:** Plays random 5-minute segments rotating between shows
- **One-Click Start:** User clicks "Play Demo" button to start - all playlist management is automatic
- **Continuous Loop:** Auto-advances after 5 minutes indefinitely

**Calendar Demo Features:**
- **4-Week Schedule Viewer:** Browse up to 4 weeks of programmed content
- **7-Day Grid Layout:** Shows Mon-Sun with dates and time slots
- **Rotating Episodes:** Each day features different episodes (no repetition within cooldown)
- **Multi-Show Schedule:** 4 shows daily at staggered times (08:00, 13:00, 16:00, 20:00)
- **Color-Coded Shows:** Visual distinction between different content types
- **Smart Distribution:** Demonstrates round-robin scheduling preventing viewer fatigue

**Local Media Player:**
- **Custom Playlist Support:** Load user-uploaded MP4, MP3, WMA, and other media files
- **Media Library Management:** Browse and play through locally stored content
- **Playback Controls:** Play/pause, next/previous, progress tracking
- **Playlist Navigation:** Click any item to jump to that track
- **Keyboard Shortcuts:** Space (play/pause), Arrow keys (next/prev)

**File Documentation & Organization System:**
- **FILE_BROWSER_README.html** - Comprehensive file browser with:
  - Organized files by type (Players, Schedulers, Utilities, Shows)
  - GitHub pull commands for offline access
  - Show-specific pages organized by title + timestamp
  - Quick-access buttons and search system
  - Easy retrieval from any page or GUI
- **Accessible from:** All pages via "📋 Documentation" link, M3U PRO "Documentation" button, or direct URL
- **Offline Capability:** Full instructions for cloning from GitHub and using pages without server

**System Design Choices:**
The architecture employs a dual-component design, separating playlist management (desktop application) from web-based content consumption. Player templates are static HTML/CSS/JavaScript. A central `index.html` serves as a navigation hub. Data is persisted using JSON files for desktop applications and `localStorage` for web applications. The system is configured for Replit Autoscale and GitHub Pages deployment. Standalone pages with embedded playlist data ensure offline functionality. All imports undergo rigorous validation including schema validation, UTC timestamp normalization, and cryptographic hash-based duplicate and conflict detection.

## External Dependencies

**Python Application:**
- `fastapi`: Web framework.
- `uvicorn`: ASGI server.
- `pydantic`: Data validation and settings.
- `requests`: HTTP client.
- `beautifulsoup4`: HTML parsing.
- `Pillow (PIL Fork)`: Image processing.
- `tkinterdnd2`: Drag-and-drop for Tkinter.
- `PyInstaller`: Standalone executables.
- `FFmpeg`: Video processing and metadata.
- `VLC Media Player`: Embedded video playback.
- `Rumble oEmbed API`: Video metadata.

**Web Applications:**
- `axios` (Node.js): HTTP client.
- `HLS.js`: HLS video playback.
- `dash.js`: DASH video playback.
- `Feather Icons`: Scalable vector icons.
- `express-rate-limit`: API rate limiting.