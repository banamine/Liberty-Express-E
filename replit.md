# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade playout scheduler for 24/7 broadcasting, designed for continuous video content delivery. It supports intelligent drag-and-drop scheduling, an auto-filler system, category balancing, multi-week planning with recurring events, and professional export to industry-standard playout engines. The system includes a REST API for remote control and a web-based dashboard, targeting applications such as campus TV, hotels, YouTube live channels, and local broadcasters.

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
The core system operates in either an Advanced (GUI) or Silent Background (Daemon) mode, processing inputs from various sources including a GUI, REST API, numeric keypad, and a web dashboard.

**UI/UX Decisions:** ScheduleFlow features a professional blue accent. Other components utilize diverse aesthetics: NEXUS TV (neon cyberpunk), Simple Player (minimalist), Rumble Channel (purple gradient), Multi-Channel Viewer (grid-based), Buffer TV (blue-to-red gradient with numeric keypad and TV Guide overlay), and Interactive Hub (bubble navigation). A professional web dashboard provides a UI for non-technical users.

**Technical Implementations:**
The system is built on a modular Python architecture using FastAPI (port 3000) for the backend and a Node.js proxy (port 5000) as the public gateway. Key modules handle scheduling, validation, cross-platform file operations, versioning, backups, media stripping, progress tracking, and response caching. Core scheduling logic includes intelligent drag-and-drop, auto-filling, category balancing, multi-week planning, and recurring events. Video playback utilizes native HTML5 video, HLS.js, and DASH.js. Data persistence uses `localStorage` for client-side and SQLite and JSON files for server-side. Video validation includes HTTP 200 checks, FFprobe metadata, and HLS segment validation. Lazy loading is implemented for efficiency. The system supports automated GitHub Pages deployment and includes a production-ready validation engine covering schema validation, UTC timestamp parsing, duplicate detection (MD5), and conflict detection. A 48-hour cooldown enforces unique video plays. Response caching with configurable TTL and thread-safe progress tracking are integrated. A comprehensive refactoring effort modularized the system into 10 focused modules, introduced cross-platform file management with backups, structured JSON logging, enhanced media stripping with Selenium and `robots.txt` compliance, optimized scheduling logic with timezone support, integrated FastAPI, implemented a ThreadPoolExecutor for threading, and centralized configuration using YAML. Authentication now includes JWT, user management, role-based access control, and audit logging. A template system for large HLS/M3U8 playlists (1000+ segments) incorporates server-side sliding windows, client-side buffer management, and delta updates for bandwidth savings.

**Feature Specifications:**
ScheduleFlow offers M3U parsing, channel validation, EPG fetching, settings management, and NDI Output Control Center integration. A Private Media Stripper extracts video/audio/stream links from any website, creates playable .m3u playlists, works 100% offline, and ensures complete privacy. NEXUS TV provides dynamic content scheduling and auto-thumbnail generation. The Multi-Channel Viewer supports advanced multi-viewing with smart audio. Buffer TV focuses on buffering optimization and a TV Guide. Advanced player controls include skip functions, volume control, fullscreen toggles, and timestamp-based clipping. The import/export system supports XML (TVGuide format) and JSON, with comprehensive validation and error reporting. The Interactive Hub features modals for import, schedule, and export, an interactive calendar, and a status dashboard.

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