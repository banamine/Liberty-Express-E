# ScheduleFlow Carousel - Usage Guide

## What It Is
A playlist carousel player for browsing and playing multiple videos:
- **Movies** (MP4 files)
- **Short videos** (clips, promos)
- **Rumble videos** (embedded)
- **HLS streams** (live or playlists)
- **M3U playlists** (bulk import)

---

## 3 Ways to Use It

### Option 1: Add Single Videos One-by-One
```
1. Visit: http://your-app/scheduleflow_carousel.html
2. Click "➕ Add URL"
3. Paste any video URL (see examples below)
4. Click "Add Video"
5. Repeat for more videos
6. Use arrows to browse
7. Click "▶️ PLAY" on any video
```

**Supported URLs:**
- MP4: `https://example.com/movie.mp4`
- Rumble: `https://rumble.com/embed/v3t4m5f/`
- HLS: `https://example.com/playlist.m3u8`
- Local: `/videos/my-video.mp4` (if served from your server)

---

### Option 2: Import M3U Playlist (Bulk)
```
1. Visit: http://your-app/scheduleflow_carousel.html
2. Click "➕ Add URL"
3. Paste entire M3U playlist into text box (see example_m3u_playlists.m3u)
4. Click "Import M3U Playlist"
5. All videos added at once!
6. Use arrows to browse your playlist
7. Click "▶️ PLAY" on any video
```

**M3U Format:**
```
#EXTM3U
#EXTINF:574, Video Title
https://example.com/video1.mp4

#EXTINF:300, Another Video
https://example.com/video2.mp4

#EXTINF:120, Rumble Video
https://rumble.com/embed/v3t4m5f/
```

---

### Option 3: Share Clips with Timestamps
```
1. Play a video
2. Click "✂️ Clip Mode"
3. At desired start point: click "Mark Start"
4. At desired end point: click "Mark End"
5. Click "▶️ Play Clip" to test
6. Click "🔗 Share"
7. Copy generated URL with timestamps
8. Share link - opens at exact clip point
```

---

## Example Videos

### Public Domain / Free Movies
```
Big Buck Bunny (9 min, 175 MB):
https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4

Elephant's Dream (11 min, 120 MB):
https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4

Sintel (15 min, 390 MB):
https://commondatastorage.googleapis.com/gtv-videos-library/sample/Sintel.mp4
```

### Short Videos / Clips
```
Volleyball Clip (2 min, 10 MB):
https://commondatastorage.googleapis.com/gtv-videos-library/sample/VolleyballShort.mp4

Teaser (1 min, 5 MB):
https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerEscapes.mp4
```

### Rumble Example
```
Format: https://rumble.com/embed/VIDEOID/
Example: https://rumble.com/embed/v3t4m5f/
```

---

## Copy-Paste M3U Playlist Example

Save this as `my-playlist.m3u` or paste into the carousel:

```
#EXTM3U
#EXT-X-VERSION:3

#EXTINF:574, Movie: Big Buck Bunny
https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4

#EXTINF:180, Short: Elephant's Dream
https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4

#EXTINF:300, Rumble Video
https://rumble.com/embed/v3t4m5f/

#EXTINF:120, Clip: Volleyball
https://commondatastorage.googleapis.com/gtv-videos-library/sample/VolleyballShort.mp4
```

---

## Features

### 🎬 Playback
- Full-screen video player
- Video controls (play, pause, volume, seek)
- Supports MP4, HLS, Rumble embeds

### 📺 Carousel Browsing
- Left/Right arrows to browse videos
- Dot indicators to jump to any video
- Current video badge showing position

### ✂️ Clip Creator
- Set custom start/end times (HH:MM:SS)
- Mark points while video plays
- Play only the clip portion

### 🔗 Shareable Links
- Generate URLs with exact timestamps
- Share specific moments from videos
- Recipients jump to that exact point

### ⌨️ Keyboard Shortcuts
| Key | Action |
|-----|--------|
| ← / → | Previous/Next video |
| ENTER | Play current video |
| C | Toggle Clip Mode |
| S | Share current video |

### 💾 Local Storage
- All videos saved in browser
- Persists between sessions
- No server storage needed

---

## Best For

✅ **Movies** - Feature films, documentaries  
✅ **Short Videos** - Clips, promos, trailers  
✅ **Rumble Content** - Embedded Rumble videos  
✅ **Playlists** - Multi-video sequences  
✅ **Clips** - Creating shareable segments with exact timestamps  
✅ **Live TV** - HLS streaming playlists  

---

## File Sizes / Video Duration Reference

| Type | Duration | File Size | Example |
|------|----------|-----------|---------|
| Feature Film | 90-180 min | 500MB-2GB | Big Buck Bunny (9 min, 175 MB) |
| Short Video | 2-10 min | 10-100 MB | Volleyball clip (2 min, 10 MB) |
| Clip/Promo | 30 sec - 2 min | 5-30 MB | Teaser videos |
| Rumble Video | Any | Streamed | No file download |
| HLS Stream | Live/Continuous | Streamed | No file download |

---

## Rumble Integration

### Getting Rumble Video ID
1. Go to video on Rumble.com
2. URL looks like: `https://rumble.com/v3t4m5f-video-title/`
3. Extract ID: `v3t4m5f`
4. Use in carousel: `https://rumble.com/embed/v3t4m5f/`

### Why Rumble?
- Full Rumble player with all controls
- No download needed (embedded)
- Works seamlessly in carousel
- Mix with other video types

---

## Tips

💡 **Tip 1:** Mix video types in one playlist
- MP4 movies + Rumble videos + HLS streams = one carousel

💡 **Tip 2:** Use M3U for bulk import
- Paste entire playlist at once
- Add hundreds of videos in seconds
- Edit file, re-import to update

💡 **Tip 3:** Create shareable clips
- Clip Mode → Share → Copy URL
- Send exact timestamp to others
- Recipient lands at your marked point

💡 **Tip 4:** Test with sample videos
- Use Big Buck Bunny for testing
- Small enough to load instantly
- 9 minutes of quality test content

💡 **Tip 5:** Full-screen for presentations
- Click "⛶ FS" button
- Or press F11 in browser
- Perfect for TV/screen display

---

## Keyboard Controls (In Video Player)

**Video Controls:**
- `SPACE` - Play/Pause
- `←` / `→` - Seek back/forward
- `↑` / `↓` - Volume up/down
- `F` - Fullscreen
- `M` - Mute/unmute

---

## Examples Included

See these files in `/examples/`:

1. **example_m3u_playlists.m3u** - Ready-to-use M3U files
2. **javascript_carousel_examples.js** - Code examples
3. **CAROUSEL_USAGE_GUIDE.md** - This guide

---

## Access

**Production:** `https://your-app.replit.dev/scheduleflow_carousel.html`  
**Development:** `http://localhost:5000/scheduleflow_carousel.html`

---

## Need Help?

- **Keyboard shortcuts?** Click the hint text under the card
- **Share a clip?** Use "✂️ Clip Mode" then "🔗 Share"
- **Import playlist?** Use "➕ Add URL" and paste M3U
- **Add Rumble video?** Use embed format: `https://rumble.com/embed/VIDEOID/`
