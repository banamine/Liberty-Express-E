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
- **Code Audit:** Under-claim, never hallucinate. Verify before claiming functionality works.

## Fixed Issues & Implementation (Nov 22, Session 3)
### ✅ PRODUCTION-READY IMPORT/EXPORT/SCHEDULE SYSTEM
**Status:** COMPLETE with full validation, UTC normalization, duplicate detection, conflict detection

#### What Was Implemented:
1. **Schedule Validators** - XML/JSON schema validation with error reporting
   - Validates root elements, event structure, required fields
   - Detects malformed XML (rejects parse errors)
   - Validates JSON schema (checks object structure, required fields)

2. **Timestamp Parser** - ISO 8601 parsing with UTC normalization
   - Parses formats: 2025-11-22T10:00:00Z, 2025-11-22T10:00:00-05:00, 2025-11-22T10:00:00+01:00
   - Converts all timezones to UTC
   - Returns consistent ISO 8601 UTC strings (e.g., 2025-11-22T15:00:00Z)

3. **Duplicate Detector** - Cryptographic hash-based detection
   - Uses MD5(title:start_time) for duplicate identification
   - Detects exact duplicates (same title + same start time)
   - Removes duplicates from imported schedules, reports count

4. **Conflict Detector** - Overlapping timeslot detection
   - Detects all overlapping event pairs
   - Returns conflict details (event indices, titles, start/end times)
   - Reports conflicts in import result

5. **Import Functions**
   - `import_schedule_xml(filepath)` - Import TVGuide XML with validation
   - `import_schedule_json(filepath)` - Import schedule JSON with validation
   - `import_m3u(filepath)` - Import M3U playlists (simple format)
   - All return: schedule_id, events_imported, duplicates_removed, conflicts_detected

6. **API Endpoints**
   - `POST /api/import-schedule` - Trigger import (XML or JSON)
   - `GET /api/schedules` - List all imported schedules with validation metadata
   - `GET /api/playlists` - List all playlists
   - All endpoints call Python backend via subprocess

#### Audit Test Results (Nov 22, 2025):
✅ **Test 1: Malformed XML Rejection**
- Input: Incomplete XML (missing closing tags)
- Expected: Parse error, error status
- Result: PASS - Returns `{"status":"error","type":"parse_error",...}`

✅ **Test 2: Timezone Normalization**
- Input: 3 events in different timezones (-05:00, +01:00, Z)
- Expected: All times converted to UTC
- Result: PASS - 2025-11-22T10:00:00-05:00 → 2025-11-22T15:00:00Z, 2025-11-22T10:00:00+01:00 → 2025-11-22T09:00:00Z

✅ **Test 3: Duplicate Detection**
- Input: 3 events (1 duplicate: "Morning Show" imported twice with same start time)
- Expected: 1 duplicate removed, returned in warnings
- Result: PASS - `"duplicates_removed": 1, "warnings": {"duplicates": [...]}` with event data

✅ **Bonus Test 4: Conflict Detection**
- Input: 2 overlapping events (Morning Show 15:00-17:00, Afternoon Special 14:00-16:00)
- Expected: Overlap detected
- Result: PASS - `"conflicts_detected": 1` with event pair details

#### Files Created/Modified:
- **M3U_Matrix_Pro.py** (v2.1.0)
  - Added: TimestampParser, ScheduleValidator, DuplicateDetector, ConflictDetector classes
  - Added: `import_schedule_xml()`, `import_schedule_json()`, `_extract_xml_event()` methods
  - All using Python stdlib only (xml.etree.ElementTree, datetime, hashlib, uuid)
  - CLI arguments: `--import-schedule-xml FILE`, `--import-schedule-json FILE`
  - Removed Flask dependency (was failing)

- **api_server.js**
  - Added: `/api/import-schedule` (POST)
  - Added: `/api/schedules` (GET)
  - Added: `/api/playlists` (GET)
  - All call Python backend via subprocess spawn

- **Schedules Storage**
  - Each imported schedule saved to `schedules/{schedule_id}.json`
  - Metadata includes: total_imported, duplicates_removed, conflicts_detected
  - Warnings stored: duplicate events, conflict pairs with full details

#### Known Limitations:
- No conflict resolution (auto-merge, time-shift, etc.) - only detection
- No XSD validation for XML (uses loose schema validation)
- No database (uses JSON files in filesystem)
- No UI for viewing/editing conflict details (data is stored, awaiting UI)

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
- **Interactive Hub:** Control dashboard with bubble navigation for managing playlists, schedules, exports, and players.

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
- **Schedule Validation Engine:** Production-ready import/export with XML/JSON schema validation, timestamp parsing, timezone normalization, duplicate detection, and conflict detection.

### Feature Specifications
- **ScheduleFlow:** Core M3U parsing, channel validation, EPG fetching, settings management, error handling, XSS prevention, URL validation, Rumble URL detection, Navigation Hub integration, and NDI Output Control Center.
- **NEXUS TV:** Dynamic content scheduling, responsive UI, auto-midnight schedule refresh, channel analysis, favorites export, and auto-thumbnail generation with IndexedDB.
- **Multi-Channel Viewer:** Advanced multi-viewing with grid layout selector, smart audio management, configurable rotation scheduler, and focus mode.
- **Buffer TV:** Buffering optimization, numeric keypad, adjustable load timeout/retry delay, automatic retry, TV Guide, and quick category access.
- **Advanced Player Controls:** Includes features like skip forward/backward (10s, 20s, 30s, 1m), full-range volume control, fullscreen toggle, multi-screen grid viewing (up to 6 videos), auto-hiding control bars, timestamp-based video clipping, and screenshot capture.
- **Import/Export/Schedule System:** XML/JSON validation, ISO 8601 timestamp parsing with UTC normalization, MD5-based duplicate detection, overlapping timeslot detection, comprehensive error reporting.
- **Audit Report:** Generates a comprehensive report detailing test coverage, function status, code quality, and cleanup.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop application) from content consumption (web players).
- **Static Web Server:** All player templates run as static HTML/CSS/JavaScript files.
- **Navigation Hub System:** Central `index.html` for managing and navigating generated player pages.
- **Local Persistence:** Data is persisted using JSON files for desktop apps and `localStorage` for web apps.
- **Automated Deployments:** Configured for Replit Autoscale deployment and GitHub Pages.
- **Standalone Page Generation:** Self-contained generated pages with embedded playlist data and bundled dependencies for offline functionality.
- **Production-Ready Validation:** All imports validated against schema, timestamps normalized to UTC, duplicates detected via cryptographic hashing, conflicts detected via interval overlap detection.

## External Dependencies

### Python Application (M3U Matrix Pro & Video Player Pro)
- **requests:** For HTTP requests.
- **Pillow (PIL Fork):** For image processing.
- **tkinterdnd2:** For drag-and-drop functionality in Tkinter.
- **PyInstaller:** For creating standalone executables.
- **FFmpeg:** For video processing, metadata extraction, and screenshot generation.
- **VLC Media Player:** For embedded video playback.
- **Rumble oEmbed API:** Public API for fetching video metadata.
- **Python stdlib only for import/export:** xml.etree.ElementTree, datetime, hashlib, uuid, json, pathlib (NO Flask, NO external dependencies)

### Web Applications (All Player Templates)
- **npx serve:** (Optional) For static file serving during development/testing.
- **HLS.js:** For HLS (HTTP Live Streaming) playback.
- **dash.js:** For DASH (Dynamic Adaptive Streaming over HTTP) playback.
- **Feather Icons:** For scalable vector icons.
- **System Fonts:** Standard browser fonts used for text rendering.

## API Endpoints (ScheduleFlow v2.1.0)

### System Management
- `GET /api/system-info` - Returns version, page count, platform info
- `GET /api/pages` - Lists all generated HTML player pages

### Playlists (M3U Format)
- `GET /api/playlists` - Lists all imported playlists
- `POST /api/save-playlist` - Save playlist items to M3U file

### Schedules (XML/JSON)
- `GET /api/schedules` - Lists all imported schedules with validation metadata
- `POST /api/import-schedule` - Import schedule from XML/JSON file with validation

### Configuration
- `GET /api/config` - Retrieve current configuration
- `POST /api/config` - Update configuration

All API endpoints return JSON with status field and detailed error messages.
