# Video Player Pro - Feature Documentation

## Core Features

### 1. Main Launcher Interface
- **Minimalist Design**: Clean, modern dark theme interface
- **Single Entry Point**: One-click launch button to access the player workbench
- **Feature Preview**: Quick overview of application capabilities on launch screen

### 2. Video Player Workbench

#### Dual-Panel Layout
- **Left Panel**: Playlist management with tree view
- **Right Panel**: Video player controls and information display

#### Playlist Management
- **Add Videos**: Individual file selection or batch import
- **Folder Scanning**: Recursive folder scanning for all video files
- **Supported Formats**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- **Auto-Save**: Playlist automatically saves on changes
- **Persistent Storage**: Playlist preserved between sessions

#### File Operations
- **Copy/Paste**: Copy selected videos and paste to duplicate entries
- **Delete**: Remove selected videos from playlist
- **Clear All**: Remove all videos with confirmation
- **Keyboard Shortcuts**:
  - `Ctrl+O`: Open videos
  - `Ctrl+C`: Copy selected
  - `Ctrl+V`: Paste videos
  - `Delete`: Remove selected

### 3. Video Metadata Extraction

#### FFmpeg Integration
Automatically extracts comprehensive video information:
- **Duration**: Precise video length in HH:MM:SS format
- **Resolution**: Width x Height (e.g., 1920x1080)
- **Codec**: Video codec information (H.264, HEVC, etc.)
- **File Type**: Extension-based type identification
- **File Size**: Size in megabytes

#### Metadata Display
- Playlist view shows: Title, Duration, Type
- Detailed info window displays all extracted metadata
- JSON export capability for metadata storage

### 4. Screenshot & Thumbnail System

#### Screenshot Capture
- **Single-Click Capture**: Screenshot button captures current frame
- **FFmpeg Processing**: High-quality JPEG screenshots
- **Automatic Timestamping**: Unique filename generation
- **Storage**: Dedicated screenshots/ directory

#### Metadata Generation
Each screenshot includes JSON metadata:
```json
{
  "video": "Video Title",
  "filepath": "/path/to/video.mp4",
  "timestamp": "20250116_143022",
  "screenshot": "screenshot_20250116_143022.jpg",
  "resolution": "1920x1080",
  "duration": "00:45:30",
  "capture_time": "2025-01-16T14:30:22.123456"
}
```

#### Automatic Thumbnails
- **Thumbnail Generation**: 320x180px thumbnails created automatically
- **Filename Convention**: `thumb_[timestamp].jpg`
- **Quality Optimization**: 85% JPEG quality for balance

### 5. Playback System

#### External Player Integration
- **System Default**: Uses OS default video player
- **Cross-Platform**: Windows, macOS, Linux support
- **Playlist Navigation**: Previous/Next buttons
- **Double-Click Play**: Play videos directly from playlist

#### Playback Controls
- Play/Pause toggle
- Previous video
- Next video
- Sequential playback support

### 6. Advanced Scheduling System

#### Schedule Generation
- **Start Time Configuration**: Set schedule start time (HH:MM)
- **Show Duration**: Configurable time slots (minutes)
- **Automatic Calculation**: Next show times calculated automatically
- **Predictive Scheduling**: Based on video lengths and time slots

#### Schedule Features
- **Time Slot Management**: Each video assigned a time slot
- **Next Show Prediction**: Displays when next show starts
- **Schedule Visualization**: Tree view with all schedule details
- **JSON Export**: Export schedule for external use

#### Schedule Display Columns
1. **Start Time**: When the video begins
2. **Title**: Video name
3. **Duration**: Actual video length
4. **Next Show**: Predicted next show start time

### 7. Data Management

#### Auto-Save System
- Playlist saves automatically on changes
- Persistent storage in `data/playlist.json`
- Recovery on application restart

#### Manual Save/Load
- **Save Playlist**: Export playlist as JSON
- **Load Playlist**: Import previously saved playlists
- **Format**: Human-readable JSON with full metadata

#### File Organization
```
video_player_app/
├── screenshots/          # Screenshot storage
│   ├── screenshot_*.jpg  # Full screenshots
│   ├── screenshot_*.json # Metadata files
│   └── thumb_*.jpg       # Thumbnails
├── data/                 # Application data
│   └── playlist.json     # Auto-saved playlist
```

## Technical Specifications

### Dependencies
- **Python 3.7+**: Core runtime
- **Tkinter**: GUI framework (built-in)
- **FFmpeg**: Video processing and metadata extraction
- **Pillow (PIL)**: Image processing for thumbnails

### Performance Optimizations
- **Threading**: Metadata extraction runs in background threads
- **Lazy Loading**: Videos processed as added, not all at once
- **Efficient Storage**: JSON format for fast read/write

### Error Handling
- Graceful failure for missing FFmpeg
- Validation for video file formats
- User-friendly error messages
- Timeout protection for FFmpeg operations

## Use Cases

### Video Collection Management
1. Import entire video folders
2. View video metadata at a glance
3. Organize with copy/paste operations
4. Save collections as reusable playlists

### Content Scheduling
1. Generate TV-style schedules
2. Plan viewing times
3. Predict show durations
4. Export schedules for publishing

### Screenshot Documentation
1. Capture key frames from videos
2. Generate thumbnails automatically
3. Store metadata for reference
4. Build visual catalogs

### Playlist Creation
1. Build custom video sequences
2. Reorder with ease
3. Duplicate entries as needed
4. Export for archival

## Future Enhancement Possibilities

- Drag & drop support (with tkinterdnd2)
- Built-in video player (VLC integration)
- Advanced search and filtering
- Tag-based organization
- Multi-schedule management
- Batch screenshot capture
- Video editing capabilities
- Network stream support
- Cloud storage integration
- Mobile companion app
