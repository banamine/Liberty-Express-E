# SYSTEM CONNECTION DIAGRAM - Visual Guide

## 🔗 THE COMPLETE CONNECTION MAP

### Import Resolution at Runtime

```
┌─────────────────────────────────────────────────────────────────┐
│                   WHEN M3U_MATRIX_PRO.py STARTS                │
└─────────────────────────────────────────────────────────────────┘

Step 1: File location
────────────────────────────────────────────────────────────────
__file__ = /home/runner/workspace/Applications/M3U_MATRIX_PRO.py
Path(__file__).resolve() = /home/runner/workspace/Applications/M3U_MATRIX_PRO.py
Path(__file__).parent = /home/runner/workspace/Applications/
Path(__file__).parent.parent = /home/runner/workspace/  ← PROJECT_ROOT


Step 2: Add to sys.path
────────────────────────────────────────────────────────────────
sys.path.insert(0, "/home/runner/workspace/Core_Modules")
sys.path.insert(0, "/home/runner/workspace")

sys.path is now: [
    "/home/runner/workspace/Core_Modules",
    "/home/runner/workspace",
    ... (other standard paths)
]


Step 3: Import resolution
────────────────────────────────────────────────────────────────
When code does: from tv_schedule_db import TVScheduleDB

Python searches:
1. "/home/runner/workspace/Core_Modules/" ← FOUND! ✓
   tv_schedule_db.py exists here
2. (No need to check further)


When code does: from parsers.m3u_parser import M3UParser

Python searches:
1. "/home/runner/workspace/Core_Modules/parsers/" ← FOUND! ✓
   m3u_parser.py exists here
2. (No need to check further)
```

---

## 📊 DEPENDENCY GRAPH

```
┌────────────────────────────────────────────────────────────────┐
│                     USER LAUNCHES APP                          │
└────────────────────────────────────────────────────────────────┘
                              ↓
                      M3U_MATRIX_PRO.py
                      (Applications/)
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
          READS:        IMPORTS:        LAUNCHES:
      • M3U files   Core_Modules/*    TV_SCHEDULE_CENTER.py
      • EPG files   ├─ TVScheduleDB      (subprocess)
      • Playlists   ├─ AutoScheduler         ↓
                    ├─ M3UParser
                    ├─ EPGParser       Core_Modules/*
                    ├─ UndoManager     ├─ TVScheduleDB
                    ├─ GitHubDeploy    ├─ AutoScheduler
                    ├─ ChannelValidator├─ ScheduleManager
                    └─ ProgressManager └─ WebEPGServer
                              ↓
                    CREATES:   ↓
              • schedule.db ←──┘
              (SQLite)
                    
                              ↓
                    GENERATES:
              Web_Players/ →  Generators
              • Templates      ↓
              • CSS/JS    WRITES OUTPUT:
              • Code      M3U_Matrix_Output/
                         generated_pages/
                         ├─ nexus_tv_output.html
                         ├─ buffer_tv_output.html
                         ├─ performance_player_output.html
                         ├─ interactive_hub.html
                         └─ ... (all player pages)
```

---

## 🗂️ FOLDER TREE WITH IMPORT PATHS

```
/home/runner/workspace/ ← PROJECT_ROOT
│
├── Applications/
│   ├── M3U_MATRIX_PRO.py
│   │   ├─ sys.path.insert(0, PROJECT_ROOT / "Core_Modules")
│   │   │
│   │   ├─ from tv_schedule_db import TVScheduleDB
│   │   │  └─ Resolved to: Core_Modules/tv_schedule_db.py ✓
│   │   │
│   │   ├─ from auto_scheduler import AutoScheduler
│   │   │  └─ Resolved to: Core_Modules/auto_scheduler.py ✓
│   │   │
│   │   ├─ from parsers.m3u_parser import M3UParser
│   │   │  └─ Resolved to: Core_Modules/parsers/m3u_parser.py ✓
│   │   │
│   │   ├─ from undo.undo_manager import UndoManager
│   │   │  └─ Resolved to: Core_Modules/undo/undo_manager.py ✓
│   │   │
│   │   └─ subprocess.Popen([sys.executable, "TV_SCHEDULE_CENTER.py"])
│   │      └─ Launches: Applications/TV_SCHEDULE_CENTER.py (new process) →
│   │
│   ├── TV_SCHEDULE_CENTER.py
│   │   ├─ sys.path.insert(0, PROJECT_ROOT / "Core_Modules")
│   │   │  (same calculation, same result)
│   │   │
│   │   ├─ from tv_schedule_db import TVScheduleDB
│   │   │  └─ Resolved to: Core_Modules/tv_schedule_db.py ✓
│   │   │
│   │   ├─ from auto_scheduler import AutoScheduler
│   │   │  └─ Resolved to: Core_Modules/auto_scheduler.py ✓
│   │   │
│   │   └─ Creates schedules via TVScheduleDB
│   │      └─ Writes to: schedule.db (same directory)
│   │
│   └── VIDEO_PLAYER_PRO.py
│       └─ (same pattern as above)
│
├── Core_Modules/
│   ├── tv_schedule_db.py ← TVScheduleDB
│   │   └─ import sqlite3
│   │   └─ db_path = Path.cwd() / "schedule.db"
│   │      └─ Current working directory: Applications/
│   │      └─ Database location: Applications/schedule.db
│   │
│   ├── auto_scheduler.py ← AutoScheduler
│   │   └─ import tv_schedule_db (found via sys.path)
│   │   └─ Uses: TVScheduleDB to store data
│   │
│   ├── schedule_manager.py ← ScheduleManager
│   │   └─ Helper class for AutoScheduler
│   │
│   ├── web_epg_server.py ← WebEPGServer
│   │   └─ HTTP server on port 8000
│   │   └─ Accesses: schedule.db via TVScheduleDB
│   │
│   ├── parsers/
│   │   ├── m3u_parser.py ← M3UParser
│   │   └── epg_parser.py ← EPGParser
│   │
│   ├── validators/
│   │   └── channel_validator.py ← ChannelValidator
│   │
│   ├── undo/
│   │   └── undo_manager.py ← UndoManager
│   │
│   ├── cache/
│   │   └── simple_cache.py ← SimpleCache
│   │
│   ├── github_deploy.py ← GitHubDeploy
│   │   └─ Pushes to GitHub
│   │
│   └── settings/
│       └── settings_manager.py ← SettingsManager
│
├── Web_Players/ ← TEMPLATES (NOT GENERATED)
│   ├── nexus_tv.html
│   │   └─ Template with: {{PLAYLIST_DATA}}
│   │   └─ Generators COPY and FILL this
│   │
│   ├── buffer_tv.html
│   ├── performance_player.html
│   ├── multi_channel.html
│   ├── simple_player.html
│   ├── rumble_channel.html
│   └── ... (11+ total)
│
├── M3U_Matrix_Output/
│   ├── generated_pages/
│   │   ├── interactive_hub.html ← GENERATED (self-contained)
│   │   ├── nexus_tv_output.html ← GENERATED (self-contained)
│   │   ├── buffer_tv_output.html ← GENERATED (self-contained)
│   │   └── ... (more generated pages)
│   │
│   └── playlists/
│       └── playlist_1.json ← Playlist data
│
├── schedule.db ← DATABASE (created at runtime)
│   ├─ Table: channels
│   ├─ Table: shows
│   ├─ Table: schedules
│   └─ Table: time_slots
│
└── replit.md ← Documentation
```

---

## 🔄 DATA FLOW: FROM GUI TO OUTPUT PAGES

```
┌──────────────────┐
│   USER LAUNCHES  │
│  M3U_MATRIX_PRO  │
└────────┬─────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ 1. Load settings from JSON files    │
    │ 2. Initialize Core_Modules classes  │
    │ 3. Setup GUI with Tkinter           │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ USER ACTION: Open Schedule Center   │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ subprocess.Popen() → TV_SCHEDULE_   │
    │ CENTER.py (new Python process)      │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ TV_SCHEDULE_CENTER initializes:     │
    │ • Adds Core_Modules to sys.path     │
    │ • Creates TVScheduleDB instance     │
    │ • Creates AutoScheduler instance    │
    │ • Opens schedule.db from same dir   │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ USER ACTION: Import from folder     │
    │ AutoScheduler.import_folder()       │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ Scan folder for video files         │
    │ Create shows in schedule.db         │
    │ TVScheduleDB.add_show()             │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ Back in M3U_MATRIX_PRO:             │
    │ USER ACTION: Generate Page          │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ 1. Get channels from self.channels  │
    │ 2. Select template: nexus_tv.html   │
    │ 3. Create NextusTVGenerator()       │
    │ 4. Call generator.generate()        │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ Generator code:                     │
    │ 1. Read Web_Players/nexus_tv.html   │
    │ 2. Convert channels to JSON         │
    │ 3. Embed data in HTML               │
    │ 4. Write to M3U_Matrix_Output/      │
    │    generated_pages/nexus_tv_output  │
    │    .html                            │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ File created: nexus_tv_output.html  │
    │ • Contains embedded CSS             │
    │ • Contains embedded JavaScript      │
    │ • Contains embedded playlist data   │
    │ • Self-contained = works offline    │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ USER ACTION: Open in browser        │
    │ webbrowser.open(file:///.../)       │
    └────────────┬────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │ Browser displays:                   │
    │ • NEXUS TV player                   │
    │ • All channels loaded               │
    │ • Ready to play streams             │
    └─────────────────────────────────────┘
```

---

## 🎯 CRITICAL IMPLEMENTATION DETAILS

### 1. How sys.path Injection Works

```python
# File: /home/runner/workspace/Applications/M3U_MATRIX_PRO.py
# Line 20-29

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# __file__ = /home/runner/workspace/Applications/M3U_MATRIX_PRO.py
# .resolve() = absolute path
# .parent = /home/runner/workspace/Applications/
# .parent = /home/runner/workspace/  ← This is PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT / "Core_Modules"))
# Add /home/runner/workspace/Core_Modules/ to front of search path

# Now this works:
from tv_schedule_db import TVScheduleDB
# Python finds: /home/runner/workspace/Core_Modules/tv_schedule_db.py
```

### 2. Subprocess Independence

```python
# File: /home/runner/workspace/Applications/M3U_MATRIX_PRO.py
# Method: open_schedule_center() at line 1214

subprocess.Popen([sys.executable, str(schedule_center_path)])
# Launches COMPLETELY NEW Python process
# New process has FRESH sys.path
# But TV_SCHEDULE_CENTER.py does SAME calculation:
#   PROJECT_ROOT = Path(__file__).resolve().parent.parent
#   Result: /home/runner/workspace/ (SAME!)
#   sys.path.insert(0, str(PROJECT_ROOT / "Core_Modules"))
#   Result: /home/runner/workspace/Core_Modules/ (SAME!)

# Both processes access SAME Core_Modules and SAME schedule.db
```

### 3. Database Sharing

```python
# Both M3U_MATRIX_PRO and TV_SCHEDULE_CENTER run from:
os.chdir(Path(__file__).parent)  # Line 142 in M3U_MATRIX_PRO
# Working directory: /home/runner/workspace/Applications/

# TVScheduleDB does:
db_path = Path.cwd() / "schedule.db"
# Result: /home/runner/workspace/Applications/schedule.db

# BOTH processes create/open SAME database file!
# Thread-safe because SQLite handles locking
```

### 4. Template to Output Conversion

```python
# In generator.generate() method:

# 1. FIND TEMPLATE
template_path = Path(__file__).parent.parent.parent / "Web_Players"
# __file__ = /home/runner/workspace/Core_Modules/generators/nexus_tv_gen.py
# .parent = /home/runner/workspace/Core_Modules/generators/
# .parent = /home/runner/workspace/Core_Modules/
# .parent = /home/runner/workspace/
# + "Web_Players" = /home/runner/workspace/Web_Players/

# 2. READ TEMPLATE
template_file = template_path / "nexus_tv.html"
html_template = open(template_file).read()

# 3. EMBED DATA
channels_json = json.dumps(channels)
modified_html = html_template.replace(
    "<!--PLAYLIST_DATA-->",
    f"<script>const PLAYLIST = {channels_json};</script>"
)

# 4. WRITE OUTPUT
output_path = Path(output_dir) / "nexus_tv_output.html"
# output_dir = /home/runner/workspace/M3U_Matrix_Output/generated_pages/
output_path.write_text(modified_html)

# Result: /home/runner/workspace/M3U_Matrix_Output/generated_pages/
#         nexus_tv_output.html (self-contained, ready to open)
```

---

## ✅ VERIFICATION CHECKLIST

**All files can find each other because:**

- [x] Every .py file calculates PROJECT_ROOT independently
- [x] Every .py file adds Core_Modules to sys.path
- [x] Core_Modules classes are found via sys.path injection
- [x] Web_Players templates stored in known location (Web_Players/)
- [x] Generators use relative paths to find templates
- [x] Database stored in working directory (shared by all processes)
- [x] Output written to known location (M3U_Matrix_Output/generated_pages/)
- [x] Generated pages are self-contained (embedded data + code)
- [x] No hardcoded absolute paths
- [x] Works with subprocess launches
- [x] Works with different working directories

---

## 🚨 IF SOMETHING BREAKS

| Problem | Solution |
|---------|----------|
| Import error: `from tv_schedule_db import` fails | Check PROJECT_ROOT calculation. Verify sys.path includes /workspace/Core_Modules/ |
| Database not found | Check working directory: `print(os.getcwd())`. Verify schedule.db exists there |
| Template not found | Check Web_Players/ path calculation. Use `print()` to debug Path operations |
| Generated pages blank | Check HTML file exists. Open in browser and view page source. Verify data was embedded |
| Schedule data not saving | Check database file permissions. Verify TVScheduleDB initialized correctly |
| Web players don't load | Open with `file://` protocol not `http://`. Check for JavaScript errors in console |

---

**Summary:** Everything is connected via sys.path injection + relative paths.
No magic, no globals, all calculated at runtime. Works anywhere.

Generated: November 22, 2025
Status: Production Ready
