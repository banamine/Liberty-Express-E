# 🎬 M3U MATRIX ALL-IN-ONE
## Professional IPTV Management & Streaming Platform

### ✨ NEW: Simplified Folder Structure & NDI Broadcast Support!
The project has been completely reorganized for easier navigation and includes professional broadcast capabilities.

---

## 🚀 Quick Start

### Windows Users:
1. **Launch M3U Matrix Pro**: Double-click `LAUNCH_M3U_MATRIX_PRO.bat`
2. **Launch Video Player Pro**: Double-click `LAUNCH_VIDEO_PLAYER_PRO.bat`

### Linux/Mac Users:
1. **Launch M3U Matrix Pro**: Run `./launch_m3u_matrix_pro.sh`
2. **Launch Video Player Pro**: Run `./launch_video_player_pro.sh`

---

## 📁 Clean & Organized Project Structure

```
M3U_MATRIX_ALL_IN_ONE/
│
├── 📱 Applications/              ← Main Applications Here!
│   ├── M3U_MATRIX_PRO.py       (IPTV Playlist Manager)
│   └── VIDEO_PLAYER_PRO.py     (Media Player Workbench)
│
├── 🌐 Web_Players/              ← All Web Player Templates
│   ├── nexus_tv.html           (24-hour Scheduled Player)
│   ├── buffer_tv.html          (TV with Buffering Controls)
│   ├── multi_channel.html      (1-6 Simultaneous Channels)
│   ├── simple_player.html      (Clean Video Player)
│   ├── web_iptv.html          (Sequential Channel Player)
│   ├── rumble_channel.html    (Rumble Video Player)
│   ├── stream_hub.html        (Live TV Hub)
│   └── standalone_secure.html (Secure Standalone Player)
│
├── 📦 Core_Modules/             ← Core Python Libraries
│   ├── page_generator.py      (Page Generation Engine)
│   ├── ndi_output.py          (NDI Broadcast Support)
│   ├── output_manager.py      (File Management)
│   └── page_generator_fix.py  (Runtime Fixes)
│
├── 💾 M3U_Matrix_Output/        ← All Generated Content
│   ├── generated_pages/        (Your Generated Players)
│   │   └── index.html         (Navigation Hub)
│   ├── playlists/             (Saved Playlists)
│   ├── thumbnails/            (Video Thumbnails)
│   ├── documentation/         (Guides & Docs)
│   └── exports/               (Exported Files)
│
├── 📚 Sample_Playlists/         ← Demo Content
│   └── [Demo M3U Files]
│
├── 📖 Documentation/            ← User Guides
│   ├── README.md              (Main Documentation)
│   ├── NDI_BROADCAST_GUIDE.md (NDI Setup Guide)
│   └── INSTALLER_GUIDE.md     (Installation Guide)
│
└── 🚀 Launch Scripts
    ├── LAUNCH_M3U_MATRIX_PRO.bat     (Windows)
    ├── LAUNCH_VIDEO_PLAYER_PRO.bat   (Windows)
    ├── launch_m3u_matrix_pro.sh      (Linux/Mac)
    └── launch_video_player_pro.sh    (Linux/Mac)
```

---

## 🎯 Key Features

### M3U MATRIX PRO (Desktop Application)
- **Complete IPTV Management**: Load, edit, organize M3U playlists
- **Smart Channel Organization**: Auto-sort by country, category, language
- **EPG Integration**: TV guide support with XMLTV
- **Thumbnail Caching**: Automatic channel logo management
- **Page Generation**: Create 8+ different web player types
- **🔴 NDI Broadcast Output**: Stream to OBS, vMix, TriCaster
- **Rumble Integration**: Import and manage Rumble channels
- **Smart Scheduler**: 7-day automated scheduling
- **Navigation Hub**: Central management for all generated pages

### VIDEO PLAYER PRO (Media Workbench)
- **VLC-Powered Playback**: Professional media player
- **Screenshot Capture**: Automated or manual screenshots
- **Metadata Extraction**: FFmpeg-powered video analysis
- **Playlist Management**: Advanced playlist editing
- **NDI Output Toggle**: One-click broadcast streaming
- **Scheduling**: Time-based playback automation
- **Persistent Settings**: Remember folder preferences

### Web Players (8 Professional Templates)
1. **NEXUS TV**: 24-hour auto-scheduled cyberpunk player
2. **Buffer TV**: TV player with numeric keypad (0-9, +10, +20)
3. **Multi-Channel**: Watch 1-6 channels simultaneously
4. **Simple Player**: Clean, minimalist video player
5. **Web IPTV**: Traditional channel-based player
6. **Rumble Channel**: Dedicated Rumble video player
7. **Stream Hub**: Professional broadcast hub
8. **Standalone Secure**: Encrypted URL player

---

## 🔴 NDI Broadcast Integration

### Professional Video-over-IP Streaming
Stream any channel to production software via **Network Device Interface (NDI)**:

- **Multi-Channel Broadcasting**: Stream multiple channels simultaneously
- **Production Quality**: 1920x1080 @ 30fps professional video
- **Compatible Software**: OBS Studio, vMix, Wirecast, TriCaster
- **Real-Time Monitoring**: Live status for all streams
- **Network Efficient**: ~150 Mbps per Full NDI stream
- **One-Click Control**: Easy start/stop from control center

**Access NDI Control Center**: Click the **🔴 NDI** button (red) in M3U Matrix Pro toolbar

### NDI Quick Setup:
1. Install NDI Tools from [ndi.tv](https://ndi.tv/tools/)
2. Install VLC Media Player with NDI plugin
3. Launch M3U Matrix Pro
4. Click **🔴 NDI** button
5. Select channel and click "Start NDI Output"
6. Open OBS/vMix and add NDI source

---

## 💡 How to Use

### Basic Workflow
1. **Launch M3U Matrix Pro** using the launch script
2. **Load M3U Playlist**: Drag & drop or use LOAD button
3. **Organize Channels**: Click ORGANIZE for auto-sorting
4. **Generate Players**: Choose from 8 player types
5. **Open Navigation Hub**: Click NAV HUB to manage pages

### Advanced Features
- **NDI Broadcasting**: Stream channels to production systems
- **Rumble Browser**: Visual channel discovery with categories
- **Smart Scheduling**: Automated 7-day TV schedules
- **Multi-Channel Viewer**: Watch up to 6 channels at once
- **Buffer TV**: Advanced buffering with numeric channel selection

---

## 🛠️ System Requirements

### Required Software
- **Python 3.11 or 3.12** (NOT 3.13 - PyInstaller incompatible)
- **VLC Media Player** (Required for Video Player Pro)
- **Web Browser** (Chrome, Firefox, Edge recommended)

### Optional Software
- **FFmpeg**: For video metadata and duration extraction
- **NDI Tools**: For broadcast streaming capability
- **OBS Studio**: For receiving NDI streams

### Python Libraries
```bash
pip install tkinterdnd2 requests Pillow python-vlc
```

---

## 📦 Installation Guide

### Step 1: Download & Extract
1. Download the project ZIP file
2. Extract to your desired location (e.g., `C:\M3U_Matrix` or `~/Documents/M3U_Matrix`)

### Step 2: Install Python
1. Download Python 3.11 or 3.12 from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Verify: `python --version`

### Step 3: Install VLC
1. Download VLC from [videolan.org](https://videolan.org)
2. Install with default settings
3. VLC is required for Video Player Pro

### Step 4: Install Python Libraries
```bash
# Open terminal/command prompt in project folder
pip install tkinterdnd2 requests Pillow python-vlc
```

### Step 5: Launch Applications
- **Windows**: Double-click the `.bat` files
- **Linux/Mac**: Run the `.sh` scripts

---

## 🎨 Generated Output Structure

All generated content is professionally organized in `M3U_Matrix_Output/`:

```
M3U_Matrix_Output/
├── generated_pages/
│   ├── index.html           ← Navigation Hub (Main Page)
│   ├── nexus_tv/           ← NEXUS TV Players
│   ├── buffer_tv/          ← Buffer TV Players
│   ├── multi_channel/      ← Multi-Channel Players
│   ├── simple_player/      ← Simple Players
│   ├── web_iptv/          ← Web IPTV Players
│   ├── rumble_channel/    ← Rumble Players
│   └── standalone/        ← Standalone Players
├── playlists/             ← Saved M3U Files
├── thumbnails/            ← Channel Logos & Screenshots
├── exports/              ← JSON, CSV Exports
└── documentation/        ← Generated Guides
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python 3.11 or 3.12, add to PATH |
| "Module not found" | Run `pip install tkinterdnd2 requests Pillow python-vlc` |
| "VLC not available" | Install VLC Media Player |
| "NDI not working" | Install NDI Tools and VLC NDI plugin |
| "Can't open navigation hub" | Check `M3U_Matrix_Output/generated_pages/index.html` |
| "PyInstaller fails" | Use Python 3.11/3.12, NOT 3.13 |

### File Locations
- **Navigation Hub**: `M3U_Matrix_Output/generated_pages/index.html`
- **Generated Players**: `M3U_Matrix_Output/generated_pages/[type]/`
- **Saved Playlists**: `M3U_Matrix_Output/playlists/`
- **Documentation**: `Documentation/` folder

---

## 📚 Documentation

### Available Guides
- **Main Documentation**: This README
- **NDI Broadcast Guide**: `Documentation/NDI_BROADCAST_GUIDE.md`
- **Installation Guide**: `Documentation/INSTALLER_GUIDE.md`
- **Player Documentation**: Built into each generated page

### Quick Reference
- **NAV HUB Button** (Gold): Opens navigation center
- **🔴 NDI Button** (Red): Opens broadcast control
- **RUMBLE BROWSER** (Tomato): Visual channel discovery
- **GENERATE PAGES** (Pink): Create web players

---

## 🚀 Quick Commands

### Windows Commands
```batch
REM Launch M3U Matrix Pro
LAUNCH_M3U_MATRIX_PRO.bat

REM Launch Video Player Pro
LAUNCH_VIDEO_PLAYER_PRO.bat
```

### Linux/Mac Commands
```bash
# Launch M3U Matrix Pro
./launch_m3u_matrix_pro.sh

# Launch Video Player Pro
./launch_video_player_pro.sh
```

### Python Direct Launch
```bash
# From project root
cd Applications
python M3U_MATRIX_PRO.py
python VIDEO_PLAYER_PRO.py
```

---

## 🎬 Workflow Examples

### Create a 24-Hour TV Channel
1. Load M3U playlist in M3U Matrix Pro
2. Click **SMART SCHEDULE** for 7-day scheduling
3. Select **NEXUS TV** template
4. Generate pages
5. Open in browser for auto-scheduled playback

### Broadcast to OBS Studio
1. Load channels in M3U Matrix Pro
2. Click **🔴 NDI** button
3. Select channel, click "Start NDI Output"
4. In OBS: Add Source → NDI Source
5. Select your channel from dropdown

### Multi-Channel Monitoring
1. Generate **Multi-Channel** player
2. Select 4 or 6 channel grid
3. Load different streams per channel
4. Use keyboard (1-6) to switch audio

---

## 📝 License & Credits

**M3U MATRIX ALL-IN-ONE** - Professional IPTV Management Platform

This project combines multiple technologies to create a comprehensive IPTV solution:

### Core Technologies
- **Python/Tkinter**: Desktop application framework
- **HTML5/CSS3/JavaScript**: Web player interfaces
- **VLC Media Player**: Professional video playback
- **NDI Protocol**: Broadcast-grade streaming
- **FFmpeg**: Video processing and metadata
- **HLS.js/dash.js**: Adaptive streaming support

### Features Highlights
- 8 different web player templates
- Professional NDI broadcast output
- Rumble video platform integration
- Smart 7-day scheduling system
- Multi-channel simultaneous viewing
- Comprehensive playlist management

---

## 📞 Support & Help

### Getting Help
1. **Check Documentation**: Review guides in Documentation folder
2. **Navigation Hub**: Access at `M3U_Matrix_Output/generated_pages/index.html`
3. **Error Messages**: Screenshot any errors for troubleshooting
4. **Python Version**: Ensure using 3.11 or 3.12 (NOT 3.13)
5. **Dependencies**: Verify all required libraries installed

### Project Structure Benefits
- **Simplified Organization**: Easy to find everything
- **One-Click Launch**: Convenient batch/shell scripts
- **Clean Separation**: Apps, templates, and output organized
- **Professional Layout**: Broadcast-ready configuration

---

**Transform your IPTV experience with professional management and broadcasting!** 🎬📺✨

*Version 5.0 - Now with NDI Broadcast Support and Simplified Structure*