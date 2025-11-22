# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade, modern playout scheduler designed for 24/7 broadcasting needs of campus TV stations, hotels, YouTube live channels, and local broadcasters. It simplifies traditional broadcast scheduling with features like intelligent drag-and-drop scheduling (1-minute precision), an auto-filler system for gap management, category balancing for content rotation, multi-week planning with recurring events, and professional export capabilities to industry-standard playout engines (e.g., CasparCG, OBS, vMix). The system includes a REST API for remote control, a web-based dashboard, and is built for unattended 24/7 operation. Its core purpose is to provide a user-friendly yet powerful tool for managing continuous video content delivery.

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
The project features various UI/UX designs tailored for specific player types:
- **ScheduleFlow (formerly M3U MATRIX):** Clean, modern design with a light theme and professional blue accent for a professional playout scheduler.
- **NEXUS TV:** Neon cyberpunk aesthetic with animations.
- **Simple Player:** Clean, responsive, minimalist UI.
- **Rumble Channel:** Dedicated player with a purple gradient and playlist sidebar.
- **Multi-Channel Viewer:** Grid-based player (1-6 channels) with responsive CSS Grid, smart audio, and focus mode.
- **Buffer TV:** TV player with blue-to-red gradient, numeric keypad, adjustable buffering, and TV Guide overlay.
- **Video Player Pro:** Minimalist launcher GUI and a dual-panel workbench.
- **Keyboard Command Center:** Features a user-friendly interface with category filtering, search, preset configuration, and persistent settings.
- **ScheduleFlow Carousel:** Responsive UI with a live clock, dots navigator, and fullscreen support.
- **M3U Scheduler:** Drag-and-drop interface for 24-hour planning with visual feedback.

### Technical Implementations
- **Core Scheduling Logic:** Intelligent drag-and-drop scheduling with 1-minute precision, auto-filler system for gap management, category balancing for content rotation, multi-week planning with recurring events.
- **Player Technologies:** Utilizes native HTML5 video, HLS.js, and DASH.js for robust media playback.
- **Persistence:** Employs `localStorage` for client-side data persistence (e.g., schedules, video lists, clip markers) and JSON files for server-side data (M3U Matrix Pro).
- **Video Validation:** Implements a three-tier validation process including HTTP 200 checks, FFprobe metadata extraction (codec, resolution, bitrate, duration), and HLS segment validation.
- **Lazy Loading & Memory Optimization:** Uses `LazyPlaylistLoader` (Python) and `UniversalLazyLoader` (JavaScript) to load only a few items at a time with background pre-loading and caching, reducing memory footprint and improving UI responsiveness.
- **Keyboard Command Center:** Provides comprehensive keyboard shortcuts and a centralized control interface for various application functions.
- **Carousel & M3U Scheduler:** Features manual URL input, multi-format support (MP4, HLS, M3U, YouTube), clip mode with start/end times, shareable URLs, and bulk M3U import.
- **Auto-Deployment:** Integration with `Core_Modules/github_deploy.py` for automated pushing of generated web pages to a specified GitHub repository.
- **Rumble Integration:** Utilizes iframe embedding, automatic URL detection, and oEmbed API for metadata retrieval.
- **NDI Output Control Center:** For NDI stream management in the Python desktop application.

### Feature Specifications
- **ScheduleFlow:** Core M3U parsing, channel validation, EPG fetching, settings management, error handling, XSS prevention, URL validation, Rumble URL detection, Navigation Hub integration, and NDI Output Control Center.
- **NEXUS TV:** Dynamic content scheduling, responsive UI, auto-midnight schedule refresh, channel analysis, favorites export, and auto-thumbnail generation with IndexedDB.
- **Multi-Channel Viewer:** Advanced multi-viewing with grid layout selector, smart audio management, configurable rotation scheduler, and focus mode.
- **Buffer TV:** Buffering optimization, numeric keypad, adjustable load timeout/retry delay, automatic retry, TV Guide, and quick category access.
- **Advanced Player Controls:** Includes features like skip forward/backward (10s, 20s, 30s, 1m), full-range volume control, fullscreen toggle, multi-screen grid viewing (up to 6 videos), auto-hiding control bars, timestamp-based video clipping, and screenshot capture.
- **Audit Report:** Generates a comprehensive report detailing test coverage, function status, code quality, and cleanup.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop application) from content consumption (web players).
- **Static Web Server:** All player templates run as static HTML/CSS/JavaScript files.
- **Navigation Hub System:** Central `index.html` for managing and navigating generated player pages.
- **Local Persistence:** Data is persisted using JSON files for desktop apps and `localStorage` for web apps.
- **Automated Deployments:** Configured for Replit Autoscale deployment and GitHub Pages.
- **Standalone Page Generation:** Self-contained generated pages with embedded playlist data and bundled dependencies for offline functionality.

## External Dependencies

### Python Application (M3U Matrix Pro & Video Player Pro)
- **requests:** For HTTP requests.
- **Pillow (PIL Fork):** For image processing.
- **tkinterdnd2:** For drag-and-drop functionality in Tkinter.
- **PyInstaller:** For creating standalone executables.
- **FFmpeg:** For video processing, metadata extraction, and screenshot generation.
- **VLC Media Player:** For embedded video playback.
- **Rumble oEmbed API:** Public API for fetching video metadata.

### Web Applications (All Player Templates)
- **npx serve:** (Optional) For static file serving during development/testing.
- **HLS.js:** For HLS (HTTP Live Streaming) playback.
- **dash.js:** For DASH (Dynamic Adaptive Streaming over HTTP) playback.
- **Feather Icons:** For scalable vector icons.
- **System Fonts:** Standard browser fonts used for text rendering.