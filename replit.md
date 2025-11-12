# NEXUS TV - Classic Movies Channel

## Overview
NEXUS TV is a sophisticated 24-hour streaming television channel featuring classic movies with a futuristic neon cyberpunk interface. The application provides a schedule-based broadcast experience with automatic video playback, timezone support, and M3U playlist management capabilities.

**Status:** Fully configured and running on Replit
**Last Updated:** November 12, 2025

## Project Structure

### Main Files
- `index.html` - Complete NEXUS TV application (2036 lines, self-contained)
- `manifest.json` - PWA manifest for standalone installation
- `service-worker.js` - Service worker for offline caching

### Sample Content
- Various `.m3u` and `.m3u8` files - Classic movie playlists for testing

### Configuration
- `package.json` - Node.js dependencies (serve package)
- `.replit` - Replit configuration (nodejs-20, web)
- `.gitignore` - Git ignore patterns

## Features

### Core Functionality
- **24-Hour Schedule:** Automatic playback based on time-of-day schedule
- **Schedule-Based Playback:** Videos start at their scheduled time with correct elapsed time
- **M3U Playlist Support:** Load, replace, append, or randomly select playlists
- **Video Formats:** Supports MP4, HLS (.m3u8), MPEG-DASH (.mpd), and streaming URLs
- **Offline Capability:** All code and styles embedded in single HTML file

### User Interface
- **Neon Cyberpunk Design:** Futuristic interface with animated backgrounds and neon effects
- **Top Bar:** 
  - Thumbnail carousel showing previous, current, and upcoming programs
  - Real-time clock display
  - Channel name with gradient effects
  - Audio controls (mute/unmute, volume slider)
  - "Up Next" program information
- **Video Player:** Full-screen video with schedule-aware playback
- **Control Panel:** Slide-up menu with playback controls, playlist management, timezone clocks, and fullscreen
- **Title Bubble:** Auto-appearing notification when programs change
- **Splash Screen:** Daily schedule overview on page load

### Advanced Features
- **World Timezone Clocks:** Display current time in 6 major time zones (Local, New York, London, Tokyo, Sydney, Dubai)
- **Playlist Management:**
  - Replace current playlist
  - Append to existing playlist
  - Random playlist selection
  - Save/export playlist as M3U file
- **Keyboard Controls:**
  - Space: Play/Pause
  - F: Fullscreen toggle
  - T: Show timezone clocks
  - P: Open playlist manager
  - Escape: Close overlays/exit fullscreen
- **Auto-Refresh:** Midnight reset with countdown notification

## Running the Project

### Development
The project runs automatically when you start the Repl:
- Server: `npx serve -l 5000 --no-clipboard`
- Port: 5000
- Access: Via the Replit webview

### Deployment
Configured for Replit Autoscale deployment:
- Uses static file server (serve) for production
- Stateless web application (no server state)
- All assets embedded in single HTML file
- No database required

## Technical Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (all embedded in single file)
- **Video Player:** Native HTML5 video element
- **UI Framework:** Pure CSS with custom neon effects and animations
- **Fonts:** Orbitron (Google Fonts) for futuristic typography
- **Icons:** Font Awesome 6.4.0
- **Server:** Static file server (serve npm package)

## Schedule Data Structure

The application uses a schedule array with the following structure:
```javascript
{
    title: "Movie Title",
    logo: "thumbnail_url",
    video: "video_url", 
    start_time: "HH:MM",
    end_time: "HH:MM"
}
```

Default schedule includes 12 classic movies spanning a 24-hour period.

## Playlist Format

M3U playlists should follow this format:
```
#EXTM3U
#EXTINF:-1 tvg-logo="thumbnail_url",Movie Title
video_url
```

The parser automatically calculates start/end times based on 30-minute default duration.

## Browser Storage
The application does not use localStorage or cookies - all state is runtime-based and resets with page refresh.

## Known Features
- Fully self-contained single HTML file (no external CSS/JS dependencies except CDN resources)
- Automatic video synchronization based on schedule
- Smooth transitions between programs
- Responsive to window hover for control panel visibility
- Neon glow effects and animated backgrounds

## Recent Changes
- November 12, 2025: Initial Replit setup
  - Deployed complete NEXUS TV template (2036 lines)
  - Configured workflow for port 5000
  - Set up deployment configuration for Autoscale
  - Created .gitignore for Node.js
  - Removed old IPTV player files (app.js, script.js, styles.css)

## User Preferences
None recorded yet.

## Future Improvements
- Add EPG (Electronic Program Guide) data integration
- Implement recording/timeshift capabilities
- Add chapter markers for movies
- Support for multiple channels
- User-customizable color themes
- WebSocket support for live schedule updates
