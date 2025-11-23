# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade playout scheduler for 24/7 broadcasting, designed for campus TV stations, hotels, YouTube live channels, and local broadcasters. It offers intelligent drag-and-drop scheduling, an auto-filler system, category balancing, multi-week planning with recurring events, and professional export to industry-standard playout engines (e.g., CasparCG, OBS, vMix). The system includes a REST API for remote control and a web-based dashboard, built for unattended operation to deliver continuous video content.

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

## System Architecture

### UI/UX Decisions
The project features a clean, modern design for ScheduleFlow with a professional blue accent. Other components utilize diverse aesthetics, including a neon cyberpunk theme for NEXUS TV, a minimalist UI for Simple Player, a purple gradient for Rumble Channel, and a grid-based viewer for Multi-Channel Viewer. Buffer TV employs a blue-to-red gradient with a numeric keypad and TV Guide overlay. The Interactive Hub uses bubble navigation for managing playlists, schedules, and exports.

### Technical Implementations
The core scheduling logic includes intelligent drag-and-drop, auto-filling, category balancing, multi-week planning, and recurring events. Video playback uses native HTML5 video, HLS.js, and DASH.js. Data persistence is handled via `localStorage` for client-side and JSON files for server-side. Video validation involves HTTP 200 checks, FFprobe metadata, and HLS segment validation. Lazy loading is implemented for efficient resource management. The system supports automated GitHub Pages deployment and includes a production-ready validation engine for imports and exports, covering XML/JSON schema validation, timestamp parsing to UTC, duplicate detection (MD5), and conflict detection. A 48-hour cooldown enforcement mechanism prevents repetitive video plays.

### Feature Specifications
ScheduleFlow includes M3U parsing, channel validation, EPG fetching, settings management, and NDI Output Control Center integration. NEXUS TV provides dynamic content scheduling and auto-thumbnail generation. The Multi-Channel Viewer offers advanced multi-viewing with smart audio. Buffer TV focuses on buffering optimization and a TV Guide. Advanced player controls include skip functions, volume control, fullscreen toggles, and timestamp-based clipping. The import/export system supports XML (TVGuide format) and JSON, with comprehensive validation and error reporting. The Interactive Hub offers modals for import, schedule, and export, an interactive calendar, and status dashboard.

### System Design Choices
The architecture uses a dual-component design separating playlist management (desktop application) from web-based content consumption. Player templates run as static HTML/CSS/JavaScript files. A central `index.html` serves as a navigation hub. Data is persisted using JSON files for desktop apps and `localStorage` for web apps. The system is configured for Replit Autoscale and GitHub Pages deployment. Standalone pages with embedded playlist data ensure offline functionality. All imports undergo rigorous validation including schema validation, UTC timestamp normalization, and cryptographic hash-based duplicate and conflict detection.

## External Dependencies

### Python Application
- **requests:** For HTTP requests.
- **Pillow (PIL Fork):** For image processing.
- **tkinterdnd2:** For drag-and-drop in Tkinter.
- **PyInstaller:** For creating standalone executables.
- **FFmpeg:** For video processing, metadata, and screenshots.
- **VLC Media Player:** For embedded video playback.
- **Rumble oEmbed API:** For fetching video metadata.
- **Python Standard Library:** (e.g., `xml.etree.ElementTree`, `datetime`, `hashlib`, `uuid`, `json`, `pathlib`) for core functionalities without external library dependencies.

### Web Applications
- **HLS.js:** For HLS playback.
- **dash.js:** For DASH playback.
- **Feather Icons:** For scalable vector icons.