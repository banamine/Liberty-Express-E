# M3U MATRIX ALL-IN-ONE - IPTV Management & Streaming Platform

## Overview
This project delivers a comprehensive IPTV solution, integrating a professional M3U playlist manager (Python desktop application) with multiple futuristic streaming TV players (web interfaces). The platform aims to provide robust tools for managing, organizing, and playing streaming content, catering to users who demand advanced control over their IPTV experience. The vision is to offer a seamless and engaging content consumption experience through efficient playlist management and an immersive streaming environment.

The platform includes M3U MATRIX PRO, a desktop application for playlist management, and several web player templates: NEXUS TV (24-hour scheduled player), Web IPTV (sequential channel player), Simple Player (clean video-focused player), Multi-Channel Viewer (1-6 simultaneous channels with smart audio management), Rumble Channel (dedicated Rumble video player), and Buffer TV (TV player with buffering controls and numeric keypad). Additionally, it features Video Player Pro, a standalone vanilla Python video player application with advanced scheduling, screenshot capture, and metadata extraction capabilities. NEW: Professional NDI (Network Device Interface) output enables broadcast-grade video-over-IP streaming to production systems like OBS Studio, vMix, Wirecast, and TriCaster for professional live production workflows.

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
- **M3U MATRIX PRO:** Utilizes Tkinter for a native desktop application, prioritizing functionality and ease of use for playlist management.
- **NEXUS TV:** Features a neon cyberpunk aesthetic with animations for an immersive 24-hour streaming experience, including a thumbnail carousel, fullscreen player, world timezone clocks, and a theme toggle.
- **Simple Player:** Offers a clean, responsive, and minimalist UI focused solely on video content, with sequential and shuffle playback.
- **Rumble Channel:** Dedicated player for Rumble videos with a purple gradient design, sequential iframe playback, a playlist sidebar with thumbnails, and keyboard navigation.
- **Multi-Channel Viewer:** Revolutionary grid-based player supporting 1-6 simultaneous video channels with responsive CSS Grid layout, smart audio management (only one channel plays audio at a time with visual indicator), time-based rotation scheduler, focus mode for fullscreen expansion, and comprehensive keyboard controls. Features blue gradient design with channel-specific controls.
- **Buffer TV:** TV player with advanced buffering controls featuring a blue-to-red gradient (#003366 to #990000), numeric keypad for channel selection (0-9, +10, +20), adjustable load timeout and retry delay settings, TV Guide overlay, quick category buttons, and HLS.js streaming support.
- **Video Player Pro:** Features a minimalist launcher GUI and an advanced dual-panel workbench for video management.

### Technical Implementations
- **M3U MATRIX PRO:** Built with Python 3.11 and Tkinter. Features include drag & drop, live validation, smart playlist organization, EPG integration (XMLTV), remote URL import, regex search, auto-save, UUID tracking, and a Timestamp Generator. It includes a Smart TV Scheduler for 7-day schedule generation and an Enhanced Import System supporting various file types and URLs. It also incorporates an installer system, automatic thumbnail caching, Undo/Redo, JSON export, and template generation for all player types. Notably, it includes deep Rumble integration for automatic URL detection, oEmbed API metadata fetching (title, thumbnail, dimensions), and enrichment with PROVIDER, VIDEO_ID, PUB_CODE, and EMBED_URL tags. NEW: Rumble Category Browser - Visual channel discovery tool with 30 pre-loaded Rumble channel references organized by 11 categories (Conspiracy, News, Politics, Religious, Comedy, Commentary, Documentary, Health, Financial, Journalism, History), search/filter functionality, and one-click import to playlist. Note: Browser imports channel page references (TYPE='CHANNEL_REF') for browsing Rumble content, not individual playable videos. For video imports, use regular M3U import with Rumble video URLs. NEW: NDI Output Control Center - Professional broadcast integration via Network Device Interface for sending multiple video streams over IP to production systems like OBS Studio and vMix.
- **NEXUS TV:** Developed using HTML5, CSS3, and Vanilla JavaScript with the native HTML5 video element. It features a 24-hour auto-scheduled playback system, PWA configuration, HLS.js and DASH.js integration, a favorites system, history tracking, channel search, URL encryption/sharing, and uses FFmpeg for local file analysis. **UPDATED - Offline Support:** Playlist data now embedded directly in generated HTML via {{EMBEDDED_CHANNELS}} placeholder, enabling 100% offline playback with file:// protocol support. Falls back to embedded data if network fetch fails.
- **Simple Player:** A clean, responsive HTML5 video player using vanilla JavaScript and HLS.js for .m3u8 streams. It supports sequential and shuffle playback, group-based playlist organization, auto-advance, and is mobile-optimized.
- **Rumble Channel:** A dedicated Rumble video player using iframe embedding for sequential playback. It features automatic Rumble URL detection, oEmbed API integration for metadata, playlist sidebar with thumbnails, keyboard navigation, and auto-advance. Security features include XSS prevention via DOM methods, URL validation for rumble.com/embed URLs, and JSON escaping. It stores metadata offline, with videos streaming from Rumble.com.
- **Multi-Channel Viewer:** Developed using HTML5, CSS3 Grid, and Vanilla JavaScript. Supports flexible grid layouts (1-6 channels) with dynamic channel addition/removal. Features smart audio controller (single active audio source), time-based rotation system (5-60 min intervals), focus mode for fullscreen expansion, HLS.js and DASH.js integration for multi-format streams, keyboard shortcuts (1-6 for audio switching, SPACE for play/pause all, ESC to exit focus), and mobile-responsive design with touch controls. Includes configuration dialog for default channel count selection.
- **Buffer TV:** Developed using HTML5, CSS3, and Vanilla JavaScript with HLS.js integration. Features a numeric keypad (0-9, +10, +20 buttons) for direct channel selection, configurable buffering controls (load timeout 5-30s, retry delay 1-10s), TV Guide overlay showing all channels with categories, quick category buttons (Movies, Entertainment, Documentary, Music), CORS proxy support for remote streams, automatic stream retry with fallback handling, progress bar with time display, full video controls, and previous/next channel navigation. GUI accessible via "BUFFER TV" button (crimson red) in M3U Matrix Pro toolbar with configuration dialog for page name.
- **Video Player Pro:** A standalone Python desktop application using Tkinter, FFmpeg, and VLC. Key features include advanced import (M3U/M3U8, TXT, video/audio files, folder scanning), file management, FFmpeg-based metadata extraction, a screenshot system with JSON metadata, smart scheduling, playlist persistence (JSON), and cross-platform compatibility. An embedded VLC player supports in-app video playback, live screenshot capture, and real-time video info. NEW: Persistent settings system with user-selectable save folders (screenshots, metadata JSON, thumbnails) that remember selections across sessions, and TV Guide export functionality that creates M3U Matrix Pro-compatible JSON files for seamless integration between Video Player Pro and M3U Matrix Pro.

### Feature Specifications
- **M3U MATRIX PRO:** Core functionalities include M3U parsing, channel validation, EPG fetching, settings management, error handling, security (XSS prevention, URL validation), and Rumble URL detection with oEmbed API integration. Navigation Hub integration with "NAV HUB" button (gold #FFD700) in toolbar Row 1 opens the central hub page for managing all generated player pages. Rumble Category Browser accessible via "RUMBLE BROWSER" button (tomato #FF6347) in toolbar Row 2 provides visual channel discovery with grid cards, category filtering, search functionality, and instant playlist import. NEW: NDI Output Control Center accessible via "🔴 NDI" button (red #FF0000) in toolbar Row 2 provides professional broadcast-grade streaming with multi-channel NDI output management, real-time status monitoring, resolution/framerate configuration (1080p@30fps default), and integration with production systems like OBS Studio, vMix, Wirecast, and TriCaster.
- **NEXUS TV:** Provides dynamic content scheduling, a responsive UI, automatic midnight schedule refresh, channel analysis, favorites export as M3U, and auto-thumbnail generation with IndexedDB.
- **Rumble Channel:** Specialized player for Rumble videos with automatic URL normalization, metadata fetching, secure iframe embedding, and standalone page generation.
- **Multi-Channel Viewer:** Advanced multi-viewing player with grid layout selector (1, 2, 3, 4, or 6 channels), smart audio management system, configurable rotation scheduler with visual timer, focus mode controls, play all/pause all/mute all functions. GUI accessible via "MULTI-CHANNEL" button (blue) in M3U Matrix Pro toolbar with configuration dialog for page name and default channel count.
- **Buffer TV:** TV player with buffering optimization featuring numeric keypad channel selection, adjustable load timeout (5-30 seconds) and retry delay (1-10 seconds), automatic retry with multiple fallback options, TV Guide with all channels and categories, quick category access buttons, and standalone page generation. GUI accessible via "BUFFER TV" button (crimson red #DC143C) in M3U Matrix Pro toolbar with configuration dialog for page name.
- **Auto-Thumbnail System:** Built-in across all player templates, capturing two screenshots per video (25% and 75% playtime) automatically during playback. Thumbnails are stored in IndexedDB (browser storage) with separate databases per page and support HLS, DASH, and direct stream formats.

### System Design Choices
- **Dual-Component Architecture:** Separates playlist management (desktop app) from content consumption (web player).
- **Static Web Server:** All player templates run as static file servers.
- **Navigation Hub System:** Central hub page (`generated_pages/index.html`) serves as a splash screen and navigation center for all generated pages. Features include:
  - **Organized Folder Structure:** Pages organized by template type (`nexus_tv/`, `buffer_tv/`, `multi_channel/`, `web_iptv/`, `simple_player/`, `rumble_channel/`)
  - **Back to Hub Button:** All generated pages include a floating "🏠 Hub" button (top-left) linking back to the navigation hub
  - **Sample Channels Library:** 10 free demo video channels (Big Buck Bunny, Sintel, etc.) for quick testing
  - **Bookmarks Export:** Generate browser-compatible HTML bookmarks file organized by template type
  - **Auto-Cleanup:** Configurable retention system to delete pages older than N days
  - **Statistics Dashboard:** Shows total pages, recent activity, and page counts per template
  - **Quick Access:** "NAV HUB" button (gold #FFD700) in M3U Matrix Pro toolbar Row 1 opens hub in browser
- **Local Persistence:** M3U Matrix Pro persists settings and data locally in JSON files and dedicated directories.
- **Automated Deployments:** Configured for Replit Autoscale deployment for the web player.
- **Standalone Page Generation:** All generated pages are self-contained with embedded playlist data and bundled dependencies, requiring no external CDNs.
- **Offline-First Design:** Pages work 100% offline for local video files, with zero external dependencies except for remote video stream URLs. **NEW - file:// Protocol Support:** All page generators now embed playlist data directly in HTML, eliminating fetch() calls that fail with file:// protocol. Pages are fully functional when opened locally via file:// without any web server.

## External Dependencies

### Python Application (M3U Matrix Pro & Video Player Pro)
- **requests:** For making HTTP requests (e.g., channel validation, remote URL import, EPG fetching, Rumble oEmbed API).
- **Pillow (PIL Fork):** For image processing (e.g., handling channel logos/thumbnails, image verification).
- **tkinterdnd2:** For drag-and-drop functionality in the GUI.
- **PyInstaller:** For creating standalone Windows executables.
- **FFmpeg:** Used by Video Player Pro for video processing, metadata extraction, and screenshot generation.
- **VLC Media Player:** Required for embedded video playback functionality within Video Player Pro.
- **Rumble oEmbed API:** Public API endpoint (https://rumble.com/api/Media/oembed.json) for fetching video metadata. No authentication required.

### Web Applications (All Player Templates)
- **npx serve:** Node.js package used to serve static files for the web interface (optional).
- **HLS.js (Bundled):** For HLS stream playback.
- **dash.js (Bundled):** For DASH stream playback.
- **Feather Icons (Bundled):** For icons in Web IPTV.
- **System Fonts:** Used by NEXUS TV for offline compatibility.