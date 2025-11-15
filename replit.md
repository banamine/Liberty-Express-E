# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This project offers a comprehensive IPTV solution, combining a professional M3U playlist manager (Python desktop application) with a futuristic streaming TV player (web interface). The platform aims to provide robust tools for managing, organizing, and playing streaming content, catering to users who require advanced control over their IPTV experience. The vision is to deliver a seamless and engaging content consumption experience through efficient playlist management and an immersive streaming environment.

## User Preferences
- **Communication Style:** Please use clear, simple language and avoid overly technical jargon where possible.
- **Workflow:** I prefer an iterative development approach. Please propose changes and discuss them with me before implementing major modifications.
- **Interaction:** Ask for my approval before making any significant changes to the project structure or core functionalities. Provide detailed explanations for proposed solutions or complex logic.
- **Codebase Changes:**
    - Do not make changes to the `Sample Playlists/` folder.
    - Do not make changes to the `M3U_MATRIX_README.md` file.
    - Ensure all changes are well-documented within the code.

## System Architecture
The project is split into two main components: M3U MATRIX PRO (a Python desktop application) and NEXUS TV (a web-based streaming player).

### UI/UX Decisions
- **M3U MATRIX PRO:** Utilizes Tkinter for a native desktop application feel, focusing on functionality and ease of use for playlist management.
- **NEXUS TV:** Features a neon cyberpunk aesthetic with animations, designed for an immersive 24-hour streaming experience. It includes a thumbnail carousel, fullscreen video player, world timezone clocks, dynamic top panel, and a theme toggle (light/dark mode).

### Technical Implementations
- **M3U MATRIX PRO:**
    - Built with Python 3.11 and Tkinter.
    - Features include drag & drop channel reordering, live validation, smart playlist organization, EPG integration (XMLTV), CSV export, remote URL import, regex-powered search, auto-save, progress bars, improved error messages, exit protection, UUID tracking for channels, and a Timestamp Generator for M3U playlists with seek markers.
    - Incorporates an installer system for Windows with portable and full installation modes, auto-updates, and user verification.
    - Includes an automatic thumbnail caching system.
    - Implements Undo/Redo functionality and JSON export with metadata.
- **NEXUS TV:**
    - Developed using HTML5, CSS3, and Vanilla JavaScript.
    - Utilizes the native HTML5 video element for playback.
    - Implements a 24-hour auto-scheduled playback system and a dual-mode toggle for Schedule and Live TV.
    - Configured as a Progressive Web Application (PWA).
    - Features HLS.js and DASH.js integration for various streaming formats, a favorites system, history tracking, channel search, and URL encryption/sharing.
    - Uses FFmpeg for accurate video duration and keyframe detection from local files.

### Feature Specifications
- **M3U MATRIX PRO:** Core functionalities include M3U parsing, channel validation, EPG fetching, settings management, robust error handling, and security features like XSS prevention and URL validation.
- **NEXUS TV:** Provides dynamic content scheduling, a responsive user interface, automatic midnight refresh for updated schedules, comprehensive channel analysis with charts, and export of favorites as M3U.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop app) from content consumption (web player) for specialized functionality.
- **Static Web Server:** NEXUS TV runs as a static file server.
- **Local Persistence:** M3U Matrix Pro persists settings and data locally in JSON files and dedicated directories.
- **Automated Deployments:** Configured for Replit Autoscale deployment for the web player.

## External Dependencies

### Python Application (M3U Matrix Pro)
- **requests:** For making HTTP requests (e.g., channel validation, remote URL import, EPG fetching).
- **Pillow (PIL Fork):** For image processing (e.g., handling channel logos/thumbnails, image verification).
- **tkinterdnd2:** For drag-and-drop functionality in the GUI.
- **PyInstaller:** For creating standalone Windows executables.

### Web Application (NEXUS TV)
- **npx serve:** Node.js package used to serve static files for the web interface.
- **Google Fonts (Orbitron):** For specific typography styling.
- **Font Awesome 6.4.0:** For icons used in the UI.
- **HLS.js:** For HLS stream playback.
- **dash.js:** For DASH stream playback.