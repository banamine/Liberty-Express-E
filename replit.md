# Web IPTV Player

## Overview
Web IPTV Player is a Chrome extension and standalone web application that allows users to stream IPTV channels. The app supports M3U playlists, direct video streams (HLS, MPEG-DASH, MP4), and provides features like favorites, history, and playlist management.

**Status:** Fully configured and running on Replit
**Last Updated:** November 12, 2025

## Project Structure

### Main Files
- `index.html` - Main HTML entry point for the web application
- `script.js` - Main application logic using VideoJS player
- `styles.css` - Application styling
- `manifest.json` - PWA manifest for standalone installation
- `service-worker.js` - Service worker for offline caching

### Additional Files
- `app.js` - Alternative implementation (not currently used)
- Various `.m3u` and `.m3u8` files - Sample IPTV playlists

### Configuration
- `package.json` - Node.js dependencies (serve package)
- `.replit` - Replit configuration
- `.gitignore` - Git ignore patterns

## Features

### Core Functionality
- **Playlist Support:** M3U, JSON, TXT formats
- **Stream Types:** HLS (.m3u8), MPEG-DASH (.mpd), MP4, and more
- **Video Player:** VideoJS-based player with full controls
- **Favorites:** Save and manage favorite channels
- **History:** Track previously loaded playlists
- **Drag & Drop:** Upload playlist files via drag and drop
- **Keyboard Controls:** 
  - Space: Play/Pause
  - Arrow keys: Navigate channels and volume
  - +/- : Adjust playback speed
- **Numeric Keypad:** Quick channel switching (like a TV remote)

### UI Features
- Responsive sidebar with playlist and favorites
- Dark theme interface
- Mobile-friendly design
- Sortable playlist items
- Closed captions toggle

## Running the Project

### Development
The project runs automatically when you start the Repl:
- Server: `npx serve -l 5000 --no-clipboard`
- Port: 5000
- Access: Via the Replit webview

### Deployment
Configured for Replit Autoscale deployment:
- Uses the same serve command for production
- Stateless web application (no server state)
- All data stored in browser localStorage

## Technical Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Video Player:** VideoJS 8.5.2
- **Streaming:** HLS.js for HLS streams
- **UI Libraries:** 
  - SortableJS for drag-and-drop sorting
  - Feather Icons (via CDN)
- **Server:** Static file server (serve)

## Browser Storage
The application uses localStorage for:
- Playlist data
- Favorites list
- Viewing history
- Theme preferences

## Known Limitations
- The project contains two different JavaScript implementations (app.js and script.js) - currently using script.js with VideoJS player
- Service worker cache list may reference files that don't exist but won't break functionality
- VideoJS initialization warning in console (minor, doesn't affect functionality)

## Recent Changes
- November 12, 2025: Initial Replit setup
  - Renamed main HTML file to index.html
  - Fixed stylesheet reference from style.css to styles.css
  - Updated service-worker.js to reference correct files
  - Configured workflow for port 5000
  - Set up deployment configuration
  - Created .gitignore for Node.js

## User Preferences
None recorded yet.

## Future Improvements
- Add missing PWA icon assets
- Consolidate app.js and script.js implementations
- Add more comprehensive error handling
- Add EPG (Electronic Program Guide) support
- Add recording/timeshift capabilities
