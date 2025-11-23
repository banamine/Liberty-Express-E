# ScheduleFlow User Manual

**Version:** 2.0.0  
**Last Updated:** November 22, 2025  
**For:** Campus TV, Hotels, YouTube Live, Local Broadcasters

---

## Quick Start (5 Minutes)

### Step 1: Open ScheduleFlow
Visit: `http://localhost:5000` or your Replit public URL

You'll see the **Interactive Hub Dashboard** with 5 main buttons:

```
┌─────────────────────────────────────────────────────┐
│              ScheduleFlow Control Hub                │
├─────────────────────────────────────────────────────┤
│  📥 IMPORT    📋 SCHEDULE    📤 EXPORT    📊 STATS   │
└─────────────────────────────────────────────────────┘
```

### Step 2: Import a Schedule (or skip to Step 3)
Click **📥 IMPORT** → Upload an XML or JSON schedule file

**File format:**
```xml
<?xml version="1.0"?>
<schedule>
  <event>
    <title>Morning News</title>
    <start>2025-11-23T08:00:00Z</start>
    <end>2025-11-23T09:00:00Z</end>
  </event>
  <!-- More events... -->
</schedule>
```

### Step 3: Create a Schedule
Click **📋 SCHEDULE** → Enter:
- Video URLs (one per line)
- Start date/time
- Duration (hours)
- Repeat spacing (cooldown hours)

ScheduleFlow will **automatically fill** the entire time period with your videos!

### Step 4: Export
Click **📤 EXPORT** → Choose format:
- **XML** (TVGuide format, for professional playout engines)
- **JSON** (for custom processing)

Download and use with:
- CasparCG
- OBS
- vMix
- Custom scripts

---

## Feature 1: Import Schedules

### Supported Formats

#### XML (TVGuide Format)
```xml
<?xml version="1.0"?>
<schedule>
  <event>
    <title>Show Title</title>
    <start>2025-11-23T08:00:00Z</start>
    <end>2025-11-23T09:00:00Z</end>
  </event>
</schedule>
```

**Required fields:**
- `title` (name of the video/show)
- `start` (ISO 8601 timestamp)
- `end` (ISO 8601 timestamp)

#### JSON Format
```json
{
  "schedule": [
    {
      "title": "Show Title",
      "start": "2025-11-23T08:00:00Z",
      "end": "2025-11-23T09:00:00Z"
    }
  ]
}
```

### Import Steps

1. Click **📥 IMPORT** button
2. Select file (XML or JSON)
3. Click "Upload"
4. View results:
   - ✅ Events imported
   - 🔄 Duplicates removed (if any)
   - ⚠️ Conflicts detected (if any)

### Timezone Support

ScheduleFlow automatically converts times to UTC:

| Input | Converts To |
|-------|------------|
| 2025-11-23T08:00:00Z | UTC (no change) |
| 2025-11-23T08:00:00+05:30 | UTC (subtract 5:30) |
| 2025-11-23T08:00:00-08:00 | UTC (add 8 hours) |
| 2025-11-23T08:00:00 | UTC (assumes no offset) |

**Example:** Hong Kong time (GMT+8) → Converted to UTC automatically

---

## Feature 2: Schedule Videos

### How Auto-Scheduling Works

When you create a schedule, ScheduleFlow:

1. **Randomizes** your video list (optional)
2. **Enforces cooldown** - No video repeats within 48 hours
3. **Fills gaps** - Repeats videos to cover entire time period
4. **Returns schedule** - Calendar view with exact times

### Example

**Input:**
- Videos: [Video1, Video2, Video3]
- Period: 24 hours (8 AM → 8 AM next day)
- Each video: 1 hour
- Cooldown: 48 hours (no repeat within 2 days)

**Output:**
```
08:00 - Video1
09:00 - Video2
10:00 - Video3
11:00 - Video1    ← OK (will be 48+ hours before next play)
12:00 - Video2
...
```

### Schedule Settings

| Setting | Default | Options |
|---------|---------|---------|
| Duration | 24 hours | 1-168 hours |
| Cooldown | 48 hours | 24-240 hours |
| Shuffle | Yes | Yes/No |

### Creating a Schedule

1. Click **📋 SCHEDULE**
2. Enter **start date/time**
3. Paste **video URLs** (one per line):
   ```
   http://example.com/video1.mp4
   http://example.com/video2.mp4
   http://example.com/video3.mp4
   ```
4. Set **duration** (hours)
5. Click **Generate Schedule**
6. View calendar with scheduled videos

---

## Feature 3: Export Schedules

### Export Formats

#### XML Export (TVGuide Format)
Professional playout engines use this format.

```xml
<?xml version="1.0"?>
<tvguide>
  <programme start="20251123080000" stop="20251123090000">
    <title>Video1</title>
    <desc>Scheduled at 2025-11-23T08:00:00Z</desc>
  </programme>
</tvguide>
```

**Use with:**
- CasparCG
- Professional broadcast systems
- EPG generators

#### JSON Export
For custom processing or archival.

```json
{
  "schedule_id": "abc-123",
  "events": [
    {
      "title": "Video1",
      "start": "2025-11-23T08:00:00Z",
      "end": "2025-11-23T09:00:00Z"
    }
  ]
}
```

### Export Options

1. **Export Single Schedule**
   - Select schedule from list
   - Choose format (XML/JSON)
   - Download file

2. **Export All Schedules**
   - Exports all imported schedules
   - Combined into one XML file
   - Useful for backup

### Downloading

Exported files:
- Auto-download via browser
- Or copy URL to external system
- Timestamps in UTC

---

## Understanding Results

### Success Message
```
✅ Import Successful
48 events imported
2 duplicates removed
1 conflict detected
```

**What this means:**
- ✅ **48 events imported** - All videos added to schedule
- ⚠️ **2 duplicates removed** - Same video appeared twice; one removed
- ⚠️ **1 conflict detected** - Two videos scheduled at same time; user notified

### Understanding Duplicates

A duplicate is detected when:
- **Same URL appears twice** in import
- **Same video metadata** across different events

**Example:**
```
Event 1: http://example.com/video.mp4 (8-9 AM)
Event 2: http://example.com/video.mp4 (2-3 PM)  ← Duplicate!
```

**Action:** ScheduleFlow removes one, keeps the other.

### Understanding Conflicts

A conflict is detected when:
- **Two videos scheduled at same time**
- **Overlapping timeslots**

**Example:**
```
Event 1: 8:00-9:00 AM
Event 2: 8:30-9:30 AM  ← Overlaps!
```

**Action:** ScheduleFlow reports conflict; user must resolve manually.

---

## Dashboard & Statistics

### Calendar View
Click **📊 STATS** to see:
- **Total events** - Number of videos scheduled
- **Duration** - Total hours covered
- **Coverage** - What percentage of time has content
- **Upcoming** - Next 5 scheduled events

### Real-time Updates
- Refreshes automatically every 30 seconds
- Shows live schedule status
- Toast notifications for important events

---

## Common Tasks

### Task 1: Import M3U Playlist

**Option 1: Convert to XML first**
1. Open M3U file in text editor
2. For each URL, create an event with start/end times
3. Save as XML
4. Import via ScheduleFlow

**Option 2: Use external tools**
- M3U → CSV conversion tools
- Then convert CSV → XML
- Then import

### Task 2: Fill 24 Hours of Content

1. Click **📋 SCHEDULE**
2. Enter 4-5 of your most popular videos
3. Set duration: **24 hours**
4. Set cooldown: **48 hours** (prevents repeating same video too soon)
5. Enable shuffle: **Yes**
6. Click **Generate**

Result: ScheduleFlow fills entire 24-hour period!

### Task 3: Create Weekly Schedule

1. Import schedule for **Monday**
2. Create schedule for **Tuesday** (different videos)
3. Create schedule for **Wednesday** (repeat of Monday videos, different times)
4. Repeat for remaining days
5. Export all as single XML file

### Task 4: Handle Large Files

**Problem:** Importing 1000+ events causes timeout

**Solution:**
1. Split file into smaller chunks (100 events each)
2. Import chunks separately
3. Results combined automatically

---

## Troubleshooting

### Problem: Import Fails
**Cause:** Malformed XML/JSON  
**Solution:**
- Check file format (see examples above)
- Ensure all tags closed properly
- Validate with: `curl -X POST http://localhost:5000/api/import-schedule ...`

### Problem: Duplicate Events
**Cause:** Same video listed twice  
**Solution:**
- ScheduleFlow auto-removes duplicates
- Check import report for details
- Re-import if needed

### Problem: Schedule Conflicts
**Cause:** Overlapping timeslots  
**Solution:**
- Adjust event times manually
- Or delete conflicting event
- Re-import after fixing

### Problem: Empty Calendar
**Cause:** No schedule created yet  
**Solution:**
1. Click **📋 SCHEDULE**
2. Enter video URLs
3. Click **Generate Schedule**

### Problem: Server Not Responding
**Cause:** API server is down  
**Solution:**
```bash
# Restart server (if in development)
node api_server.js

# Check if running
curl http://localhost:5000/api/system-info
```

### Problem: Exported File is Blank
**Cause:** No schedule exists yet  
**Solution:**
1. Create a schedule first (📋 SCHEDULE)
2. Then export (📤 EXPORT)

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `I` | Open Import modal |
| `S` | Open Schedule modal |
| `E` | Open Export modal |
| `?` | Show help |
| `Esc` | Close modal |

---

## Best Practices

### For Campus TV
1. **Import class schedule** as base
2. **Create weekly schedule** for each day
3. **Set cooldown to 72 hours** (no video repeats within 3 days)
4. **Export as XML** for CasparCG integration

### For Hotel TV
1. **Import content catalog**
2. **Create 24-hour loop** with promotional videos
3. **Rotate content daily** for freshness
4. **Export twice daily** (day/night rotation)

### For YouTube Live
1. **Import existing playlist**
2. **Create 12-hour schedule** for each stream
3. **Use shuffle: Yes** for variety
4. **Export as JSON** for custom webhook

### For Local Broadcasters
1. **Import professional EPG**
2. **Create 7-day master schedule**
3. **Export to CasparCG** for automation
4. **Back up exports** for compliance

---

## Performance Tips

### For Large Libraries (1000+ videos)
1. Split import into smaller files (100-200 events)
2. Process separately
3. Results merge automatically

### For Real-time Updates
1. Refresh dashboard (📊 STATS) manually
2. Or wait for auto-refresh (every 30 seconds)

### For Faster Exports
1. Export single schedule (not all)
2. Format as JSON (smaller file)
3. Or XML for professional engines

---

## Data Privacy

### What ScheduleFlow Stores
- ✅ Your schedule data (local JSON files)
- ✅ Your video URLs
- ✅ Import history

### What ScheduleFlow Does NOT Store
- ❌ Your account information
- ❌ Analytics/tracking data
- ❌ Third-party integrations

### Backups
Store your data safely:
```bash
# Back up all schedules
cp -r schedules/ schedules.backup.$(date +%Y%m%d)

# Back up configuration
cp m3u_matrix_settings.json m3u_matrix_settings.json.backup
```

---

## Advanced Features

### Cooldown System
**What it does:** Prevents the same video from playing twice within 48 hours

**Example:**
```
08:00 - Video1 (plays)
09:00 - Video2
...
Next day
08:00 - Video1 (blocked - only 24 hours have passed)
08:00 - Video3 (plays instead - not played recently)
...
Third day
08:00 - Video1 (allowed - 56 hours have passed)
```

### Conflict Detection
**What it does:** Identifies overlapping timeslots

**How to resolve:**
1. Check import report
2. Adjust event times
3. Or delete conflicting events
4. Re-import if needed

### Duplicate Detection
**What it does:** Finds identical videos by URL hash

**How it works:**
- MD5 hash of each URL computed
- Identical hashes = duplicates
- Automatically removed on import

---

## FAQ

**Q: What time format should I use?**  
A: ISO 8601 UTC format: `2025-11-23T08:00:00Z`

**Q: Can I edit a schedule after importing?**  
A: Yes, export as JSON, edit manually, re-import

**Q: How many videos can I schedule?**  
A: Unlimited (tested with 1000+ events)

**Q: What's the cooldown for?**  
A: Prevents viewer fatigue from seeing same video too often

**Q: Can I have different cooldowns for different videos?**  
A: Not yet; global cooldown only (48 hours default)

**Q: What's the maximum schedule duration?**  
A: Up to 1 month (24-168 hours per operation)

**Q: Does ScheduleFlow integrate with CasparCG?**  
A: Yes; export to XML format for CasparCG import

**Q: Can I schedule multiple channels?**  
A: Create separate schedules per channel, export separately

---

## Support Resources

### Check System Status
```
http://localhost:5000/api/system-info
```

### View Schedules
```
http://localhost:5000/api/schedules
```

### View Configuration
```
http://localhost:5000/api/config
```

### Get Help
1. Check troubleshooting section (above)
2. Review API documentation (API_DOCUMENTATION.md)
3. Check deployment guide (DEPLOYMENT_GUIDE.md)

---

## Updates & Version History

**v2.0.0** (Nov 22, 2025)
- ✅ XML/JSON import
- ✅ Auto-schedule with cooldown
- ✅ XML/JSON export
- ✅ Duplicate detection
- ✅ Conflict detection
- ✅ Interactive dashboard
- ✅ Responsive design
- ✅ Toast notifications
- ✅ 48-hour cooldown enforcement
- ✅ Persistent cooldown history

---

## Keyboard Reference

| Feature | Shortcut |
|---------|----------|
| Import | `I` |
| Schedule | `S` |
| Export | `E` |
| Stats | `D` |
| Help | `?` |

---

**Last Updated:** November 22, 2025  
**Status:** Complete  
**Support:** See API_DOCUMENTATION.md for technical details
