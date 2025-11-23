# M3U MATRIX PRO - Complete IPTV Management Suite

## 🚀 Overview
M3U MATRIX PRO is a powerful desktop application for managing, organizing, and editing M3U/M3U8 IPTV playlists. Built with Python and Tkinter, it offers advanced features for playlist management, channel validation, EPG integration, and more.

## ✨ Features

### Core Functionality
- **Drag & Drop Reordering** - Visually reorganize channels by dragging rows
- **Live Channel Checking** - Validate channel URLs to find broken streams
- **M3U Parsing** - Robust parser supporting EXTINF, EXTGRP, and custom tags
- **TV Guide Integration** - Fetch and parse XMLTV EPG data
- **Multi-File Support** - Load and merge multiple M3U playlists
- **Smart Organization** - Auto-group channels, remove duplicates, normalize names

### Advanced Features
- **Cut/Copy/Paste** - Full clipboard support for channel management
- **Inline Editing** - Double-click to edit channel properties
- **URL Import** - Download playlists directly from remote URLs
- **CSV Export** - Export channel data to spreadsheet format
- **Regex Search** - Advanced filtering with regular expression support
- **Multi-Column Sorting** - Sort by number, name, group, URL, or custom fields
- **Backup URLs** - Track multiple URLs per channel
- **Custom Tags** - Support for non-standard M3U tags

## 🎮 How to Use

### Starting the Application
```bash
./run_m3u_matrix.sh
```
Or:
```bash
python3 M3U_MATRIX_PRO.py
```

### Loading Playlists
1. Click **LOAD** button
2. Select one or more M3U/M3U8 files
3. Channels appear in the matrix view

### Organizing Channels
1. Click **ORGANIZE** to:
   - Remove duplicate channels
   - Normalize group names
   - Auto-increment channel numbers
   - Sort alphabetically

### Checking Channel Status
1. Click **CHECK** to validate all channel URLs
2. Wait for the audit to complete
3. Review results showing working/broken channels
4. Broken channels marked with ✗, working with ✓

### Editing Channels
- **Drag to Reorder**: Click and drag rows to change order
- **Double-Click to Edit**: Click any cell to edit inline
- **Right-Click Menu**: Access additional options (Play, Copy URL, Delete, etc.)

### Importing from URL
1. Click **IMPORT URL**
2. Enter the M3U playlist URL
3. Channels automatically download and merge

### EPG Integration
1. Click **FETCH EPG**
2. Enter XMLTV format EPG URL
3. Schedule data populates automatically

### Exporting
- **SAVE**: Save as M3U file
- **EXPORT CSV**: Export to spreadsheet format

## ⌨️ Keyboard Shortcuts
- **Double-Click**: Edit channel property
- **Right-Click**: Context menu
- **Drag**: Reorder channels

## 📁 Project Structure
```
M3U_MATRIX_PRO/
├── M3U_MATRIX_PRO.py          # Main application
├── run_m3u_matrix.sh          # Launch script
├── logs/                      # Application logs
├── exports/                   # Exported playlists and CSV files
├── backups/                   # Backup copies
├── thumbnails/                # Channel logos cache
├── epg_data/                  # EPG XML cache
├── temp/                      # Temporary files
├── m3u_matrix_settings.json   # User settings (auto-created)
└── tv_guide.json              # TV schedule data (auto-created)
```

## 🛠️ Dependencies
- Python 3.11+
- tkinter (included with Python)
- requests
- pillow

All dependencies are automatically installed on Replit.

## 🎨 UI Overview

### Toolbar Buttons
- **LOAD**: Open M3U files
- **ORGANIZE**: Auto-organize channels
- **CHECK**: Validate channel URLs
- **SAVE**: Export M3U playlist
- **EXPORT CSV**: Export to CSV
- **IMPORT URL**: Download remote playlist
- **FETCH EPG**: Get TV guide data
- **GOLD**: Launch web player (coming soon)
- **TV GUIDE**: Edit schedule
- **NEW**: Clear all and start fresh

### Left Panel
- **Loaded Files**: List of imported M3U files
- **TV Guide Preview**: Shows current/upcoming programs

### Main Matrix
Columns:
- **#**: Channel number
- **Now Playing**: Current show (from EPG/schedule)
- **Next**: Upcoming show
- **Group**: Channel category
- **Name**: Channel name
- **URL**: Stream URL
- **Backs**: Number of backup URLs
- **Tags**: Custom tag count
- **Del**: Delete button

## 🔧 Advanced Usage

### Custom Tags
The parser automatically extracts any custom tags from M3U files:
```m3u
#EXTINF:-1 tvg-id="channel1" tvg-name="Channel 1",Channel 1
#EXTGRP:Movies
#CUSTOM-TAG:value
#ANOTHER-TAG:data
http://stream.url
```

### Regex Searching
Use `/pattern/` syntax for regex search:
```
/^HBO/        - Channels starting with HBO
/sports/i     - Case-insensitive sports search
/\d{4}/       - Channels with 4-digit numbers
```

### Schedule Management
1. Right-click channel → "Schedule Show"
2. Or double-click "Now Playing" column
3. Or use "TV GUIDE" button for bulk editing

### Batch Operations
1. Select multiple channels (Ctrl+Click)
2. Use CUT/COPY buttons
3. PASTE to move/duplicate channels

## 📝 Settings
Settings are automatically saved to `m3u_matrix_settings.json`:
- Window geometry
- Theme preferences
- Recent files
- Default EPG URL
- Auto-check options

## 🐛 Troubleshooting

### Application Won't Start
- Ensure Python 3.11+ is installed
- Check that dependencies are installed
- Review logs in `logs/m3u_matrix.log`

### Channels Not Loading
- Verify M3U file format
- Check file encoding (UTF-8 recommended)
- Review error messages in status bar

### EPG Not Working
- Ensure URL points to valid XMLTV format
- Check network connection
- Verify channel IDs match EPG data

## 📜 M3U Format Support

Supported Tags:
- `#EXTM3U` - Header
- `#EXTINF` - Channel info
- `#EXTGRP` - Group name
- `tvg-id` - EPG channel ID
- `tvg-name` - Channel name
- `tvg-logo` - Logo URL
- `group-title` - Category
- Custom tags (preserved during save)

## 🚀 Future Enhancements
- Web-based player integration
- Playlist sharing
- Cloud sync
- Auto-update broken channels
- Bulk URL replacement
- Channel preview thumbnails
- Multi-language support

## 📄 License
See LICENSE file for details.

## 💡 Tips
- Use ORGANIZE after loading multiple files to clean up
- CHECK channels before saving to remove dead streams
- Use groups to categorize channels logically
- Regular exports create backups automatically
- EPG data enhances TV guide functionality

---
**M3U MATRIX PRO** - Professional IPTV Playlist Management
