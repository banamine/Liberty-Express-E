# ScheduleFlow Architecture - Wiring Diagram & Hard Questions

**Date:** November 23, 2025  
**Updated:** After code inspection  

---

## ❌ What I Claimed vs ✅ What Actually Exists

### My Original Claim:
> "M3UPro runs in background and pushes functions."

### Hard Questions You Asked:
1. **How?** WebSocket? REST polling? File watching?
2. **Crash safety?** What if the background process dies?

### The Truth:
**There is NO persistent background process.** M3U_Matrix_Pro.py is a **CLI tool**, not a server.

---

## The Real Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser/UI)                        │
│  • Static HTML/JavaScript                                        │
│  • Local storage for client state                                │
│  • REST API calls for backend operations                         │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST
                     │ (5000)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              API SERVER (api_server.js - Node.js)                │
│  • Express server (always running)                               │
│  • Rate limiting (100 req/min)                                   │
│  • Security middleware (auth, file size, XXE)                    │
│  • Request logging                                               │
└────────────────────┬────────────────────────────────────────────┘
                     │ spawn() via
                     │ Task Queue
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         TASK QUEUE (task_queue.js - Node.js)                     │
│  • Max 4 concurrent processes                                    │
│  • Queues requests if limit reached                              │
│  • Timeout: 30 seconds per process                               │
│  • Error handling for crashed processes                          │
└────────────────────┬────────────────────────────────────────────┘
                     │ spawn('python3', args)
                     │ (new process per call)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PYTHON CLI PROCESS (M3U_Matrix_Pro.py - spawned per operation)  │
│  • Short-lived (200ms - 5s typical)                              │
│  • Arguments: --export-schedule-xml, --import, etc.              │
│  • Reads/writes JSON files                                       │
│  • Exits when done (exit code 0 or error)                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              PERSISTENT DATA (Filesystem)                        │
│  • config.json (schedules)                                       │
│  • schedules/cooldown_history.json                               │
│  • logs/scheduleflow.log (error tracking)                        │
│  • generated_pages/ (static exports)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend → API Communication
**Pattern:** REST API calls (no WebSocket, no polling, no file watching)

```javascript
// Example: Import schedule
POST /api/import-schedule
{
  "filepath": "demo_data/sample_schedule.xml",
  "format": "xml"
}
```

**Response:**
```json
{
  "status": "success",
  "schedule_id": "uuid-here",
  "events": 6
}
```

**Failure:**
```json
{
  "status": "error",
  "message": "XML parse error: mismatched tag at line 5",
  "type": "parse_error"
}
```

### 2. API → Task Queue → Python Process Flow

**Step 1:** API receives request
```javascript
// api_server.js line 280
const output = await pythonQueue.execute(args);
```

**Step 2:** Task Queue (max 4 concurrent)
```javascript
// task_queue.js line 34-36
if (this.activeCount < this.maxConcurrency) {
  this._executeTask(task);  // Execute immediately
} else {
  this.queue.push(task);    // Queue if at limit
}
```

**Step 3:** Python process spawned
```javascript
// task_queue.js line 62
const python = spawn('python3', task.args, {
  stdio: ['pipe', 'pipe', 'pipe']
});
```

**Step 4:** Process runs to completion or timeout
```javascript
// task_queue.js line 81-87
const timeoutHandle = setTimeout(() => {
  if (!completed) {
    completed = true;
    python.kill();  // Kill if exceeds 30 seconds
    this._taskComplete(task, new Error('Process timeout'), null);
  }
}, task.timeout);
```

**Step 5:** Receive output/error
```javascript
// task_queue.js line 90-102
python.on('close', (code) => {
  if (code === 0) {
    this._taskComplete(task, null, output.trim());  // Success
  } else {
    this._taskComplete(task, error, null);  // Error
  }
});
```

### 3. M3U_Matrix_Pro.py CLI Arguments

**Example Operations:**
```bash
# List all schedules
python3 M3U_Matrix_Pro.py --list-schedules

# Export schedule to XML
python3 M3U_Matrix_Pro.py --export-schedule-xml abc123 output.xml

# Import schedule
python3 M3U_Matrix_Pro.py --import-schedule /path/to/file.xml

# Delete schedule
python3 M3U_Matrix_Pro.py --delete-schedule abc123
```

**Each command:**
- Runs in isolation (no shared state with other processes)
- Reads/writes JSON files
- Logs to `logs/scheduleflow.log`
- Exits with code 0 (success) or non-zero (error)
- Duration: 200ms - 5 seconds typical

---

## Hard Question #1: How Does Communication Work?

### Your Question:
> How? (WebSocket, REST polling, file watching?)

### The Answer:
**Simple REST API - no fancy mechanisms needed.**

```
User Action → Browser → POST /api/operation → Task Queue → Python CLI → Response
```

Each API call is **synchronous** (waits for Python process to finish):
- Browser sends request
- Task Queue spawns Python process
- API waits for process to complete (or timeout at 30s)
- Response sent back to browser
- Python process cleaned up

**Why not WebSocket?** Because operations complete quickly (< 5 seconds), synchronous REST is simpler and more reliable.

---

## Hard Question #2: Process Crash Safety - "No Heartbeat = Dead System?"

### Your Question:
> What if the background process crashes? No heartbeat = dead system?

### The Answer:
**There IS NO background M3U process to crash.** Each operation is separate.

#### Scenario 1: Python Process Crashes
```
Task Queue spawns Python process
↓
Python process crashes (exit code 1)
↓
Task Queue catches: code !== 0
↓
Error returned to API client: "Operation failed: [error details]"
↓
API server still running, accepts next request
```

**Result:** Single operation fails, system stays up.

#### Scenario 2: API Server Crashes
```
User makes request
↓
API server crashes
↓
Browser gets connection error
↓
User clicks retry or refreshes
↓
API server restart (automatic in Replit)
↓
System recovers
```

**Heartbeat mechanism:** The API server itself IS the heartbeat. While it's running, system is healthy.

#### Scenario 3: Process Timeout (30 seconds exceeded)
```
Python process hangs (infinite loop, deadlock, etc.)
↓
Task Queue timeout fires
↓
Task Queue kills process: python.kill()
↓
Error returned: "Process timeout after 30 seconds"
↓
API server releases resources, accepts next request
```

**Protection:** Timeout prevents zombie processes from accumulating.

---

## Process Pool Protection

**Why max 4 concurrent processes?**

```javascript
const pythonQueue = new TaskQueue(4);  // Limited concurrency
```

**Without limit:**
- Request 100 imports → spawn 100 Python processes
- Each process uses ~30MB RAM
- 100 × 30MB = 3GB needed
- System runs out of memory (OOM)
- Everything crashes

**With limit (4 max):**
- Request 100 imports → queue them
- Run 4 at a time (max ~120MB RAM)
- As one finishes, next in queue runs
- System stays stable

**Monitor via:**
```bash
# In Task Queue
pythonQueue.getStats()
{
  "activeProcesses": 2,
  "queuedTasks": 5,
  "maxConcurrency": 4,
  "utilizationPercent": 50
}
```

---

## Failure Modes & Recovery

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| **Python process crashes** | Exit code ≠ 0 | Error returned to user, API continues |
| **Process hangs 30s** | Timeout fires | Process killed, error returned to user, API continues |
| **File corrupted** | JSON parse error in Python | Error logged, backup created (*.corrupt), API continues |
| **API server crashes** | Browser connection error | Auto-restart in Replit, user retries |
| **Out of memory** | Shouldn't happen (pool limits) | Process killed by OS, Task Queue handles gracefully |
| **Database lock** | File lock during save | Retry logic in Python, error logged |

---

## Logging & Debugging

### API Request Logging
```
[INFO] POST /api/import-schedule - 200 (1245ms)
[ERROR] POST /api/import-schedule - 400 (50ms)
```

### Python Process Logging
```
2025-11-23 01:57:00,176 - INFO - Successfully imported XML schedule: abc123 (6 events)
2025-11-23 01:57:01,390 - ERROR - Failed to export schedule: Permission denied
2025-11-23 01:57:02,172 - WARNING - Skipping malformed timestamp for 'test.mp4'
```

### Monitor Both
```bash
# All logs
tail -f logs/scheduleflow.log

# Errors only
grep ERROR logs/scheduleflow.log

# Real-time API errors
tail -f logs/scheduleflow.log | grep "ERROR\|timeout"
```

---

## Production Readiness Assessment

### Strengths
✅ **Simple architecture** - REST API + CLI is proven model  
✅ **Process pooling** - Memory protected (max 4 concurrent)  
✅ **Error isolation** - Single operation failure doesn't cascade  
✅ **Timeout protection** - Hanging processes killed after 30s  
✅ **Comprehensive logging** - All errors visible  
✅ **No persistent daemon** - Simpler to manage, fewer failure modes  

### Weaknesses / Phase 2 Improvements
⚠️ **No request ID tracking** - Hard to correlate errors with specific users (add in Phase 2)  
⚠️ **No process restart policy** - If API server dies, relies on Replit auto-restart (acceptable for Phase 1)  
⚠️ **No health check endpoint** - Can't easily monitor system status (add: GET /api/health)  
⚠️ **Queue statistics not exposed** - Can't see how many tasks are queued (add: GET /api/queue-stats)  

---

## Comparison: Architecture Models

### Current Model: CLI Per Operation (ScheduleFlow)
```
REST API → spawn Python CLI → output → response
```
✅ Pros: Simple, stateless, proven, easy to scale  
✅ Each operation isolated  
✓ Memory efficient (processes exit)  
❌ Cons: Process startup overhead (~100ms per operation)  

### Alternative Model: Background Service (NOT used)
```
Control Panel ↔ M3U Background Service (WebSocket)
                    ↓
              Persistent Process
```
❌ Pros: No spawn overhead  
❌ Cons: State management complexity, crash recovery harder, must implement heartbeat  

### Alternative Model: File Watching (NOT used)
```
Control Panel → writes file → Background process watches → reads file
```
❌ Race conditions  
❌ Hard to guarantee ordering  
❌ Polling overhead  

**Chosen model is correct for this project.**

---

## Conclusion: Hard Questions Answered

### Q1: How does Control Panel connect to M3UPro?
**A:** REST API calls. No background process pushing functions. Browser → Express API → Task Queue → spawn Python CLI per operation.

### Q2: What if the background process crashes?
**A:** There is NO persistent background process. Each operation is isolated. If Python crashes, error returned to user. If API server crashes, Replit auto-restarts.

### Q3: No heartbeat = dead system?
**A:** The API server IS the heartbeat. Pool limits (max 4) prevent OOM. Timeouts (30s) kill hanging processes. Error logging shows all problems.

---

## Honest Assessment: Production Ready?

**For Phase 1:** Yes, architecture is sound.
- Simple and proven
- Process isolation prevents cascades
- Pool limits prevent OOM
- Logging visible

**For Phase 2:** Add these:
- Health check endpoint (GET /api/health)
- Queue statistics endpoint
- Request ID tracking
- Process restart/recovery policy
- Structured logging (JSON instead of text)

