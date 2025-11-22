# Simple Player Template

## Overview
Clean, responsive video player with playlist support. Designed for straightforward video playback without time-based scheduling.

## Features

### Core Features
- **Clean Video-Focused Design** - Maximizes screen space for video content
- **Responsive Layout** - Works on desktop, tablet, and mobile devices
- **Grouped Playlist** - Organizes channels by category/group
- **Playback Modes**:
  - **Sequential** - Plays channels in order
  - **Shuffle** - Randomizes playback order
- **Auto-Advance** - Automatically plays next video when current ends
- **Manual Controls** - Previous/Next buttons for manual navigation
- **Playlist Modal** - Full-screen playlist view with category grouping
- **Mobile Optimized** - Touch controls and responsive UI

### Technical Features
- HLS.js integration for HLS stream support (.m3u8)
- Automatic error handling and skip-on-fail
- Loading indicators with retry logic
- Group-based channel organization
- Active channel highlighting
- Persistent playback state

## File Structure

```
templates/simple-player/
├── player.html          # Main HTML template
├── css/
│   └── styles.css       # Player styles
└── js/
    └── app.js          # Player logic
```

## Usage

### 1. Generate Player from M3U Matrix Pro
1. Load channels in M3U Matrix Pro
2. Click "GENERATE MY PAGE OUTPUT"
3. Select "Simple Player (Clean Video Player)"
4. Click "CONTINUE"
5. Choose "BY GROUP" or "ALL IN ONE"
6. Open generated page in `generated_pages/[name]/player.html`

### 2. Open in Browser
- Open `player.html` in any modern web browser
- No server required for local files
- For streaming URLs, serve via HTTP server:
  ```bash
  python -m http.server 8000
  # or
  npx serve
  ```

### 3. Playback Controls
- **Previous Button** - Go to previous channel
- **Next Button** - Go to next channel
- **Playlist Button** - Open full playlist view
- **Sequential/Shuffle** - Toggle playback mode
- **Video Controls** - Standard HTML5 video controls

## Playback Modes

### Sequential Mode (Default)
- Plays channels in order from first to last
- Loops back to beginning after last channel
- Predictable, consistent viewing order

### Shuffle Mode
- Randomizes playback order
- Ensures all channels play before repeating
- Unpredictable, varied viewing experience

## Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Customization

### Colors
Edit `css/styles.css`:
```css
/* Header/Footer */
.player-header { background: rgba(0, 0, 0, 0.9); }

/* Buttons */
.player-controls button { background: rgba(0, 0, 100, 0.8); }

/* Playlist Modal */
.playlist-modal { background: rgba(0, 0, 0, 0.95); }
```

### Layout
Adjust sizes in `css/styles.css`:
```css
.player-header { min-height: 60px; }
.player-footer { min-height: 50px; }
```

## Troubleshooting

### Video Won't Play
- Check if URL is accessible
- Try different playback mode
- Verify HLS.js is loaded for .m3u8 streams

### Playlist Not Showing
- Ensure channels have proper group metadata
- Check browser console for errors

### Mobile Issues
- Enable autoplay in browser settings
- Try muting video first (autoplay requirement)

## License
Part of M3U Matrix Pro - IPTV Management System

## Credits
- Based on responsive player template
- HLS.js for HLS stream support
- Built with vanilla JavaScript
