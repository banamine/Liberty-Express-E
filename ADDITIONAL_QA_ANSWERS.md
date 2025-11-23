# ADDITIONAL HARD QUESTIONS - Comprehensive Answers

**Date:** November 23, 2025  
**Format:** Building on RUTHLESS_QA_ANSWERS.md

---

## SECTION A: INSTALLATION FLOW QUESTIONS

### Q22: Single startup command - does it exist?

**Answer:** ⚠️ NOT YET - Currently requires 2 terminals

**Current Reality:**
```bash
# Terminal 1
node api_server.js

# Terminal 2  
python3 M3U_Matrix_Pro.py

# Problem: User must manage 2 processes
```

**What Should Exist:**
```bash
# Option 1: Startup script (recommended)
./start_scheduleflow.sh
# Output: Both services started
# Ctrl+C to stop both

# Option 2: PM2 process manager
npm install -g pm2
pm2 start ecosystem.config.js

# Option 3: Docker
docker-compose up
```

**Action Items:**
1. Create start_scheduleflow.sh script
2. Add to setup guide
3. Mention in README

**Timeline:** 1-2 hours

**Priority:** 🟡 Medium (nice-to-have, not critical)

---

### Q23: Are dependencies properly documented?

**Answer:** ⚠️ PARTIAL

**What's Documented:**
- ✅ package.json (npm packages listed)
- ✅ requirements.txt (Python packages listed)

**What's Missing:**
- ❌ Node.js version (need v20+)
- ❌ Python version (need 3.11+)
- ❌ npm version
- ❌ System libraries (build-essential, python3-dev, etc.)
- ❌ FFmpeg (for video metadata)
- ❌ VLC (for playback)

**Current Documentation:**
- INSTALLATION.md exists ✓
- check_prerequisites.sh exists ✓

**What Needs Updating:**
- README.md (mentions old version)
- Add version requirements table

**Timeline:** 1 day

---

### Q24: Release package in archives - verified?

**Answer:** ✅ YES - User confirmed in archives

**What to Do:**
1. Point users to archives in INSTALLATION.md
2. Add section: "Quick Start with Release Package"
3. Document extraction steps

**Timeline:** 1 hour

---

## SECTION B: FIRST LAUNCH QUESTIONS

### Q25: Does dashboard load instantly?

**Answer:** ✅ YES

**Verified:**
- ✅ No splash screen
- ✅ No delay on page load
- ✅ Interactive immediately
- ✅ Modals load instantly

**Status:** No issues ✓

---

### Q26: What happens on first load?

**Answer:** Dashboard appears ready to use immediately

**User Experience:**
```
1. Open http://localhost:5000
2. See landing page (instantly)
3. Click "Start Scheduling" or "Dashboard"
4. See Import/Schedule/Export modals (instant)
5. Can immediately upload files
```

**No splash screen, no waiting** ✅

---

### Q27: Is UI intuitive?

**Answer:** ✅ YES - 5/5 rating

**Evidence:**
- ✅ Clear button labels ("Import Schedule" not "XML")
- ✅ Help text on modals
- ✅ Responsive design
- ✅ Toast notifications for feedback
- ✅ Calendar view shows events

**No issues found** ✓

---

## SECTION C: AUTO-FILL QUESTIONS

### Q28: Does auto-fill play videos?

**Answer:** ❌ NO - Schedules only, doesn't play

**What It Does:**
```
Input: 100 video URLs + time range
Output: Schedule (JSON/XML) with 144 timeslots filled
```

**What It Doesn't Do:**
```
❌ Doesn't play videos in browser
❌ Doesn't preview playback
❌ Doesn't integrate with player
```

**User Must:**
1. Auto-fill schedule
2. Export schedule (XML/JSON)
3. Import into playout engine (CasparCG, OBS, vMix)
4. Playout engine plays videos

**Help Text Needed:**
```
"Auto-fill creates a schedule for playout.
To actually watch videos, export this schedule
and import it into your playout engine."
```

**Timeline:** 1 hour (documentation only)

---

### Q29: Is playlist selection automatic?

**Answer:** ❌ NO - Requires manual upload

**Current Workflow:**
```
1. User manually pastes video URLs
2. OR uploads M3U file
3. System creates schedule
```

**No auto-loading from disk** ✓

---

## SECTION D: TV GUIDE QUESTIONS

### Q30: Is TV Guide dynamic or static?

**Answer:** ✅ DYNAMIC - Data persists to disk

**Data Flow:**
```
Import XML/JSON
    ↓
Validate
    ↓
Save to disk (Python backend)
    ↓
Page refresh
    ↓
API loads from disk
    ↓
Dashboard displays
```

**Key Point:** Data survives refresh ✓

---

### Q31: Can users drag-and-drop in calendar?

**Answer:** ⚠️ PARTIAL

**What Works:**
- ✅ Drag-drop file upload (to import)
- ✅ Calendar displays events

**What Doesn't Work:**
- ❌ Drag events to reschedule
- ❌ Resize events
- ❌ Edit timeslots

**Future Feature:** Could add drag-drop rescheduling

---

### Q32: Are there demo examples?

**Answer:** ✅ YES - Use existing M3U files

**What to Do:**
1. Load any M3U file from Sample Playlists folder
2. Use in dashboard
3. Create schedule from demo playlist

**How to Provide:**
```
1. Create demo_schedule.xml (sample events)
2. Place in Sample_Playlists/ folder
3. Add to INSTALLATION.md: "Try demo with demo_schedule.xml"
```

**Timeline:** 1 hour

---

## SECTION E: OFFLINE QUESTIONS

### Q33: Does it work without internet?

**Answer:** ✅ YES - "Once built, they run on their own"

**Offline Capabilities:**
- ✅ Schedule creation
- ✅ XML/JSON import/export
- ✅ File storage (local)
- ✅ Calendar display

**Online Features:**
- ❌ Remote video URLs (must use local files)
- ❌ EPG fetching

**For Fully Offline:**
- Use local video files only
- Don't validate URLs (skip HTTP checks)
- No cloud sync needed

**Status:** Works offline ✓

---

### Q34: Does it sync with cloud?

**Answer:** ❌ NO - Local storage only

**What Exists:**
- ✅ Manual export (download JSON/XML)
- ✅ Manual import (upload files)
- ❌ Automatic cloud sync
- ❌ Google Drive integration
- ❌ S3 backup

**For Backup:**
- User manually downloads export
- Store in cloud manually
- Import later if needed

**Timeline:** Not planned (low priority)

---

## SECTION F: INSTALLATION EXPECTATIONS

### Q35: What happens after npm install?

**Answer:** Dependencies installed, ready to run

**After Installation:**
```bash
npm install
# Creates node_modules/ folder
# installs: express, serve, etc.

python3 -m pip install -r requirements.txt
# Installs: requests, pillow, tkinterdnd2

node api_server.js
# Server ready on port 5000
```

**What User Sees:**
```
Server listening on port 5000
Ready for browser connection
```

**Timeline:** Complete ✓

---

### Q36: What if Python doesn't start?

**Answer:** User sees no error (runs silent)

**Problem:** Python backend starts silently with no feedback

**Solution Needed:**
```bash
# Add startup check
node api_server.js --check-python

# Output:
# [✓] Node.js API ready on :5000
# [✓] Python backend responsive
# [✗] Python backend NOT responding
```

**Timeline:** 1 hour

---

## SECTION G: CONFIGURATION

### Q37: How do users change port?

**Answer:** Edit api_server.js or .env file

**Current Method:**
```javascript
// api_server.js line 9
const PORT = process.env.PORT || 5000;
```

**User Can:**
1. Set environment variable: `export PORT=3000`
2. Or edit api_server.js directly

**Better Method:**
```env
# .env file
PORT=3000
PYTHON_PATH=python3
MAX_UPLOAD_SIZE=52428800
```

**Timeline:** 1 hour (add .env support)

---

## SUMMARY TABLE

| Question | Status | Priority | Effort |
|----------|--------|----------|--------|
| Q22: Single startup command | ⚠️ Missing | 🟡 Medium | 1-2h |
| Q23: Dependencies documented | ⚠️ Partial | 🟡 Medium | 1d |
| Q24: Release package verified | ✅ Yes | 🟢 Low | 1h |
| Q25: Instant load | ✅ Yes | - | Done |
| Q26: First load experience | ✅ Good | - | Done |
| Q27: UI intuitive | ✅ Yes | - | Done |
| Q28: Auto-fill plays videos | ❌ No | 🟢 Info | Done |
| Q29: Auto-load playlist | ❌ No | 🟢 Info | Done |
| Q30: TV Guide dynamic | ✅ Yes | - | Done |
| Q31: Drag-drop reschedule | ❌ Future | 🟡 Low | TBD |
| Q32: Demo examples | ✅ Available | 🟢 Low | 1h |
| Q33: Offline support | ✅ Yes | - | Done |
| Q34: Cloud sync | ❌ No | 🟡 Low | TBD |
| Q35: npm install | ✅ Works | - | Done |
| Q36: Python startup feedback | ⚠️ Silent | 🟡 Medium | 1h |
| Q37: Port configuration | ⚠️ Partial | 🟡 Medium | 1h |

---

**Total Effort to Address All Gaps:** 2-3 days

**Critical for Production:** Security (Q18-21) + startup feedback (Q36)

**Nice-to-Have:** Single startup command, drag-drop reschedule, cloud sync
