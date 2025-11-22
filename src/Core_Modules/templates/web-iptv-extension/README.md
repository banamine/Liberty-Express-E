# Web IPTV Player Template

## Overview
A modern, responsive IPTV player with channel list management, favorites, history tracking, and playlist analysis. This template is integrated into M3U Matrix Pro as an alternative to the NEXUS TV template.

## Features
- ✅ **Channel List Navigation** - Browse and select channels from sidebar
- ✅ **M3U Playlist Support** - Automatically parses M3U playlists with metadata
- ✅ **HLS & DASH Streaming** - Supports adaptive streaming protocols via CDN libraries
- ✅ **Favorites System** - Save and export favorite channels
- ✅ **History Tracking** - Recent channels saved to localStorage
- ✅ **Playlist Analysis** - View online/offline status and statistics
- ✅ **Search Functionality** - Filter channels by name
- ✅ **Theme Toggle** - Light/dark mode support
- ✅ **Local Time Display** - Shows current date and time
- ✅ **Responsive Design** - Works on desktop and mobile

## File Structure
```
web-iptv-extension/
├── player.html          # Main player interface
├── background.js        # Chrome extension service worker
├── manifest.json        # Chrome extension manifest
├── css/
│   └── styles.css       # Player styling
├── js/
│   └── app.js          # Player logic and M3U parsing
└── icons/
    ├── icon.svg        # Sample icon template
    └── README.txt      # Icon placeholder instructions
```

## Template Integration

### How It Works
1. User clicks "Generate Pages" in M3U Matrix Pro
2. Template selection dialog appears
3. User chooses "Web IPTV (Sequential Channel Player)"
4. M3U playlist data is injected into player.html
5. Complete folder structure is created in `generated_pages/`

### Generated Output
```
generated_pages/
└── [playlist_name]/
    ├── player.html       # Player with embedded playlist
    ├── manifest.json     # Chrome extension config
    ├── background.js     # Extension background script
    ├── css/
    │   └── styles.css
    ├── js/
    │   └── app.js
    └── icons/            # Add your custom icons here
```

## Using the Generated Player

### Option 1: Local Web Server (Recommended)
```bash
# Start web server
python -m http.server 8000

# Open in browser
http://localhost:8000/generated_pages/[playlist_name]/player.html
```

### Option 2: Direct File Access
```
Open: generated_pages/[playlist_name]/player.html
```
**Note:** Some streaming features may not work due to CORS restrictions

### Option 3: Chrome Extension
1. Load extension folder in Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select `generated_pages/[playlist_name]/` folder

## Customization

### Adding Custom Icons
Replace placeholder icons in the `icons/` folder:
- `icon16.png` - 16x16 pixels
- `icon48.png` - 48x48 pixels
- `icon128.png` - 128x128 pixels

You can convert the sample `icon.svg` using online tools or image editors.

### Modifying Styles
Edit `css/styles.css` to customize:
- Colors and themes
- Layout and spacing
- Fonts and typography
- Animations and transitions

### Extending Functionality
Edit `js/app.js` to add:
- Custom playlist formats
- Additional streaming protocols
- Enhanced channel metadata
- Advanced filtering options

## Supported Formats

### Video Protocols
- **HLS** (.m3u8) - HTTP Live Streaming
- **DASH** (.mpd) - Dynamic Adaptive Streaming
- **Direct** (.mp4, .webm, .ogg, etc.)

### Playlist Formats
- **M3U/M3U8** - Extended M3U with metadata
- **JSON** - Channel objects array
- **TXT** - Plain URL list

### M3U Metadata Support
The parser extracts:
- `tvg-name` - Channel name
- `tvg-logo` - Channel logo URL
- `group-title` - Channel category

## Browser Compatibility
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ⚠️ IE11 (Limited support)

## Dependencies (via CDN)
- **HLS.js v1.6.13** - HLS streaming support
- **Dash.js v5.0.0** - DASH streaming support
- **Feather Icons v4.29.2** - UI icons

All dependencies load from CDN - no local installation required!

## Comparison: Web IPTV vs NEXUS TV

| Feature | Web IPTV | NEXUS TV |
|---------|----------|----------|
| Channel List | ✅ Sidebar navigation | ✅ Grid layout |
| Playback Mode | Sequential/manual | 24-hour scheduled |
| Theme | Light/Dark toggle | Cyberpunk neon |
| Time Display | Current time | Timezone clocks |
| Favorites | ✅ Export to M3U | ❌ |
| History | ✅ localStorage | ❌ |
| Analysis | ✅ Online/offline stats | ❌ |
| Chrome Extension | ✅ Full support | ❌ |
| Best For | Channel browsing | Scheduled streaming |

## Troubleshooting

### Videos Won't Play
1. Check if web server is running (use Option 1)
2. Verify stream URLs are valid
3. Check browser console for CORS errors
4. Try different streaming protocol (HLS vs DASH vs direct)

### Channels Not Loading
1. Verify M3U playlist format is correct
2. Check that #EXTINF lines precede URLs
3. Ensure URLs don't have special characters
4. Check browser console for parsing errors

### Icons Missing
1. Add PNG icons to `icons/` folder
2. Use exact filenames: icon16.png, icon48.png, icon128.png
3. Reload extension in Chrome

## License
Part of M3U Matrix Pro project.

## Support
For issues or questions, refer to the main M3U Matrix Pro documentation.
