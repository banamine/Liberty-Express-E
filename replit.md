# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This project offers a comprehensive IPTV solution, combining a professional M3U playlist manager (Python desktop application) with a futuristic streaming TV player (web interface). The platform aims to provide robust tools for managing, organizing, and playing streaming content, catering to users who require advanced control over their IPTV experience. The vision is to deliver a seamless and engaging content consumption experience through efficient playlist management and an immersive streaming environment.

**NEW:** Video Player Pro - A standalone vanilla Python video player application with advanced scheduling, screenshot capture, and metadata extraction capabilities (see Video Player Pro section below).

## Recent Changes (November 2025)
- **Video Player Pro Playback Fix (Nov 16):** Fixed broken playback wiring. Videos now play correctly when double-clicked or Play button pressed. Added <<TreeviewSelect>> binding to update current_index, fixed double-click event handling, auto-select first video after import, improved toggle_play() error handling.
- **Video Player Pro Embedded VLC Player (Nov 16):** Added embedded VLC video player. Videos now play INSIDE the app window with live screenshot capture at exact playback position, real-time video info (codec/resolution), playback position display, and auto-advance to next video. Requires VLC Media Player installation.
- **VIDEO Button Path Fix (Nov 16):** Fixed VIDEO button in M3U MATRIX PRO to work from any drive/location. Now intelligently searches multiple possible paths to find Video Player Pro, supporting both deployment and development folder structures.
- **M3U MATRIX PRO GUI Additions (Nov 16):** Added THUMBS button (opens thumbnails folder) and VIDEO button (launches Video Player Pro) to the main GUI toolbar row 1. Fixed M3U parser to accept non-standard formats like #EXTM: and #EXTMM: tags (e.g., Taxi.m3u files).
- **Video Player Pro Sandbox Import (Nov 16):** Enhanced "Load" button with universal file acceptance philosophy. Accepts ANY file type first, scans for URLs/content, then reports results. Never rejects files upfront. Extracts links from: M3U/M3U8 playlists, TXT/HTML/XML/JSON files (HTTP/HTTPS/RTMP/RTSP/file://), video/audio files, Windows paths (C:\...), and recursive folder scanning. Improved URL extraction with line-by-line scanning and Windows path support.
- **Video Player Pro (Nov 16):** Created standalone vanilla Python video player application. Features include: minimalist launcher GUI, video player workbench with dual-panel layout, FFmpeg-based metadata extraction, screenshot capture with JSON metadata and auto-thumbnails, playlist management (copy/paste/delete), smart scheduling system with time predictions, auto-save functionality, and cross-platform playback support.
- **Auto-Thumbnail System (Nov 16):** Implemented IndexedDB-based automatic thumbnail generation for all player templates. Features include: 2 screenshots per video captured at 25% and 75% playtime, browser-based storage using IndexedDB (non-portable but fast), per-page thumbnail databases, placeholder system until captures complete, HLS/DASH/direct stream support. Thumbnails auto-generate as videos play with zero user interaction required.
- **CDN Elimination (Nov 16):** Eliminated ALL external CDN dependencies across templates. NEXUS TV embeds HLS.js, DASH.js, and thumbnail-system.js inline. Web IPTV and Simple Player use local bundled copies in js/libs/ folders. All generated pages work 100% offline (except for remote video stream URLs). Fail-fast error handling ensures library files are present before generation.
- **Smart TV Scheduler (Nov 16):** Added intelligent 7-day TV scheduling system for NEXUS TV. Features include: global content randomization, configurable show durations, no daily repeats, max consecutive episode limiting, and automated schedule generation. Scheduler dialog appears before NEXUS TV generation with settings for show duration (5-180 min), number of days (1-30), and max consecutive shows (1-10).
- **Enhanced File Import System (Nov 16):** Fixed "No channels found" error by removing restrictive URL filtering. Now accepts ALL URL types (HTTPS, HTTP, RTMP, RTSP, local paths, file:// URLs). Added TXT file support with automatic link extraction. Added folder/subfolder scanning to recursively find all media files and playlists. Import dialog now offers "Files" or "Folder" selection.
- **Title Cleaning Fix:** Fixed workbench import mode displaying URL-encoded filenames (e.g., `Hogan%27s%20Heroes.mp4`) in generated pages. Now properly decodes URLs, removes file extensions, and formats titles cleanly (e.g., `Hogan's Heroes`). Applied to all 3 player templates.
- **Folder Organization:** Implemented proper folder structure `generated_pages/<name>/` with isolated assets for each generated page.

## User Preferences
- **Communication Style:** Please use clear, simple language and avoid overly technical jargon where possible.
- **Workflow:** I prefer an iterative development approach. Please propose changes and discuss them with me before implementing major modifications.
- **Interaction:** Ask for my approval before making any significant changes to the project structure or core functionalities. Provide detailed explanations for proposed solutions or complex logic.
- **Codebase Changes:**
    - Do not make changes to the `Sample Playlists/` folder.
    - Do not make changes to the `M3U_MATRIX_README.md` file.
    - Ensure all changes are well-documented within the code.

## System Architecture
The project includes M3U MATRIX PRO (Python desktop application) with three web player templates: NEXUS TV (24-hour scheduled player), Web IPTV (sequential channel player), and Simple Player (clean video-focused player).

### UI/UX Decisions
- **M3U MATRIX PRO:** Utilizes Tkinter for a native desktop application feel, focusing on functionality and ease of use for playlist management.
- **NEXUS TV:** Features a neon cyberpunk aesthetic with animations, designed for an immersive 24-hour streaming experience. It includes a thumbnail carousel, fullscreen video player, world timezone clocks, dynamic top panel, and a theme toggle (light/dark mode).
- **Simple Player:** Clean, responsive video player with minimal UI focusing on video content. Features sequential and shuffle playback modes without time-based scheduling or clocks.

### Technical Implementations
- **M3U MATRIX PRO:**
    - Built with Python 3.11 and Tkinter.
    - Features include drag & drop channel reordering, live validation, smart playlist organization, EPG integration (XMLTV), CSV export, remote URL import, regex-powered search, auto-save, progress bars, improved error messages, exit protection, UUID tracking for channels, and a Timestamp Generator for M3U playlists with seek markers.
    - **Smart TV Scheduler:** Creates 7-day TV schedules with global randomization, configurable show durations, no daily repeats, and consecutive episode limiting. Integrated into NEXUS TV generation workflow.
    - **Enhanced Import System:** Accepts M3U/M3U8 playlists, TXT files (with automatic URL extraction), video/audio files, and folder scanning (recursive). Supports all URL types including local paths, file:// URLs, HTTPS, RTMP, RTSP.
    - Incorporates an installer system for Windows with portable and full installation modes, auto-updates, and user verification.
    - Includes an automatic thumbnail caching system.
    - Implements Undo/Redo functionality and JSON export with metadata.
    - Template generator supports three player types: NEXUS TV, Web IPTV, and Simple Player.
- **NEXUS TV:**
    - Developed using HTML5, CSS3, and Vanilla JavaScript.
    - Utilizes the native HTML5 video element for playback.
    - Implements a 24-hour auto-scheduled playback system and a dual-mode toggle for Schedule and Live TV.
    - Configured as a Progressive Web Application (PWA).
    - Features HLS.js and DASH.js integration for various streaming formats, a favorites system, history tracking, channel search, and URL encryption/sharing.
    - Uses FFmpeg for accurate video duration and keyframe detection from local files.
- **Simple Player:**
    - Clean, responsive HTML5 video player built with vanilla JavaScript.
    - HLS.js integration for .m3u8 stream support.
    - Dual playback modes: Sequential (plays in order) and Shuffle (randomizes).
    - Group-based playlist organization with modal view.
    - Auto-advance to next video on completion.
    - Mobile-optimized with touch controls.
    - No time-based scheduling or clocks - video-focused UI.

### Feature Specifications
- **M3U MATRIX PRO:** Core functionalities include M3U parsing, channel validation, EPG fetching, settings management, robust error handling, and security features like XSS prevention and URL validation.
- **NEXUS TV:** Provides dynamic content scheduling, a responsive user interface, automatic midnight refresh for updated schedules, comprehensive channel analysis with charts, export of favorites as M3U, and auto-thumbnail generation with IndexedDB storage.
- **Auto-Thumbnail System:** Built-in thumbnail generation across all player templates. Captures 2 screenshots per video (at 25% and 75% playtime) automatically during playback. Stores thumbnails in IndexedDB (browser storage) with separate databases per page. Supports HLS, DASH, and direct stream formats. No user intervention required - fully automatic.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop app) from content consumption (web player) for specialized functionality.
- **Static Web Server:** All player templates run as static file servers.
- **Local Persistence:** M3U Matrix Pro persists settings and data locally in JSON files and dedicated directories.
- **Automated Deployments:** Configured for Replit Autoscale deployment for the web player.
- **Standalone Page Generation:** All generated pages are completely self-contained with embedded playlist data and bundled dependencies (no external CDNs required).
- **Offline-First Design:** Pages work 100% offline for local video files, with zero external dependencies except for remote video stream URLs.

## Video Player Pro

### Description
A standalone vanilla Python desktop application for advanced video playback, scheduling, and management. Built entirely with standard Python libraries (Tkinter) and FFmpeg integration.

### Key Features
- **Main Launcher**: Minimalist GUI with single-click launch button
- **Video Workbench**: Advanced dual-panel interface for playlist management and playback
- **Advanced Import (Load Button)**: Blue "📂 Load" button with full import capabilities:
  - M3U/M3U8 playlist parsing with metadata
  - TXT file URL extraction (HTTP, HTTPS, RTMP, RTSP, file://)
  - Video/audio file direct import
  - Recursive folder scanning for all media and playlists
  - Automatic link detection from text files
- **File Management**: Open, close, delete, copy, paste video operations
- **FFmpeg Integration**: Automatic metadata extraction (duration, resolution, codec, file size)
- **Screenshot System**: Capture screenshots with automatic JSON metadata and thumbnail generation
- **Smart Scheduling**: Generate TV-style schedules with customizable time slots and predictions
- **Playlist Persistence**: Auto-save and manual save/load of playlists in JSON format
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Technical Stack
- Python 3.7+ with Tkinter (built-in GUI framework)
- FFmpeg for video processing and metadata extraction
- Pillow (PIL) for image/thumbnail processing
- JSON-based data storage

### File Structure
```
src/video_player_app/
├── main_launcher.py           # Main launcher GUI
├── video_player_workbench.py  # Workbench interface
├── run_player.py              # Entry point script
├── README.txt                 # User documentation
├── FEATURES.md                # Feature documentation
├── screenshots/               # Screenshot storage
├── data/                      # Application data
└── data/playlist.json        # Auto-saved playlist
```

### Usage
```bash
cd src/video_player_app
python run_player.py
```

## External Dependencies

### Python Application (M3U Matrix Pro)
- **requests:** For making HTTP requests (e.g., channel validation, remote URL import, EPG fetching).
- **Pillow (PIL Fork):** For image processing (e.g., handling channel logos/thumbnails, image verification).
- **tkinterdnd2:** For drag-and-drop functionality in the GUI.
- **PyInstaller:** For creating standalone Windows executables.

### Web Applications (All Player Templates)
- **npx serve:** Node.js package used to serve static files for the web interface (optional - pages can also run directly via file://).
- **HLS.js (Bundled):** For HLS stream playback - downloaded locally (529KB) for offline use.
- **dash.js (Bundled):** For DASH stream playback in Web IPTV - downloaded locally (908KB) for offline use.
- **Feather Icons (Bundled):** For icons in Web IPTV - downloaded locally (75KB) for offline use.
- **System Fonts:** NEXUS TV uses system fonts ('Segoe UI', 'Arial Black', 'Impact') instead of Google Fonts for offline compatibility.
- **Note:** All CDN dependencies have been eliminated. Generated pages are 100% self-contained and work offline.