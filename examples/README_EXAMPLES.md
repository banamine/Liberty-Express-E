# ScheduleFlow Carousel - Examples & Format Reference

## Files in This Directory

### 1. **example_m3u_playlists.m3u**
   - Complete M3U playlist with 15+ example videos
   - Shows MP4 format, HLS streams, Rumble links, local files
   - Copy-paste ready: paste entire content into carousel "Import M3U" box
   - Includes movies, shorts, live TV examples

### 2. **javascript_carousel_examples.js**
   - 10 JavaScript code examples
   - Single video, playlists, Rumble videos, HLS streams
   - Code to programmatically add videos
   - Usage instructions for all features

### 3. **CAROUSEL_USAGE_GUIDE.md**
   - Complete user guide
   - Step-by-step instructions for all features
   - Keyboard shortcuts
   - Tips & best practices
   - Rumble integration guide

---

## Quick Copy-Paste Examples

### Single MP4 Movie
```
https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4
```

### Single Rumble Video
```
https://rumble.com/embed/v3t4m5f/
```

### HLS Live Stream
```
https://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/original/llnw/en/audio_aac_lc_128kbps.m3u8
```

### Entire M3U Playlist
See **example_m3u_playlists.m3u** file

---

## What Works Best

✅ Movies (MP4, 9+ minutes)  
✅ Short videos (30 sec - 5 min)  
✅ Rumble videos (embedded)  
✅ HLS streams (live TV, playlists)  
✅ M3U playlists (bulk import)  

---

## Rumble Integration

Videos on Rumble are perfect for:
- Wide variety of content
- Embedded player (no file download)
- Mix with other video types in carousel
- Shareable clips with timestamps

**Format:** `https://rumble.com/embed/VIDEOID/`  
Extract VIDEOID from Rumble URL and use above format.

---

## How to Use These Examples

1. **For quick testing:**
   - Copy single MP4 URL
   - Paste into carousel "Add URL"
   - Play immediately

2. **For bulk import:**
   - Copy entire `example_m3u_playlists.m3u` content
   - Paste into "Import M3U Playlist" box
   - Click Import
   - Browse 15+ videos instantly

3. **For JavaScript integration:**
   - See `javascript_carousel_examples.js`
   - Copy code examples to your project
   - Modify URLs for your videos

4. **For Rumble content:**
   - Get video ID from Rumble URL
   - Use embed format: `https://rumble.com/embed/VIDEOID/`
   - Add to carousel same as other videos

---

## File Format Reference

| Format | Extension | Example | Works? |
|--------|-----------|---------|--------|
| MP4 Video | .mp4 | `https://example.com/movie.mp4` | ✅ Yes |
| HLS Playlist | .m3u8 | `https://example.com/stream.m3u8` | ✅ Yes |
| M3U Playlist | .m3u | Text file with URLs | ✅ Yes |
| Rumble Embed | n/a | `https://rumble.com/embed/VIDEOID/` | ✅ Yes |
| WebM | .webm | `https://example.com/video.webm` | ✅ Yes |
| Ogg Theora | .ogg | `https://example.com/video.ogg` | ✅ Yes |

---

## Getting Started (3 Steps)

1. **Visit:** http://your-app/scheduleflow_carousel.html

2. **Choose import method:**
   - Single video: Click "➕ Add URL" → paste MP4 link
   - Rumble video: Click "➕ Add URL" → paste embed link
   - Multiple videos: Click "➕ Add URL" → paste M3U content → Import

3. **Play:**
   - Use arrows to browse
   - Click "▶️ PLAY" on any video
   - Use "✂️ Clip Mode" to create shareable segments

---

## Troubleshooting

**Video won't play?**
- Check URL is accessible (not 404)
- Try a public test video first (Big Buck Bunny)
- Check browser console for errors

**M3U import shows "No valid URLs"?**
- Make sure URLs start with `http://` or `https://`
- Remove comment lines (starting with #)
- Keep one URL per line

**Rumble video not showing?**
- Use embed format: `https://rumble.com/embed/VIDEOID/`
- Not: `https://rumble.com/vVIDEOID-title/`
- Extract VIDEOID correctly from URL

**Clip mode not working?**
- Use format: HH:MM:SS (hours:minutes:seconds)
- Example: 01:23:45 = 1 hour, 23 min, 45 sec
- Click "Mark Start" and "Mark End" while video is playing

---

## Next Steps

- See **CAROUSEL_USAGE_GUIDE.md** for complete feature documentation
- See **example_m3u_playlists.m3u** for copy-paste playlist examples
- See **javascript_carousel_examples.js** for code examples

---

## Perfect For

🎬 **Rumble creators** - Showcase channel playlists  
📺 **Live TV** - HLS streams and playlists  
🎥 **Video library** - Browse and organize content  
✂️ **Clip sharing** - Create shareable segments with timestamps  
🎞️ **Presentations** - Full-screen video playback  
