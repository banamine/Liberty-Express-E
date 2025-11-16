# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This project offers a comprehensive IPTV solution, combining a professional M3U playlist manager (Python desktop application) with a futuristic streaming TV player (web interface). The platform aims to provide robust tools for managing, organizing, and playing streaming content, catering to users who require advanced control over their IPTV experience. The vision is to deliver a seamless and engaging content consumption experience through efficient playlist management and an immersive streaming environment.

## Recent Changes (November 2025)
- **Title Cleaning Fix:** Fixed workbench import mode displaying URL-encoded filenames (e.g., `Hogan%27s%20Heroes.mp4`) in generated pages. Now properly decodes URLs, removes file extensions, and formats titles cleanly (e.g., `Hogan's Heroes`). Applied to all 3 player templates.
- **Offline Capability:** Eliminated ALL external CDN dependencies. Downloaded HLS.js, Dash.js, and Feather Icons locally. Pages now work 100% offline (except for remote video stream URLs).
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
- **NEXUS TV:** Provides dynamic content scheduling, a responsive user interface, automatic midnight refresh for updated schedules, comprehensive channel analysis with charts, and export of favorites as M3U.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop app) from content consumption (web player) for specialized functionality.
- **Static Web Server:** All player templates run as static file servers.
- **Local Persistence:** M3U Matrix Pro persists settings and data locally in JSON files and dedicated directories.
- **Automated Deployments:** Configured for Replit Autoscale deployment for the web player.
- **Standalone Page Generation:** All generated pages are completely self-contained with embedded playlist data and bundled dependencies (no external CDNs required).
- **Offline-First Design:** Pages work 100% offline for local video files, with zero external dependencies except for remote video stream URLs.

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