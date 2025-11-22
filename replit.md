# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This project provides a comprehensive IPTV solution, integrating a Python desktop application for M3U playlist management (M3U MATRIX PRO) with multiple web-based streaming TV players. The platform aims to offer robust tools for organizing and playing streaming content, delivering a seamless and engaging content consumption experience. Key capabilities include professional M3U playlist management, 24-hour scheduled streaming (NEXUS TV), sequential channel playback (Web IPTV), multi-channel viewing (Multi-Channel Viewer), dedicated Rumble video playback, and advanced TV playback with buffering controls (Buffer TV). It also features a standalone Video Player Pro with advanced scheduling and a Professional NDI (Network Device Interface) output for broadcast-grade video-over-IP streaming to production systems.

## User Preferences
- **Communication Style:** Please use clear, simple language and avoid overly technical jargon where possible.
- **Workflow:** I prefer an iterative development approach. Please propose changes and discuss them with me before implementing major modifications.
- **Interaction:** Ask for my approval before making any significant changes to the project structure or core functionalities. Provide detailed explanations for proposed solutions or complex logic.
- **Codebase Changes:**
    - Do not make changes to the `Sample Playlists/` folder.
    - Do not make changes to the `M3U_MATRIX_README.md` file.
    - Ensure all changes are well-documented within the code.

## System Architecture

### UI/UX Decisions
- **M3U MATRIX PRO:** Tkinter-based desktop application for native playlist management.
- **NEXUS TV:** Neon cyberpunk aesthetic with animations for an immersive 24-hour streaming experience.
- **Simple Player:** Clean, responsive, minimalist UI focused on video content.
- **Rumble Channel:** Dedicated player for Rumble videos with a purple gradient design and playlist sidebar.
- **Multi-Channel Viewer:** Grid-based player (1-6 channels) with responsive CSS Grid, smart audio management, and focus mode.
- **Buffer TV:** TV player with a blue-to-red gradient, numeric keypad, adjustable buffering settings, and TV Guide overlay.
- **Video Player Pro:** Minimalist launcher GUI and a dual-panel workbench for video management.

### Technical Implementations
- **M3U MATRIX PRO:** Python 3.11 with Tkinter. Features drag & drop, live validation, smart playlist organization, EPG integration, remote URL import, regex search, auto-save, UUID tracking, Timestamp Generator, Smart TV Scheduler, Enhanced Import System, installer, automatic thumbnail caching, Undo/Redo, JSON export, template generation for all players, deep Rumble integration (URL detection, oEmbed API metadata, Rumble Category Browser), and NDI Output Control Center for broadcast integration. Includes FFprobe integration for real stream validation, checking random samples, detecting stream types, and extracting metadata with timeout protection.
- **NEXUS TV:** HTML5, CSS3, Vanilla JavaScript with native HTML5 video, 24-hour auto-scheduled playback, PWA, HLS.js/DASH.js, favorites, history, channel search, URL encryption, and offline support with embedded playlist data.
- **Simple Player:** HTML5 video player, vanilla JavaScript, HLS.js, sequential/shuffle playback, group-based organization, and mobile-optimized.
- **Rumble Channel:** Uses iframe embedding for sequential Rumble video playback, automatic URL detection, oEmbed API for metadata, XSS prevention, and offline metadata storage.
- **Multi-Channel Viewer:** HTML5, CSS3 Grid, Vanilla JavaScript. Supports flexible grid layouts, dynamic channel management, smart audio controller, time-based rotation, focus mode, and keyboard shortcuts.
- **Buffer TV:** HTML5, CSS3, Vanilla JavaScript, HLS.js. Features numeric keypad, configurable buffering controls (load timeout, retry delay), TV Guide, quick category buttons, CORS proxy support, and automatic stream retry.
- **Video Player Pro:** Standalone Python Tkinter app using FFmpeg and VLC. Features advanced import, file management, metadata extraction, screenshot system, smart scheduling, playlist persistence, embedded VLC player, and persistent settings with TV Guide export.

### Feature Specifications
- **M3U MATRIX PRO:** Core M3U parsing, channel validation, EPG fetching, settings management, error handling, security (XSS prevention, URL validation), Rumble URL detection, Navigation Hub integration, Rumble Category Browser, and NDI Output Control Center for professional broadcast streaming.
- **NEXUS TV:** Dynamic content scheduling, responsive UI, auto-midnight schedule refresh, channel analysis, favorites export, and auto-thumbnail generation with IndexedDB.
- **Rumble Channel:** Specialized player with automatic URL normalization, metadata fetching, secure iframe embedding, and standalone page generation.
- **Multi-Channel Viewer:** Advanced multi-viewing with grid layout selector, smart audio management, configurable rotation scheduler, focus mode, and play/pause/mute functions.
- **Buffer TV:** TV player with buffering optimization, numeric keypad, adjustable load timeout/retry delay, automatic retry, TV Guide, and quick category access.
- **Auto-Thumbnail System:** Integrated across all player templates, capturing screenshots (25% and 75% playtime) during playback, stored in IndexedDB with support for HLS, DASH, and direct streams.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop) from content consumption (web players).
- **Static Web Server:** All player templates run as static files.
- **Navigation Hub System:** Central `index.html` for managing and navigating all generated player pages, including an organized folder structure, "Back to Hub" button, sample channels, bookmarks export, auto-cleanup, and statistics dashboard.
- **Local Persistence:** M3U Matrix Pro uses JSON files for local data persistence.
- **Automated Deployments:** Configured for Replit Autoscale deployment.
- **Standalone Page Generation:** Self-contained generated pages with embedded playlist data and bundled dependencies.
- **Offline-First Design:** Pages work offline for local video files with `file://` protocol support, embedding playlist data directly in HTML.

## Code Quality & Maintenance

### LSP Diagnostics Status
- **Total Warnings Reduced:** 47 → 8 (83% reduction)
- **Fixed Issues:**
  - ✅ Type hints for Optional[List[str]] in validation functions
  - ✅ Proper import error handling with type: ignore comments
  - ✅ UndoManager API fixed (push_action → save_state)
  - ✅ Image module optional import protection
  - ✅ Duplicate exception handling removed
  - ✅ Removed orphaned code blocks

### Memory Management
- **Video Player Pro VLC Cleanup:** NEW - Implemented proper resource cleanup
  - `_cleanup_vlc()` method stops VLC instance and releases memory
  - Registered cleanup handler (WM_DELETE_WINDOW protocol)
  - Prevents memory leaks when window is closed
  - Safe exception handling during cleanup

## External Dependencies

### Python Application (M3U Matrix Pro & Video Player Pro)
- **requests:** HTTP requests (validation, remote import, EPG, Rumble oEmbed).
- **Pillow (PIL Fork):** Image processing (logos, thumbnails).
- **tkinterdnd2:** Drag-and-drop functionality.
- **PyInstaller:** Standalone Windows executables.
- **FFmpeg:** Video processing, metadata extraction, screenshot generation (Video Player Pro).
- **VLC Media Player:** Embedded video playback (Video Player Pro).
- **Rumble oEmbed API:** Public API for video metadata.

### Web Applications (All Player Templates)
- **npx serve:** Static file serving (optional).
- **HLS.js (Bundled):** HLS stream playback.
- **dash.js (Bundled):** DASH stream playback.
- **Feather Icons (Bundled):** Icons (Web IPTV).
- **System Fonts:** Used by NEXUS TV.