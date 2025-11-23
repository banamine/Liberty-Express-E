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

## Auto-Play Behavior - IMPORTANT TO UNDERSTAND

### The Simple Answer

**Dashboard:** No auto-play (it's for management only)  
**Players:** YES, auto-play (videos play in sequence)

---

### What This ACTUALLY Means

#### IN THE DASHBOARD (http://localhost:5000)
When you import a schedule and view it in the dashboard:
- You see a list of videos
- You can drag-drop to reorder
- You can view conflicts/gaps
- **Videos DO NOT play** - the dashboard is just for managing schedules

**What happens:** You view, edit, and organize. That's it.

#### IN THE PLAYER (After you export)
When you export the schedule and open it in a player:
- Player opens with schedule loaded
- Videos **play automatically** in the order you scheduled them
- Next video starts when previous one ends
- Continues in sequence through all videos

**What happens:** Videos play continuously without needing clicks

---

### Concrete Examples

#### Example 1: Using the Web Player

**Step 1: Import Schedule (Dashboard)**
```
1. Go to http://localhost:5000
2. Click "Import Schedule"
3. Select demo_data/sample_schedule.xml
4. You see: "6 events imported"
```
**Result:** Schedule is in dashboard. NO VIDEOS PLAY YET.

**Step 2: Export to Player (Web)**
```
1. Click "Export Schedule"
2. Choose "XML" or "JSON"
3. Download the file
4. Open the file in a browser
```
**Result:** Player opens. Videos START PLAYING automatically.

**What you see:**
- First video starts playing immediately
- When it finishes, next video plays automatically
- No buttons to click between videos
- Videos play in scheduled order
- 48-hour cooldown prevents repeats

---

#### Example 2: Using Desktop Player

**Step 1: Export from Dashboard**
```
1. http://localhost:5000 → Export Schedule
2. Save XML file
```

**Step 2: Open in Desktop Player**
```
1. Run: python3 M3U_Matrix_Pro.py
2. Load the exported schedule
3. Videos START PLAYING automatically
```

**What you see:**
- Player UI opens
- Current video playing
- Next video queued
- Playlist showing remaining videos
- Videos advance automatically

---

#### Example 3: Broadcast System (OBS/CasparCG)

**Step 1: Export to XML**
```
1. Dashboard → Export Schedule
2. Save as schedule.xml
```

**Step 2: Load into Broadcast System**
```
1. OBS/CasparCG/vMix: Import schedule.xml
2. Videos load into playlist
3. System plays automatically based on schedule time
```

**What you see:**
- Broadcast system shows loaded videos
- Auto-play engine follows schedule times
- Videos play at scheduled times
- 24/7 continuous operation

---

### Auto-Play Features Explained

**What AUTO-PLAYS means:**
- ✅ Next video starts automatically (no manual clicks needed)
- ✅ Timing follows your schedule
- ✅ Videos play in sequence you defined
- ✅ Repeating content prevented by 48-hour cooldown

**What does NOT auto-play:**
- ❌ Dashboard import (just management)
- ❌ First video in player (you export, player handles this)
- ❌ Videos with broken URLs (player will show error)

---

### Common Confusion CLEARED UP

**"Do I need to click play?"**
- Dashboard: YES (or don't, just manage there)
- Player: NO (videos play automatically)

**"When do videos start playing?"**
- Dashboard: Never - it's just management
- Web Player: Immediately when you open/export
- Broadcast System: At scheduled time you set

**"Can I manually control playback?"**
- Dashboard: Yes, drag-drop to reorder before export
- Web Player: Limited (next/previous buttons usually available)
- Broadcast: Depends on your system

**"What if I only want some videos to play?"**
- Dashboard: Don't import videos you don't want
- Or: Export only selected videos
- Player will play whatever is exported

---

### The Workflow (Crystal Clear)

```
STEP 1: DASHBOARD (Management, NO playback)
┌─────────────────────────────┐
│ Import schedule.xml         │
│ (videos are now in system)   │
│                             │
│ View the list              │
│ Drag-drop to reorder       │
│ Check conflicts            │
│ (Still no playback)         │
└─────────────────────────────┘
        ↓
STEP 2: EXPORT (Prepare for playback)
┌─────────────────────────────┐
│ Export to XML or JSON        │
│ (Creates player file)        │
│ Save: player_schedule.xml    │
└─────────────────────────────┘
        ↓
STEP 3: PLAYER (Automatic playback)
┌─────────────────────────────┐
│ Open player_schedule.xml     │
│ in browser or desktop app    │
│                             │
│ VIDEOS AUTO-PLAY:           │
│ • First video starts now     │
│ • Videos play continuously   │
│ • No clicks needed           │
│ • Follows schedule times     │
└─────────────────────────────┘
```

---

### Remember

- **Dashboard** = Scheduling tool (no video playback)
- **Player** = Playback engine (auto-play videos)
- **Export** = Bridge between dashboard and player

If videos don't play, you're probably still in the dashboard. Open the exported file in a player instead.  

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
