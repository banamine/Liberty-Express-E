# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade, modern playout scheduler built for campus TV stations, hotels, YouTube live channels, and local broadcasters. Purpose-built to eliminate the complexity of traditional broadcast scheduling while maintaining professional features. Core functionality includes intelligent drag-and-drop scheduling (1-minute precision), auto-filler system (for gap management), category balancing (content rotation rules), multi-week planning with recurring events, and professional export to industry-standard playout engines (CasparCG, OBS, vMix, FFmpeg, Blackmagic HyperDeck, JustPlayout). The system includes a REST API for remote control, web-based dashboard, and is designed for unattended 24/7 operation.

## User Preferences
- **Communication Style:** Please use clear, simple language and avoid overly technical jargon where possible.
- **Workflow:** I prefer an iterative development approach. Please propose changes and discuss them with me before implementing major modifications.
- **Interaction:** Ask for my approval before making any significant changes to the project structure or core functionalities. Provide detailed explanations for proposed solutions or complex logic.
- **Codebase Changes:**
    - Do not make changes to the `Sample Playlists/` folder.
    - Do not make changes to the `M3U_MATRIX_README.md` file.
    - Ensure all changes are well-documented within the code.

## Phase 2 Completion → Phase 3 Rebrand (Nov 22, 2025)

### ✅ REBRAND TO SCHEDULEFLOW - PROFESSIONAL POSITIONING
- **Name Change**: M3U MATRIX → **ScheduleFlow** (professional playout scheduler)
- **New Positioning**: "Run your 24/7 TV channel without losing your mind"
- **Target Market**: Campus TV, hotels, YouTube live, local stations (realistic, honest positioning)
- **Professional Landing Page** (Nov 22): 
  - Clean, modern design (light theme, professional blue accent)
  - Hero: Simple, honest value proposition
  - 6 core features (1-min grid, drag-drop, auto-filler, category balancing, export, REST API)
  - Use cases: Campus TV, hospitality, YouTube Live, local stations, radio, events
  - 3-tier pricing (Free → Pro $49/mo → Enterprise)
  - Clear, professional tone (removed "M3U MATRIX" branding entirely)
- **Production Status**: Ready for Phase 3 (Jan 6 deadline)

## System Architecture

### UI/UX Decisions
- **M3U MATRIX PRO:** Tkinter-based desktop application.
- **NEXUS TV:** Neon cyberpunk aesthetic with animations.
- **Simple Player:** Clean, responsive, minimalist UI.
- **Rumble Channel:** Dedicated player with a purple gradient and playlist sidebar.
- **Multi-Channel Viewer:** Grid-based player (1-6 channels) with responsive CSS Grid, smart audio management, and focus mode.
- **Buffer TV:** TV player with blue-to-red gradient, numeric keypad, adjustable buffering, and TV Guide overlay.
- **Video Player Pro:** Minimalist launcher GUI and a dual-panel workbench.

### Technical Implementations
- **M3U MATRIX PRO:** Python 3.11 with Tkinter, featuring drag & drop, live validation, EPG integration, remote URL import, regex search, auto-save, UUID tracking, timestamp generation, smart TV scheduler, enhanced import, automatic thumbnail caching, Undo/Redo, JSON export, template generation, deep Rumble integration (URL detection, oEmbed API, category browser), and NDI Output Control Center. Includes FFprobe for real stream validation.
- **NEXUS TV:** HTML5, CSS3, Vanilla JavaScript with native HTML5 video, 24-hour auto-scheduled playback, PWA, HLS.js/DASH.js, favorites, history, channel search, URL encryption, and offline support.
- **Simple Player:** HTML5 video player, vanilla JavaScript, HLS.js, sequential/shuffle playback, group-based organization, and mobile-optimized.
- **Rumble Channel:** Uses iframe embedding for sequential Rumble video playback, automatic URL detection, oEmbed API for metadata, XSS prevention, and offline metadata storage.
- **Multi-Channel Viewer:** HTML5, CSS3 Grid, Vanilla JavaScript, supporting flexible layouts, dynamic channel management, smart audio, time-based rotation, focus mode, and keyboard shortcuts.
- **Buffer TV:** HTML5, CSS3, Vanilla JavaScript, HLS.js, featuring numeric keypad, configurable buffering controls, TV Guide, quick category buttons, CORS proxy support, and automatic stream retry.
- **Video Player Pro:** Standalone Python Tkinter app using FFmpeg and VLC. Features advanced import, file management, metadata extraction, screenshot system, smart scheduling, playlist persistence, embedded VLC player, and persistent settings with TV Guide export.
- **Real Stream Validation (Phase 2):** Implements a three-tier validation process including HTTP 200 checks, FFprobe metadata extraction (video/audio codec, resolution, bitrate, duration), and HLS segment validation (downloading first 3 segments and checking Content-Length). Visual status display (green/blue/orange/red) for validation results.
- **Lazy Loading & Memory Optimization:** Implemented via `LazyPlaylistLoader` (Python) and `UniversalLazyLoader` (JavaScript) to load only 2 items at a time with background pre-loading and caching. Achieves significant memory reduction (e.g., 50x) and instant UI responsiveness for large playlists.
- **GitHub Auto-Deployment:** Integration with `Core_Modules/github_deploy.py` for automated pushing of generated web pages to a specified GitHub repository (`Liberty-Express-`) and `main` branch. Triggered after page generation, copying files to a "Ready Made" folder, creating a timestamped commit, and providing real-time deployment status.
- **Control Hub Enhancements:** Integrated "Performance Player" button and generator option, lazy loading for reduced memory footprint in the hub, enhanced inline help documentation, pop-out workbench functionality for all player types, and a new "From GitHub" filter tab to display and open deployed GitHub Pages.
- **Infowars Extravaganza (Advanced):** Red/black/yellow theme with advanced playback controls: skip forward/backward (10s, 20s, 30s, 1m), full-range volume slider, fullscreen toggle, multi-screen grid viewing (2x2 or 2x3 up to 6 videos), auto-hiding transparent control bar after 10s inactivity, timestamp-based video clipping with start/end markers, and screenshot capture with PC save functionality.

### Feature Specifications
- **M3U MATRIX PRO:** Core M3U parsing, channel validation, EPG fetching, settings management, error handling, security (XSS prevention, URL validation), Rumble URL detection, Navigation Hub integration, Rumble Category Browser, and NDI Output Control Center.
- **NEXUS TV:** Dynamic content scheduling, responsive UI, auto-midnight schedule refresh, channel analysis, favorites export, and auto-thumbnail generation with IndexedDB.
- **Rumble Channel:** Specialized player with automatic URL normalization, metadata fetching, secure iframe embedding, and standalone page generation.
- **Multi-Channel Viewer:** Advanced multi-viewing with grid layout selector, smart audio management, configurable rotation scheduler, focus mode, and play/pause/mute functions.
- **Buffer TV:** TV player with buffering optimization, numeric keypad, adjustable load timeout/retry delay, automatic retry, TV Guide, and quick category access.
- **Infowars Extravaganza (NEW):** Advanced RSS-fed player with skip controls (10s/20s/30s/1m forward/backward), volume slider with percentage display, fullscreen toggle, multi-screen grid viewing (2x2 or 2x3 layouts up to 6 simultaneous videos), transparent control bar with auto-hide after 10s inactivity, progress bar with timestamp display, video clipping with start/end timestamps, and screenshot capture functionality for PC save.
- **Auto-Thumbnail System:** Integrated across all player templates, capturing screenshots during playback and storing them in IndexedDB.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop) from content consumption (web players).
- **Static Web Server:** All player templates run as static files.
- **Navigation Hub System:** Central `index.html` for managing and navigating generated player pages.
- **Local Persistence:** M3U Matrix Pro uses JSON files for data persistence.
- **Automated Deployments:** Configured for Replit Autoscale deployment.
- **Standalone Page Generation:** Self-contained generated pages with embedded playlist data and bundled dependencies.
- **Offline-First Design:** Pages work offline for local video files, embedding playlist data directly in HTML.

## External Dependencies

### Python Application (M3U Matrix Pro & Video Player Pro)
- **requests:** HTTP requests.
- **Pillow (PIL Fork):** Image processing.
- **tkinterdnd2:** Drag-and-drop.
- **PyInstaller:** Standalone executables.
- **FFmpeg:** Video processing, metadata extraction, screenshot generation (Video Player Pro).
- **VLC Media Player:** Embedded video playback (Video Player Pro).
- **Rumble oEmbed API:** Public API for video metadata.

### Web Applications (All Player Templates)
- **npx serve:** Static file serving (optional).
- **HLS.js (Bundled):** HLS stream playback.
- **dash.js (Bundled):** DASH stream playback.
- **Feather Icons (Bundled):** Icons (Web IPTV).
- **System Fonts:** Used by NEXUS TV.