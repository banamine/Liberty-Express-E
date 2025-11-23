# First Run Guide - Getting Started with ScheduleFlow

**Welcome to ScheduleFlow!** This guide will help you set up and start using the playout scheduler in minutes.

---

## What is ScheduleFlow?

ScheduleFlow is a professional 24/7 playout scheduler for:
- Campus TV stations
- Hotels & hospitality venues
- YouTube live streams
- Local broadcasters
- Any scenario needing continuous video playback

---

## Quick Start (5 minutes)

### Step 1: Access the Dashboard
1. Open your browser to: **http://localhost:5000**
2. You should see the Interactive Hub with menu options

### Step 2: Import Your First Schedule
1. Click **"Import Schedule"** button
2. You have two options:

**Option A: Use Sample Schedule (Recommended)**
- Go to `demo_data/sample_schedule.xml` or `demo_data/sample_schedule.json`
- Click Import and select the file
- The system will import the sample schedule with 5-6 videos

**Option B: Create Your Own**
- Prepare an XML or JSON file with your videos
- Use the format shown in `demo_data/sample_schedule.xml`
- Import and ScheduleFlow will validate it

### Step 3: View Your Schedule
1. Click **"View Schedules"** in the Interactive Hub
2. You'll see:
   - Schedule name
   - Number of videos imported
   - Import date/time
   - Any warnings (duplicates, conflicts)

### Step 4: Schedule Videos
1. Click **"Schedule Playlist"**
2. Select your schedule
3. Set the start time
4. Videos will play in order automatically

### Step 5: Export for Playout
1. Click **"Export Schedule"**
2. Choose format:
   - **XML** - For CasparCG, Vizrt, other broadcast systems
   - **JSON** - For custom automation
3. Download the file
4. Load into your playout engine (OBS, vMix, CasparCG, etc.)

---

## Sample Data Included

We've provided two example schedules in `demo_data/`:

### 1. sample_schedule.xml
```xml
<?xml version="1.0"?>
<schedule>
  <events>
    <event>
      <title>Morning News</title>
      <start>2025-11-24T08:00:00Z</start>
      <videoUrl>https://example.com/news.mp4</videoUrl>
    </event>
  </events>
</schedule>
```

**Use this if:**
- You have XML playlists from another system
- You're importing from a broadcast ERP
- You prefer XML format

### 2. sample_schedule.json
```json
{
  "schedule": [
    {
      "title": "Morning Show",
      "start": "2025-11-24T06:00:00Z",
      "videoUrl": "https://example.com/show.mp4"
    }
  ]
}
```

**Use this if:**
- You're programmatically generating schedules
- You prefer JSON format
- You're building custom integrations

---

## Video Format Requirements

ScheduleFlow supports:
- **Format:** MP4, MOV, MKV, WebM, HLS streams, DASH streams
- **Codec:** H.264/H.265 video, AAC/MP3 audio
- **Size:** No limit (file size handled by browser)
- **URL:** HTTP/HTTPS only (must be publicly accessible)

---

## Auto-Play Behavior

### Does ScheduleFlow Auto-Play Videos?

**YES, in the player pages. NO, in the dashboard.**

- **Dashboard** - Shows schedules, no auto-play
- **Player Pages** - Videos play automatically in sequence
- **Web Player** - Auto-plays next scheduled video
- **Desktop Player** - Can be configured to auto-play

### How to Use Auto-Play

1. Export your schedule to XML or JSON
2. Load into your player:
   - **Web:** Use the generated player HTML
   - **Desktop:** Use the Python desktop app (M3U_Matrix_Pro.py)
   - **Broadcast:** Load into OBS, CasparCG, vMix, etc.
3. Videos will play in scheduled order

### Features

✅ Auto-play next video at scheduled time  
✅ 48-hour cooldown prevents repetition  
✅ Category balancing for variety  
✅ Drag-drop reordering before export  
✅ Time-based clipping support  

---

## Common Workflows

### Workflow 1: Daily News Schedule
1. Create schedule with news segments
2. Set times: 8:00, 12:00, 18:00, 23:00
3. Export to XML
4. Load in broadcast system
5. System plays automatically at each time

### Workflow 2: 24/7 Content Loop
1. Import playlist with 10-20 videos
2. Set start time at midnight
3. Add cooldown to prevent repetition
4. Export and deploy to player
5. Videos loop continuously with 48-hour breaks

### Workflow 3: YouTube Live Stream
1. Create schedule with 4-6 hours of content
2. Set start time to match stream time
3. Export as JSON
4. Load into custom stream controller
5. System feeds videos to YouTube Live

---

## Troubleshooting

### "File Not Found"
**Problem:** Import fails with file not found  
**Solution:** Check the file path is correct and file exists

### "Invalid XML/JSON"
**Problem:** Import fails with parse error  
**Solution:** Use the sample files to check your format

### "Videos Won't Play"
**Problem:** Player loads but videos don't play  
**Solution:**
- Check video URLs are accessible (copy URL in browser)
- Verify video format is supported
- Check for CORS issues if cross-origin

### "Schedule Not Imported"
**Problem:** Import button doesn't work  
**Solution:**
- Ensure file is XML or JSON
- Validate file format against sample
- Check file size is under 50MB

---

## Next Steps

1. **Explore the Dashboard**
   - View your imported schedules
   - See what warnings appear
   - Try the calendar view

2. **Export Your Schedule**
   - Try both XML and JSON formats
   - Open in a text editor to see structure
   - Load into your preferred player

3. **Set Up Auto-Play**
   - Deploy the exported schedule to your player
   - Test that videos play in order
   - Verify timing is correct

4. **Customize**
   - Drag-drop to reorder videos
   - Set categories for balancing
   - Add duration and metadata

---

## Key Features to Know

✨ **Intelligent Scheduling**
- Drag-and-drop interface
- Auto-filler for gaps
- Category balancing
- Multi-week planning

✨ **Professional Export**
- XML format for CasparCG, Vizrt, EBU
- JSON for custom integration
- M3U playlists for VLC/media players
- Standalone HTML pages

✨ **Validation Engine**
- Duplicate detection & removal
- Conflict detection (overlapping times)
- 48-hour cooldown enforcement
- Schema validation

✨ **Security**
- Admin API key for sensitive operations
- File size limits (50MB)
- Input validation
- User-friendly error messages

---

## Where to Go From Here

**Documentation:**
- `ADMIN_SETUP.md` - Admin operations guide
- `OFFLINE_MODE.md` - Using ScheduleFlow offline
- `SECURITY_ASSESSMENT.md` - Security details
- `api_config.json` - API reference

**Sample Files:**
- `demo_data/sample_schedule.xml` - XML example
- `demo_data/sample_schedule.json` - JSON example

**Dashboard:**
- http://localhost:5000 - Main interface
- Try importing sample schedules
- Export and test in your player

---

## Support

**Issues?** Check the documentation or see RUTHLESS_QA_ANSWERS.md for common questions.

**Ready to start?** Open http://localhost:5000 and click "Import Schedule"!

---

**Welcome aboard! Let's schedule some content! 📺**
