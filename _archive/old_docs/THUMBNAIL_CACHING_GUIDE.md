# 📸 Thumbnail Caching System - User Guide

## Overview
M3U Matrix Pro now automatically downloads and caches channel logos/thumbnails when you load M3U playlists. This makes loading faster and keeps your playlists working even if the original image URLs go offline.

## How It Works

### Automatic Caching
When you load an M3U file:
1. The system reads each channel's `tvg-logo` URL
2. Downloads the image from the internet
3. Verifies it's a valid image file
4. Saves it to the `thumbnails/` folder with a unique filename
5. Updates the channel data to use the local cached image
6. Saves the cached path in your playlist JSON

### Filename Format
Cached thumbnails use this format:
```
channelname_hash.ext
```
Example: `Hogans_Heroes_S03E01_a1b2c3d4e5f6.jpg`

- `channelname`: Sanitized channel name (first 50 characters)
- `hash`: Unique 12-character hash of the original URL
- `ext`: Original file extension (.jpg, .png, .gif, .webp)

### Benefits
✅ **Faster Loading**: Local images load instantly  
✅ **Offline Access**: Thumbnails work even if original URLs are dead  
✅ **Deduplication**: Same URL downloads only once (hash-based)  
✅ **Persistent**: Cached images saved to disk, available across sessions  
✅ **Safe**: Image verification prevents malicious files  

## Settings

### Enable/Disable Caching
Edit `m3u_matrix_settings.json`:

```json
{
  "cache_thumbnails": true
}
```

- `true` = Download and cache thumbnails (default, recommended)
- `false` = Keep original URLs, don't download

### Current Settings
The setting is enabled by default. To disable:
1. Close M3U Matrix Pro
2. Open `m3u_matrix_settings.json` in a text editor
3. Change `"cache_thumbnails": true` to `"cache_thumbnails": false`
4. Save and restart the app

## Cache Management

### View Cache Statistics
```python
from utils import get_cached_thumbnail_stats
stats = get_cached_thumbnail_stats(Path("thumbnails"))
print(f"Cached images: {stats['count']}")
print(f"Total size: {stats['total_size_mb']} MB")
```

### Clear Cache
To free up disk space:
1. Close M3U Matrix Pro
2. Delete the `thumbnails/` folder
3. Restart the app
4. Reload your M3U files (thumbnails will re-download)

### Cache Location
```
C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE\thumbnails\
```

## Error Handling

The system gracefully handles:
- ❌ **404 Not Found**: Logs warning, keeps original URL
- ⏱️ **Timeouts**: 5-second timeout per image, skips on timeout
- 🚫 **Invalid Images**: Verifies image format, rejects non-images
- 🔌 **Network Errors**: Catches connection failures, continues loading

## Technical Details

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### Download Timeout
5 seconds per image (configurable)

### Image Verification
Uses PIL (Pillow) to verify images before saving:
```python
img = Image.open(BytesIO(response.content))
img.verify()  # Ensures it's a valid image
```

### Hash Algorithm
MD5 hash (first 12 characters) ensures unique filenames for different URLs

### Thread Safety
Currently synchronous during M3U loading. For large playlists (>100 channels), consider enabling caching after initial load.

## Workflow

### First Load (New Playlist)
1. Load M3U file → Parse channels
2. For each channel with tvg-logo:
   - Check if already cached (hash lookup)
   - If not cached: Download → Verify → Save
   - Update channel logo path to local file
3. Save playlist JSON with cached paths

### Subsequent Loads (Cached Playlist)
1. Load M3U file → Parse channels
2. For each channel with tvg-logo:
   - Check if already cached ✅
   - Skip download (instant!)
   - Use local cached file
3. Load instantly with local images

## FFmpeg Integration (Local Files Only)

### Video Duration Extraction
For M3U playlists with **local file paths** (not URLs):
```json
{
  "use_ffmpeg_extraction": false
}
```

Enable this to extract accurate video durations when generating NEXUS TV pages.

**Note**: This only works with local video files on your computer, not remote URLs like archive.org.

### Remote URL Limitation
FFmpeg cannot extract duration from remote MP4 URLs without downloading the entire file. For archive.org playlists, the system uses default 30-minute time slots.

## Troubleshooting

### Thumbnails Not Downloading
✓ Check internet connection  
✓ Verify `cache_thumbnails: true` in settings  
✓ Check `thumbnails/` folder permissions  
✓ Look for errors in `logs/` folder  

### Thumbnails Show Broken Images
✓ Original URL may be invalid (404)  
✓ Check file format (must be .jpg, .png, .gif, .webp)  
✓ Delete cache and re-download  

### Slow M3U Loading
✓ Large playlists (>100 channels) take time on first load  
✓ Subsequent loads are instant (cached)  
✓ Consider disabling caching temporarily  

## Future Enhancements

Planned improvements:
- Background worker threads (non-blocking UI)
- Progress bar during thumbnail downloads
- Batch download option
- Cache size limits (auto-cleanup)
- Remote MP4 duration extraction (HTTP range requests)
- URL validation before download

## Example: Your Hogan's Heroes Playlist

When you load `hogans.m3u`:

**Before (Original URLs):**
```
tvg-logo="https://archive.org/download/.../thumbnail.jpg"
```

**After (Cached Locally):**
```
logo="thumbnails/Hogans_Heroes_S03E01_a1b2c3d4e5f6.jpg"
logo_cached=true
```

Your playlist JSON now references local files, making it faster and more reliable! 🎉

---

## Quick Reference

| Feature | Status | Location |
|---------|--------|----------|
| Thumbnail Caching | ✅ Enabled | `thumbnails/` |
| Settings File | ✅ JSON | `m3u_matrix_settings.json` |
| Cache Stats | ✅ Available | `get_cached_thumbnail_stats()` |
| FFmpeg Extraction | ⚠️ Local Only | `use_ffmpeg_extraction: false` |
| Remote MP4 Duration | ❌ Not Supported | Use defaults (30 min) |

**Enjoy faster, more reliable playlist loading!** 🚀
