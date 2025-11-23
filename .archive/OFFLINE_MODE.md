# Offline Mode Documentation

**Last Updated:** November 23, 2025

---

## Overview

ScheduleFlow supports **partial offline functionality**. This document explains what works offline and what doesn't.

---

## What Works Offline ✅

### 1. Viewing Imported Schedules
- All schedules are stored locally in `schedules/` directory
- You can view schedule details without internet
- Schedule metadata, events, and timestamps are accessible

### 2. Importing Files
- Import XML schedules from local files
- Import JSON schedules from local files  
- Import M3U playlists from local files
- Validation runs completely offline

### 3. Exporting Schedules
- Export to XML format (no internet needed)
- Export to JSON format (no internet needed)
- Generated files are saved locally

### 4. Drag-Drop Interface
- Reorder videos in schedule
- Modify event properties
- Adjust timings
- All changes persist locally

### 5. Local Players
- Desktop HTML players work offline
- Video files must be local or cached
- Generated player HTML can be run offline

---

## What Requires Internet ❌

### 1. Fetching Videos from URLs
- Videos from HTTP/HTTPS URLs require internet
- Streaming sources (YouTube, Twitch, etc.) require internet
- HLS/DASH streams require internet
- M3U playlists from remote sources require internet

### 2. EPG (Electronic Program Guide)
- Fetching EPG data from remote servers requires internet
- Updating channel listings requires internet

### 3. Cloud Synchronization
- Syncing schedules to cloud storage requires internet
- GitHub Pages deployment requires internet
- Remote backup requires internet

### 4. Validation Against Remote Sources
- Checking if URLs are valid requires internet
- Verifying video metadata requires internet
- Checking for duplicates across cloud storage requires internet

---

## Offline Workflow

### Step 1: Prepare Content
Work on your schedules with local data:

```bash
# Create local demo schedules (no internet needed)
1. Use demo_data/sample_schedule.xml
2. Use demo_data/sample_schedule.json
3. Create your own XML/JSON files locally
```

### Step 2: Import Schedules
Import your local schedules:

```bash
# Via API (requires running server)
curl -X POST http://localhost:5000/api/import-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "/path/to/local/schedule.xml",
    "format": "xml"
  }'

# Or via Desktop App
python3 M3U_Matrix_Pro.py --import-schedule-xml schedule.xml
```

### Step 3: Edit & Export
Modify schedules and export:

```bash
# Export to XML
curl -X POST http://localhost:5000/api/export-schedule-xml \
  -H "Content-Type: application/json" \
  -d '{"schedule_id": "id-here", "filename": "my_schedule.xml"}'

# Export to JSON
curl -X POST http://localhost:5000/api/export-schedule-json \
  -H "Content-Type: application/json" \
  -d '{"schedule_id": "id-here", "filename": "my_schedule.json"}'
```

### Step 4: Deploy to Player
Use exported files locally:

```bash
# Copy exported schedule to player directory
cp exports/my_schedule.xml /path/to/player/

# Run player offline
# Videos must be local files or cached
```

---

## Offline Player Setup

### Option 1: Local HTML Player

**Works Offline:**
1. Generated HTML player pages
2. Embedded video URLs (if videos are local)
3. Standalone player with schedule data

**Requirements:**
- Videos must be local files (not remote URLs)
- HTML file must be standalone
- No remote dependencies

**Example:**
```html
<!-- Player HTML with embedded schedule -->
<video src="file:///local/path/video.mp4" controls autoplay></video>
```

### Option 2: Desktop Player

**Works Offline:**
- Launch desktop app: `python3 M3U_Matrix_Pro.py`
- Load local schedules
- Play local video files
- All functionality works without internet

**Steps:**
```bash
1. Start desktop app: python3 M3U_Matrix_Pro.py
2. Import local schedule (XML/JSON)
3. Point videos to local files
4. Videos play using system player
```

### Option 3: Media Player with M3U

**Works Offline:**
- Create M3U playlist with local files
- Open in VLC, MPV, or other player
- Videos play sequentially

**Example M3U:**
```
#EXTM3U
#EXTINF:-1,Video 1
file:///path/to/video1.mp4
#EXTINF:-1,Video 2
file:///path/to/video2.mp4
```

---

## Data Persistence (Offline)

### Where Data is Stored

**Schedule Files:**
```
schedules/
├── {schedule-id}.json
├── cooldown_history.json
└── ...
```

**Configuration:**
```
m3u_matrix_settings.json
```

**Generated Pages:**
```
generated_pages/
├── index.html
├── dashboard.html
└── player.html
```

### Accessing Offline

All data is stored locally in JSON files:

```bash
# View schedules
cat schedules/schedule-id.json

# View configuration
cat m3u_matrix_settings.json

# View cooldown history
cat schedules/cooldown_history.json
```

### Backup & Restore

Offline backup is simple:

```bash
# Backup
cp -r schedules/ backup/schedules_backup/
cp m3u_matrix_settings.json backup/

# Restore
cp -r backup/schedules_backup/* schedules/
cp backup/m3u_matrix_settings.json .
```

---

## Offline Limitations & Critical Clarifications

### IMPORTANT: What "Offline" Means

**ScheduleFlow is NOT a cloud sync system.** This is critical to understand:

- ✅ **Desktop/Local Setup:** Fully offline-capable (all data stored locally)
- ✅ **Single-User Scenarios:** Complete offline functionality
- ❌ **Multi-User Cloud Sync:** NOT SUPPORTED (no reconnection/sync mechanism)
- ❌ **Collaborative Editing:** NOT SUPPORTED (no conflict resolution)

---

### 1. NO Multi-Device Sync
**What this means:**
- If you edit on Device A (offline) and Device B (online), there's NO automatic sync
- Changes on Device A will NOT appear on Device B
- There is NO conflict resolution if both devices edit the same schedule
- You must manually copy files between devices

**Example of what happens:**
```
Device A (Offline):        Device B (Online):
Edit schedule X → v1       Edit schedule X → v2
(changes stored locally)    (changes stored server)
When Device A reconnects:
[NO AUTOMATIC SYNC]
Manual action required to merge
```

**Consequence:**
- Data from one device could overwrite the other
- Must manually manage versions if using multiple devices
- For 24/7 single-server deployment: This is fine (only one device)

---

### 2. NO Video Streaming (Requires Internet)
- Remote videos won't play offline
- M3U URLs require internet
- HLS/DASH streams require internet
- ✅ Solution: Store videos locally

### 3. NO EPG Data (Requires Internet)
- Electronic Program Guide requires internet
- Can't fetch channel information
- Must use pre-imported data

### 4. NO Remote URL Validation (Requires Internet)
- Can't verify URLs are working
- Can't check video metadata
- Can't validate against remote schedules

### 5. NO Cloud Sync (Not Implemented)
- Can't sync with Dropbox, Drive, etc.
- Can't push to GitHub Pages
- No automatic backups to cloud
- **This is by design - ScheduleFlow is local-first, not cloud-first**

---

## Recommendations

### For 24/7 Playout
**Use Local Videos:**
- Download all videos to local storage
- Create schedules pointing to local paths
- Deploy locally without internet
- Backup to external drive

```bash
# Example offline setup
/playout/
├── videos/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
├── schedules/
│   └── daily_schedule.xml
└── player/
    └── index.html
```

### For Multi-Device Setup (NOT RECOMMENDED)
**If you MUST use multiple devices:**
- Create schedules on primary device
- Manually export from primary
- Manually import on secondary devices
- Update primary, then redistribute files
- ⚠️ WARNING: Prone to version conflicts

**Better approach:**
- Use one primary device for scheduling
- Other devices access exported read-only copies
- Avoid editing on multiple devices simultaneously

### For Development
**Use Docker Offline:**
```dockerfile
# Dockerfile for offline deployment
FROM node:18
WORKDIR /app
COPY . .
RUN npm install --offline
ENV NODE_ENV=production
CMD ["node", "api_server.js"]
```

---

## Offline Server (API)

### API Server Offline Support

**The API server itself needs Node.js to run:**

```bash
# Start server (requires Node.js runtime)
node api_server.js

# Server runs offline after startup
# Requires no internet to operate
```

**API Endpoints (Offline):**
- ✅ GET /api/schedules
- ✅ GET /api/playlists
- ✅ POST /api/import-schedule
- ✅ POST /api/export-schedule-xml
- ✅ POST /api/export-schedule-json
- ❌ GET /api/infowars-videos (requires internet)

---

## Troubleshooting Offline

### "Videos won't play"
**Check:**
1. Are videos local files or remote URLs?
2. Can you access the video file directly?
3. Is the video format supported?

**Solution:**
- Use local video files: `file:///path/to/video.mp4`
- Check file exists: `ls -la /path/to/video.mp4`
- Verify format: `ffprobe video.mp4`

### "Can't import schedule offline"
**Check:**
1. Is the schedule file local or remote?
2. Is the API server running?
3. Is the file path correct?

**Solution:**
```bash
# Verify file exists
ls -la /path/to/schedule.xml

# Check API running
curl http://localhost:5000/api/system-info

# Import with absolute path
curl -X POST http://localhost:5000/api/import-schedule \
  -d '{"filepath":"/absolute/path/schedule.xml","format":"xml"}'
```

### "Data disappeared"
**Check:**
1. Is schedules/ directory present?
2. Are JSON files in schedules/?
3. Did git ignore the directory?

**Solution:**
```bash
# Check directory
ls -la schedules/

# Check git ignore
cat .gitignore | grep schedules

# Restore from backup
cp backup/schedules_backup/* schedules/
```

---

## Best Practices for Offline Use

1. **Always backup locally**
   - Keep copy of schedules
   - Keep copy of videos
   - Keep copy of config

2. **Use absolute file paths**
   - Don't use relative paths
   - Makes deployment easier
   - Works across reboots

3. **Test offline first**
   - Disable internet
   - Verify everything works
   - Document what's needed

4. **Document your setup**
   - Where videos are stored
   - How to restore
   - What requires internet

5. **Plan for internet outages**
   - Keep pre-export schedules
   - Have local video cache
   - Store backups offline

---

## Summary & Reality Check

### ✅ ScheduleFlow IS Fully Offline-Capable For:
- Single-device setup (desktop or server)
- 24/7 local playout
- Local-only scheduling
- Viewing and editing schedules offline
- Exporting files
- Playing local videos
- Running the API server

### ❌ ScheduleFlow Does NOT Support:
- Multi-device sync (no cloud backend)
- Collaborative editing (no conflict resolution)
- Automatic reconnection/merge (not a cloud app)
- Real-time updates across devices
- Streaming remote videos (requires internet)
- Fetching EPG data (requires internet)
- URL validation (requires internet)

### THE TRUTH ABOUT "RECONNECTION"
**There is NO reconnection behavior to worry about** because:
1. **Local Desktop:** All data stored locally, no server to reconnect to
2. **Local Server:** Once deployed, no internet needed for playback
3. **Remote Server:** Not a supported use case (no cloud sync)

If you disconnect internet:
- Desktop app continues working (all data local)
- Videos play from local storage
- No data loss occurs
- **No sync issues because there's nothing to sync**

When you reconnect:
- Dashboard API comes back online
- Local data is unchanged
- No conflicts to resolve (single-device model)
- **Everything works as before**

### Best Use Cases
✅ Campus TV station (single server, local videos)
✅ Hotel lobby display (single device, offline)
✅ YouTube stream (pre-scheduled, local prep)
✅ 24/7 playout system (one primary device)

❌ NOT ideal for: Multi-team collaborative scheduling
❌ NOT ideal for: Cloud-based multi-device syncing
❌ NOT ideal for: Real-time dynamic content updates

---

**BOTTOM LINE:**
For 24/7 local playout with local videos, ScheduleFlow is **100% offline-capable and reliable**. 
For cloud-based multi-device collaboration, ScheduleFlow is **NOT the right tool** (and never claimed to be).

---

**Questions?** See FIRST_RUN_GUIDE.md for setup help.
