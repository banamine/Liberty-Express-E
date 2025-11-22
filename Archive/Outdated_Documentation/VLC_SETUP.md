# VLC Setup - ScheduleFlow Channels

## Quick Start

### Option 1: Load M3U in VLC (Easiest)
```
1. Open VLC Media Player
2. Go to: File → Open File
3. Select: scheduleflow_vlc.m3u
4. All 10 channels load in VLC playlist
5. Click channel → plays in VLC
```

### Option 2: Command Line (Linux/Mac)
```bash
vlc scheduleflow_vlc.m3u
```

### Option 3: Windows Command
```bash
"C:\Program Files\VideoLAN\VLC\vlc.exe" scheduleflow_vlc.m3u
```

---

## Channels Included

1. ALEX JONES NETWORK FEED: LIVE 247!
2. Patriot News Outlet Live
3. HOME OF REAL NEWS
4. NEWSMAX2 LIVE
5. RT News | Livestream 24/7
6. RT DE LIVE-TV
7. The Alex Jones Show
8. Infowars Network Feed: LIVE 247
9. His Glory TV 24/7
10. ALEX JONES - INFOWARS LIVE

---

## How It Works

- **M3U Format**: Standard VLC playlist format
- **Video IDs**: Real Rumble video IDs from live page (Nov 22, 2025)
- **Direct Links**: Click channel → VLC plays video
- **All Rumble Features**: VLC handles playback controls, quality, etc.

---

## If Video Won't Load

VLC can sometimes have issues with Rumble direct links. If that happens:

### Extract HLS Stream (Advanced)
```bash
# Install yt-dlp if needed
pip install yt-dlp

# Extract HLS URL for a video
yt-dlp -f "best[ext=m3u8]/best" --get-url https://rumble.com/vVIDEO_ID

# Use that URL in the M3U file instead
```

---

## M3U File Format Reference

```
#EXTM3U
#EXTINF:-1,Channel Name
https://rumble.com/vVIDEO_ID.html
```

Each entry:
- `#EXTINF` = channel info
- `Channel Name` = what shows in VLC playlist
- `https://...` = direct Rumble video link
