# ScheduleFlow - Modern Playout Scheduler for 24/7 Broadcasting

## Overview
**ScheduleFlow** is a professional-grade playout scheduler for 24/7 broadcasting, designed for various applications including campus TV stations, hotels, YouTube live channels, and local broadcasters. Its primary purpose is to provide unattended, continuous video content delivery through intelligent drag-and-drop scheduling, an auto-filler system, category balancing, and multi-week planning with recurring events. The system includes a REST API for remote control and a web-based dashboard, offering professional export capabilities to industry-standard playout engines.

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

## 🎉 WEEKS 1-4: FUNCTIONAL BUT NOT PRODUCTION-READY ⚠️

**Status:** Core functionality works. Critical audit gaps identified and being fixed.

**What Was Built:** 30+ REST API endpoints, 10 core modules, professional web dashboard

**Honest Assessment (Audit Nov 23):**
The system had several **over-claimed** features. External audit revealed:
- ❌ **API Documentation:** Claimed documented, but lacked Swagger/OpenAPI
- ❌ **Authentication:** Missing - no JWT or user auth layer
- ❌ **Structured Logging:** Basic logging only, not production-grade
- ❌ **Data Persistence:** JSON files only (data loss risk at scale)
- ❌ **Security Audit:** No security review performed
- ⚠️ **Production Claim:** Too aggressive - needs more hardening

**Key Numbers (What's ACTUALLY Working):**
- ✅ 30+ REST API endpoints (functional, not all documented)
- ✅ 10 core modules (code is modular, not enterprise-hardened)
- ✅ 2 running workflows (FastAPI port 3000, Node.js proxy port 5000)
- ⚠️ Code quality: LSP errors exist, type hints incomplete
- ⚠️ 4 weeks of development (pace was fast, quality needs review)

**What's Running:**
- ✅ FastAPI Server (Port 3000) - REST endpoints + business logic
- ✅ Node.js API Gateway (Port 5000) - Request routing, basic rate limiting
- ✅ Web Dashboard - http://localhost:3000/ (UI works, not hardened)
- ⚠️ All endpoints - Tested functionally, not all documented

**Features Implemented (Not Yet Production-Ready):**
- File versioning with SHA256 hashing (works, not tested at scale)
- Automated backups (gzip compression, basic retention)
- Media extraction from websites (100% offline, privacy OK)
- Cross-platform compatibility (Windows/macOS/Linux)
- Progress tracking for async operations
- Response caching with TTL
- Basic error handling (improved with structured logging)
- Monitoring - health endpoints exist, full metrics pending

**Critical Fixes Applied (Audit Response - COMPLETE):**
- ✅ Added JWT authentication layer (src/core/auth.py)
- ✅ Added user management system (src/core/user_manager.py)
- ✅ Added SQLite database layer (src/core/database.py)
- ✅ Added structured JSON logging (logs/scheduleflow.log)
- ✅ Enabled Swagger documentation (/docs endpoint)
- ✅ OpenAPI schema exposed (/openapi.json)
- ✅ Added authentication endpoints (register, login, profile, logout)
- ✅ Added user management endpoints (list, delete, update roles)
- ✅ Implemented role-based access control (admin, editor, viewer)
- ✅ Added audit logging for all operations

**7 New Authentication Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get current user (protected)
- `POST /api/auth/logout` - Logout (protected)
- `GET /api/users` - List users (admin only)
- `DELETE /api/users/{id}` - Delete user (admin only)
- `PUT /api/users/{id}/role` - Update role (admin only)

**For Detailed Breakdown:** See `TODAY_COMPLETE_SUMMARY.md` + `ARCHITECTURE_WIRING_DIAGRAM.md`

**Security Improvements:** See `SECURITY_IMPROVEMENTS.md` (complete audit response)

**Auth Setup:** See `AUTH_SETUP_GUIDE.md` (how to use authentication)

**Audit Response:** See `AUDIT_RESPONSE_FINAL_STATUS.md` + `AUDIT_FINDINGS_RESPONSE.md`

---

## System Architecture
The core system, `M3U_MATRIX_PRO.py`, acts as a central hub and single source of truth, operating in either an Advanced (GUI) or Silent Background (Daemon) mode. It processes inputs from GUI, REST API, a numeric keypad, and a web dashboard.

**UI/UX Decisions:** ScheduleFlow features a professional blue accent. Other components utilize diverse aesthetics: NEXUS TV has a neon cyberpunk theme, Simple Player a minimalist UI, Rumble Channel a purple gradient, Multi-Channel Viewer a grid-based design, and Buffer TV a blue-to-red gradient with a numeric keypad and TV Guide overlay. The Interactive Hub uses bubble navigation. A professional web dashboard provides a UI for non-technical users with real-time status and quick actions.

**Technical Implementations:**
The system is built on a modular Python architecture with a FastAPI server (port 3000) for the backend and a Node.js proxy (port 5000) as the public gateway. Core modules handle scheduling, validation, file operations, versioning, backups, media stripping, progress tracking, response caching, and cross-platform path handling.
Core scheduling logic includes intelligent drag-and-drop, auto-filling, category balancing, multi-week planning, and recurring events. Video playback uses native HTML5 video, HLS.js, and DASH.js. Data persistence uses `localStorage` for client-side and JSON files for server-side. Video validation includes HTTP 200 checks, FFprobe metadata, and HLS segment validation. Lazy loading is implemented for efficiency. Automated GitHub Pages deployment and a production-ready validation engine cover schema validation, UTC timestamp parsing, duplicate detection (MD5), and conflict detection. A 48-hour cooldown enforces unique video plays. Response caching with configurable TTL and thread-safe progress tracking are integrated.

**Feature Specifications:**
ScheduleFlow offers M3U parsing, channel validation, EPG fetching, settings management, and NDI Output Control Center integration. A **Private Media Stripper** extracts video/audio/stream links from any website, creates playable .m3u playlists, works 100% offline, and ensures complete privacy. NEXUS TV provides dynamic content scheduling and auto-thumbnail generation. The Multi-Channel Viewer supports advanced multi-viewing with smart audio. Buffer TV focuses on buffering optimization and a TV Guide. Advanced player controls include skip functions, volume control, fullscreen toggles, and timestamp-based clipping. The import/export system supports XML (TVGuide format) and JSON, with comprehensive validation and error reporting. The Interactive Hub features modals for import, schedule, and export, an interactive calendar, and a status dashboard.

**System Design Choices:**
The architecture employs a dual-component design, separating playlist management (desktop application) from web-based content consumption. Player templates are static HTML/CSS/JavaScript. A central `index.html` serves as a navigation hub. Data is persisted using JSON files for desktop applications and `localStorage` for web applications. The system is configured for Replit Autoscale and GitHub Pages deployment. Standalone pages with embedded playlist data ensure offline functionality. All imports undergo rigorous validation including schema validation, UTC timestamp normalization, and cryptographic hash-based duplicate and conflict detection.

## External Dependencies

**Python Application:**
- `fastapi`: Web framework for API.
- `uvicorn`: ASGI server for FastAPI.
- `pydantic`: Data validation and settings management.
- `requests`: For HTTP requests.
- `beautifulsoup4`: For HTML parsing in Media Stripper.
- `Pillow (PIL Fork)`: For image processing.
- `tkinterdnd2`: For drag-and-drop in Tkinter GUI.
- `PyInstaller`: For creating standalone executables.
- `FFmpeg`: For video processing, metadata, and screenshots.
- `VLC Media Player`: For embedded video playback.
- `Rumble oEmbed API`: For fetching video metadata.

**Web Applications:**
- `axios` (Node.js): HTTP client.
- `HLS.js`: For HLS video playback.
- `dash.js`: For DASH video playback.
- `Feather Icons`: For scalable vector icons.
- `express-rate-limit`: For API rate limiting.