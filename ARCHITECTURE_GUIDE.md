# ScheduleFlow Architecture Guide

**Version:** 2.0.0  
**Date:** November 22, 2025  
**Document:** Complete system architecture overview

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Interactive Hub Dashboard                          │    │
│  │  ├─ Import modal (XML/JSON)                        │    │
│  │  ├─ Schedule modal (with auto-fill)                │    │
│  │  ├─ Export modal (format selection)                │    │
│  │  ├─ Calendar view (event display)                  │    │
│  │  └─ Stats dashboard (real-time updates)            │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP REST API
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Express.js API Server (Port 5000)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Routes (24 endpoints)                              │    │
│  │  ├─ /api/import-schedule (→ Python)               │    │
│  │  ├─ /api/schedules (→ Python)                     │    │
│  │  ├─ /api/schedule-playlist (→ Python)             │    │
│  │  ├─ /api/export-schedule-* (→ Python)             │    │
│  │  └─ /api/* (config, pages, playlists)             │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Middleware Stack                                   │    │
│  │  ├─ JSON parser (express.json)                     │    │
│  │  ├─ CORS handler (Allow all origins)              │    │
│  │  ├─ Cache-control (no-cache headers)              │    │
│  │  └─ Static file server (generated_pages/)         │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    Child Process
                           │
┌──────────────────────────▼──────────────────────────────────┐
│          Python Scheduling Engine (M3U_Matrix_Pro.py)        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  8 Core Classes                                     │    │
│  │  ├─ TimestampParser (ISO 8601 normalization)      │    │
│  │  ├─ ScheduleValidator (XML/JSON validation)       │    │
│  │  ├─ DuplicateDetector (MD5 hash comparison)       │    │
│  │  ├─ ConflictDetector (overlapping timeslots)      │    │
│  │  ├─ ScheduleAlgorithm (Fisher-Yates + cooldown)  │    │
│  │  ├─ CooldownManager (persistent storage)          │    │
│  │  ├─ CooldownValidator (violation checking)        │    │
│  │  └─ M3UMatrixPro (orchestrator/main)             │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    JSON Files        Schedule Files    Cooldown History
         │                 │                 │
┌────────▼────────┐ ┌──────▼──────┐ ┌──────▼──────┐
│    Config       │ │  Schedules/ │ │ cooldown_   │
│    Settings     │ │  *.json     │ │ history.json│
└─────────────────┘ └─────────────┘ └─────────────┘
```

---

## Component Deep Dive

### 1. Frontend Layer (Browser)

**Technology:** HTML5 + CSS + JavaScript (vanilla, no framework)

**Components:**
- **interactive_hub.html** (36KB)
  - Main dashboard
  - Import/Export/Schedule modals
  - Event calendar
  - Stats display
  - Toast notifications

**Hosting:** Served by Express.js from `generated_pages/` directory

**Responsiveness:** Yes (CSS media queries, viewport meta tag)

**Communication:** Fetch API → REST endpoints

---

### 2. API Layer (Express.js)

**Framework:** Express.js 4.x  
**Port:** 5000  
**Endpoints:** 24 routes  

**Middleware Stack:**
```javascript
// 1. Body parser
app.use(express.json());

// 2. CORS headers
app.use(headers middleware);

// 3. Dynamic HTML routing
app.use(html routing middleware);

// 4. Static file serving
app.use('/generated_pages', express.static('generated_pages'));
app.use('/M3U_Matrix_Output', express.static('M3U_Matrix_Output'));
app.use(express.static('generated_pages'));

// 5. Route handlers
app.get('/api/system-info', handler);
app.post('/api/import-schedule', handler);
// ... 22 more routes

// 6. Error handling
app.use(error handler);
```

**Request Flow:**
```
Browser Request
    ↓
Express Middleware
    ↓
Route Handler
    ├─ For data operations: spawn Python process
    ├─ For file operations: read/write sync (BLOCKING)
    └─ Return JSON response
    ↓
Browser Response
```

**Issues:**
- ⚠️ Synchronous file I/O blocks all requests
- ⚠️ Process spawning per request (memory leak at scale)
- ✅ Good error handling
- ✅ CORS properly configured

---

### 3. Python Scheduling Engine

**File:** M3U_Matrix_Pro.py (1,095 lines)

**Architecture:** 8 Classes (object-oriented, modular)

#### Class Hierarchy

```
CooldownManager (lines 21-93)
└─ Manages cooldown history persistence
   ├─ Load history from JSON
   ├─ Save history after each operation
   ├─ Check if video on cooldown
   └─ Get cooldown end time

CooldownValidator (lines 94-137)
└─ Validates schedules for cooldown violations
   ├─ Check schedule for violations
   └─ Report specific conflicts

TimestampParser (lines 138-176)
└─ ISO 8601 timestamp handling
   ├─ Parse ISO 8601 strings
   ├─ Normalize to UTC
   ├─ Convert back to string
   └─ Handle timezone offsets (GMT+8, GMT-5, etc.)

ScheduleValidator (lines 177-291)
└─ XML/JSON schema validation
   ├─ Validate XML schedule structure
   ├─ Validate JSON schedule structure
   ├─ Check required fields
   ├─ Check timestamp format
   ├─ Check time order (start < end)
   └─ Aggregate validation errors

DuplicateDetector (lines 292-329)
└─ MD5-based duplicate detection
   ├─ Compute MD5 hash of video URL
   └─ Compare hashes to find duplicates

ConflictDetector (lines 330-376)
└─ Overlapping timeslot detection
   ├─ Find overlapping events
   └─ Report specific overlaps

ScheduleAlgorithm (lines 377-546)
└─ Main scheduling logic
   ├─ Fisher-Yates shuffle
   ├─ 48-hour cooldown enforcement
   ├─ Gap-filling algorithm
   ├─ Distribution across time period
   └─ Return scheduled events

M3UMatrixPro (lines 547-1095)
└─ Main orchestrator class
   ├─ import_schedule_xml()
   ├─ import_schedule_json()
   ├─ export_schedule_xml()
   ├─ export_schedule_json()
   ├─ schedule_playlist()
   ├─ get_schedules()
   ├─ get_playlists()
   └─ CLI command handlers
```

#### Data Flow: Import Schedule

```
1. User uploads XML file via UI
   ↓
2. Browser sends: POST /api/import-schedule
   ├─ filepath: "/path/to/schedule.xml"
   └─ format: "xml"
   ↓
3. Express spawns: python3 M3U_Matrix_Pro.py --import-schedule-xml <file>
   ↓
4. Python executes:
   ├─ Parse XML file
   ├─ ScheduleValidator.validate_xml_schedule()
   ├─ Extract events
   ├─ DuplicateDetector.detect_duplicates()
   ├─ ConflictDetector.detect_conflicts()
   ├─ Save to schedules/<uuid>.json
   ├─ Update m3u_matrix_settings.json
   └─ Return JSON result
   ↓
5. Express receives output
   ├─ Parse JSON response
   └─ Send back to browser
   ↓
6. Browser displays results
   ├─ Events imported: 48
   ├─ Duplicates removed: 2
   ├─ Conflicts detected: 1
   └─ Show success notification
```

#### Data Flow: Create Schedule

```
1. User inputs: video URLs, start time, duration
   ↓
2. Browser sends: POST /api/schedule-playlist
   ├─ links: [url1, url2, ...]
   ├─ start_time: "2025-11-23T08:00:00Z"
   ├─ duration_hours: 24
   ├─ cooldown_hours: 48
   └─ shuffle: true
   ↓
3. Express spawns: python3 M3U_Matrix_Pro.py --schedule-playlist ...
   ↓
4. Python executes:
   ├─ Load CooldownManager (from cooldown_history.json)
   ├─ Validate inputs
   ├─ ScheduleAlgorithm.schedule_playlist()
   │  ├─ Fisher-Yates shuffle
   │  ├─ Apply 48-hour cooldown
   │  ├─ Fill gaps with repetitions
   │  └─ Return 48 events (24-hour schedule)
   ├─ Update cooldown history
   ├─ Save schedule to file
   └─ Return JSON with event list
   ↓
5. Express receives output
   └─ Send to browser
   ↓
6. Browser displays:
   ├─ Calendar view with scheduled events
   ├─ Coverage percentage (100%)
   └─ Download/export options
```

---

## Data Storage

### Configuration (m3u_matrix_settings.json)
```json
{
  "playlists": [],
  "schedules": [],
  "exports": []
}
```
**Updated by:** API when config changes  
**Size:** Small (KB)

### Schedules (schedules/*.json)
```json
{
  "id": "uuid",
  "name": "My Schedule",
  "source": "xml",
  "filepath": "...",
  "imported": "2025-11-22T23:55:00Z",
  "events": [
    {
      "title": "Video 1",
      "start": "2025-11-22T10:00:00Z",
      "end": "2025-11-22T11:00:00Z"
    }
  ]
}
```
**One file per schedule**  
**Size:** Varies (10KB - 1MB)

### Cooldown History (schedules/cooldown_history.json)
```json
{
  "http://example.com/video1.mp4": "2025-11-22T10:00:00Z",
  "http://example.com/video2.mp4": "2025-11-24T14:30:00Z"
}
```
**Persists across sessions**  
**Updated:** After every schedule operation  
**Size:** Small (KB)

---

## Request/Response Cycle

### Example: Import XML Schedule

**Request:**
```
POST /api/import-schedule
Content-Type: application/json

{
  "filepath": "/schedules/my_schedule.xml",
  "format": "xml"
}
```

**Processing:**
```
Express Handler (api_server.js:169-208)
├─ Validate request
├─ Spawn Python process
├─ Wait for completion
├─ Parse output
└─ Send response

Python Handler (M3U_Matrix_Pro.py:575-655)
├─ Load and parse XML
├─ Validate structure
├─ Extract events
├─ Detect duplicates
├─ Detect conflicts
├─ Save schedule
└─ Return JSON result
```

**Response:**
```json
{
  "status": "success",
  "schedule_id": "abc-123-def",
  "events_imported": 48,
  "duplicates_removed": 2,
  "conflicts_detected": 1,
  "warnings": {
    "duplicates": "2 duplicate events removed",
    "conflicts": "1 overlapping timeslots detected"
  }
}
```

---

## Scalability Analysis

### Current Architecture (MVP)

**Bottlenecks:**
1. **Synchronous I/O** (api_server.js)
   - `fs.readFileSync()`, `fs.writeFileSync()`, `fs.statSync()`
   - Blocks entire server while reading/writing
   - **Impact:** 1-10 concurrent users max

2. **Process Spawning** (api_server.js)
   - New Python process per request
   - Takes ~500ms to spawn
   - Can spawn ~50-100 before out of memory
   - **Impact:** 10-20 concurrent users max

3. **Single-threaded Node.js**
   - Can't use multiple CPU cores
   - One request blocks all others if slow
   - **Impact:** CPU-bound operations slow everything

### For 50-100 Users
**Changes needed:**
1. Convert sync I/O to async (2-3 days)
2. Implement worker process pool (1-2 days)
3. Add in-memory caching (1 day)

### For 100-1000 Users
**Changes needed:**
1. Add PostgreSQL database
2. Add Redis caching
3. Add load balancer (nginx)
4. Implement horizontal scaling
5. Add CDN for static files

---

## Error Handling Architecture

### Python Level
```python
try:
    tree = ET.parse(filepath)
    # ... process ...
except ET.ParseError as e:
    return {"status": "error", "type": "parse_error", "message": str(e)}
except Exception as e:
    return {"status": "error", "type": "unexpected", "message": str(e)}
```

### Express Level
```javascript
try {
    const python = spawn('python3', args);
    python.on('close', (code) => {
        if (code === 0) {
            res.json(result);
        } else {
            res.status(500).json({status: 'error', message: '...'});
        }
    });
} catch (error) {
    res.status(500).json({status: 'error', message: error.message});
}
```

### Browser Level
```javascript
try {
    const response = await fetch('/api/import-schedule', {...});
    const data = await response.json();
    if (data.status === 'success') {
        // Handle success
    } else {
        // Show error toast
        showToast(`Error: ${data.message}`, 'error');
    }
} catch (error) {
    showToast('Network error', 'error');
}
```

---

## Security Considerations

### Current (MVP)
- ❌ No authentication
- ❌ No authorization
- ❌ No rate limiting
- ✅ CORS configured
- ✅ Cache headers set
- ✅ Error messages don't expose internals

### For Production
- [ ] Add API authentication (JWT tokens)
- [ ] Add role-based access control
- [ ] Add rate limiting (100 requests/minute per IP)
- [ ] Add input validation on all endpoints
- [ ] Add HTTPS/SSL
- [ ] Add CSRF protection
- [ ] Add SQL injection protection (when DB added)
- [ ] Add XSS protection (already mitigated by JSON responses)

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | HTML5/CSS/JS | Vanilla | UI/Dashboard |
| API | Express.js | 4.x | REST endpoints |
| Backend | Python | 3.8+ | Scheduling logic |
| Storage | JSON files | N/A | Persistence (MVP) |
| IPC | Child Process | Node.js | Python invocation |

---

## Key Design Decisions

### 1. Python Backend vs Pure Node.js
**Why separate?**
- Scheduling algorithm is complex (cooldown, conflict detection)
- Python is better for data processing
- Easier to test/maintain

**Tradeoff:**
- Process spawning overhead
- Should implement worker pool for scale

### 2. JSON File Storage vs Database
**Why JSON files?**
- No external dependencies
- Easy to understand/debug
- Suitable for MVP

**Tradeoff:**
- No querying capability
- No transaction support
- Doesn't scale past 1000 events

### 3. Single-file Frontend (interactive_hub.html)
**Why monolithic?**
- No build step needed
- Easy to deploy
- Works offline

**Tradeoff:**
- Hard to maintain (36KB single file)
- Should split into components if growing

---

## Future Architecture (Post-MVP)

```
┌─────────────────────────────────────────┐
│         React/Vue SPA Frontend         │
├─────────────────────────────────────────┤
│   nginx (SSL, load balancer, caching)  │
├─────────────────────────────────────────┤
│   Express.js API Server (Async I/O)    │
├─────────────────────────────────────────┤
│   ├─ PostgreSQL (data persistence)     │
│   ├─ Redis (caching layer)             │
│   └─ Python Worker Pool (scheduling)   │
├─────────────────────────────────────────┤
│   Message Queue (RabbitMQ/Redis)       │
└─────────────────────────────────────────┘
```

---

## Testing Architecture

### Unit Tests
- **test_unit.py** - 17 tests (M3UMatrixPro methods)
- **test_cooldown.py** - 29 tests (cooldown edge cases)
- **test_corrupted_input.py** - 20+ tests (error handling)

### Integration Tests
- **test_integration.py** - Test components together

### Stress Tests
- **test_stress.py** - Large data handling

### Load Tests
- **Missing** - Needed for concurrent user validation

---

## Deployment Architecture

### Development
```
Single server (Replit)
├─ Node.js (api_server.js)
└─ Python (M3U_Matrix_Pro.py)
```

### Production (Recommended)
```
Load Balancer (nginx)
├─ App Server 1 (Node.js + Python)
├─ App Server 2 (Node.js + Python)
└─ App Server 3 (Node.js + Python)

Database Layer
├─ PostgreSQL (primary)
└─ PostgreSQL (replica)

Cache Layer
├─ Redis (session/data cache)

File Storage
├─ S3 (schedule exports)
```

---

**Last Updated:** November 22, 2025  
**Status:** Complete  
**Recommendation:** Review before production deployment
