# ScheduleFlow Installation Guide

**Last Updated:** November 22, 2025  
**Status:** Complete, step-by-step instructions for all platforms

---

## Table of Contents
1. [Prerequisites Check](#prerequisites-check)
2. [Installation (Windows/Mac/Linux)](#installation)
3. [Configuration](#configuration)
4. [Starting ScheduleFlow](#starting-scheduleflow)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites Check

### Required (Non-Negotiable)

#### Option A: Quick Check
```bash
# Run this command:
bash check_prerequisites.sh

# Expected output:
# ✅ Node.js v20.19.3
# ✅ Python 3.11.13
# ✅ npm 9+
# ✅ Build tools available
```

#### Option B: Manual Check
```bash
# Check Node.js
node --version
# Expected: v20 or higher

# Check Python
python3 --version
# Expected: 3.11 or higher

# Check npm
npm --version
# Expected: 9 or higher
```

### If Anything is Missing

#### Windows
1. **Node.js:** Download from https://nodejs.org/ (LTS version)
2. **Python:** Download from https://www.python.org/ (3.11+)
3. **Build Tools:** Install Visual C++ Build Tools
   - Download: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"

#### macOS
```bash
# Using Homebrew:
brew install node@20
brew install python@3.11

# Install Xcode command line tools:
xcode-select --install
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager:
sudo apt update

# Install Node.js:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python:
sudo apt-get install python3.11 python3.11-dev

# Install build tools:
sudo apt-get install build-essential
```

---

## Installation

### Step 1: Clone Repository

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/[org]/ScheduleFlow.git
cd ScheduleFlow
```

**Option B: Download ZIP**
1. Visit https://github.com/[org]/ScheduleFlow
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal in the extracted folder

### Step 2: Install Node.js Dependencies

```bash
npm install

# Expected output:
# > added 60 packages
# > up to date, audited 60 packages in X.XXs
```

**If npm fails:**
- See [Troubleshooting: npm install fails](#npm-install-fails)

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt

# Expected output:
# Successfully installed requests-2.31.0, Pillow-10.0.0, ...
```

**If pip fails:**
- See [Troubleshooting: pip install fails](#pip-install-fails)

### Step 4: Verify Installation

```bash
# Run tests to verify everything works:
python3 test_unit.py

# Expected output:
# RESULTS: 18 passed, 0 failed
```

---

## Configuration

### Option A: Using Defaults (Recommended for First-Time)

**ScheduleFlow uses sensible defaults. Nothing required to start.**

Default Configuration:
- **API Port:** 3000
- **Python Path:** `python3`
- **Output Directory:** `./api_output`
- **Max Concurrent Processes:** 4

### Option B: Customize with Environment Variables

```bash
# On Windows (PowerShell):
$env:SCHEDULEFLOW_PORT = 8000
$env:SCHEDULEFLOW_PYTHON = "python"
$env:SCHEDULEFLOW_OUTPUT_DIR = "./custom_output"

# On macOS/Linux:
export SCHEDULEFLOW_PORT=8000
export SCHEDULEFLOW_PYTHON="python"
export SCHEDULEFLOW_OUTPUT_DIR="./custom_output"

# Start server with custom config:
node api_server.js
```

### Option C: Create Configuration File (Advanced)

Create `config.json`:
```json
{
  "api": {
    "port": 3000,
    "host": "0.0.0.0",
    "cors": true
  },
  "python": {
    "executable": "python3",
    "maxConcurrentProcesses": 4,
    "timeout": 30000
  },
  "paths": {
    "output": "./api_output",
    "schedules": "./api_output/schedules",
    "exports": "./api_output/exports"
  }
}
```

Then modify `api_server.js` to load it:
```javascript
const config = require('./config.json');
const PORT = config.api.port;
// ... etc
```

---

## Starting ScheduleFlow

### Option A: Development (Two Terminal Windows)

**Terminal 1: Start API Server**
```bash
node api_server.js

# Expected output:
# Server listening on port 3000
# Press Ctrl+C to stop
```

**Terminal 2: Start Python Engine** (in the same directory)
```bash
python3 -u M3U_Matrix_Pro.py

# Expected output:
# (Process runs silently - it's working if no errors)
# Press Ctrl+C to stop
```

### Option B: Production (Using PM2 Process Manager)

**Install PM2 (global):**
```bash
npm install -g pm2
```

**Create startup config:**
```bash
pm2 start api_server.js --name scheduleflow-api
pm2 start M3U_Matrix_Pro.py --interpreter python3 --name scheduleflow-engine
```

**Check status:**
```bash
pm2 status

# Expected output:
# ┌─────────────────────────┬────┬──────┬──────────┐
# │ Name                    │ id │ mode │ status   │
# ├─────────────────────────┼────┼──────┼──────────┤
# │ scheduleflow-api        │ 0  │ fork │ online   │
# │ scheduleflow-engine     │ 1  │ fork │ online   │
# └─────────────────────────┴────┴──────┴──────────┘
```

**Stop all:**
```bash
pm2 stop all
```

**Start on system boot (Linux/macOS):**
```bash
pm2 startup
pm2 save
```

### Option C: Production (Using Docker)

Create `Dockerfile`:
```dockerfile
FROM node:20

WORKDIR /app

# Install Python
RUN apt-get update && apt-get install -y python3.11 python3-pip

# Copy files
COPY . .

# Install dependencies
RUN npm install
RUN pip install -r requirements.txt

# Expose port
EXPOSE 3000

# Start both services
CMD ["bash", "-c", "node api_server.js & python3 M3U_Matrix_Pro.py"]
```

**Build and run:**
```bash
docker build -t scheduleflow .
docker run -p 3000:3000 scheduleflow
```

---

## Verification

### Check API is Running

```bash
# In a new terminal:
curl http://localhost:3000/api/system-info

# Expected output:
# {
#   "status": "ok",
#   "version": "1.0.0",
#   ...
# }
```

### Check Python Engine

```bash
# Try importing a schedule:
curl -X POST http://localhost:3000/api/import-schedule \
  -H "Content-Type: application/json" \
  -d '{"scheduleXml": "<schedule></schedule>"}'

# Expected: Either success or error message (not connection refused)
```

### Run Complete Test Suite

```bash
python3 test_unit.py

# Expected output:
# RESULTS: 18 passed, 0 failed
```

---

## Troubleshooting

### "node: command not found"

**Problem:** Node.js not installed or not in PATH

**Solution:**
1. Install Node.js: https://nodejs.org/
2. Restart terminal
3. Verify: `node --version`

---

### "python3: command not found"

**Problem:** Python not installed or not in PATH

**Solution:**
1. Install Python 3.11+: https://www.python.org/
2. Restart terminal
3. Verify: `python3 --version`

---

### npm install fails

**Problem:** `gyp ERR! configure error` or similar

**Cause:** Missing C++ build tools

**Solution (Windows):**
1. Install Visual C++ Build Tools
2. Restart terminal
3. Run: `npm install`

**Solution (macOS):**
```bash
xcode-select --install
npm install
```

**Solution (Linux):**
```bash
sudo apt-get install build-essential
npm install
```

---

### pip install fails

**Problem:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solution (Windows):**
1. Install Visual C++ Build Tools: https://visualstudio.microsoft.com/downloads/
2. Restart terminal
3. Run: `pip install -r requirements.txt`

**Solution (macOS/Linux):**
```bash
# macOS:
xcode-select --install

# Linux:
sudo apt-get install python3.11-dev build-essential

# Then:
pip install -r requirements.txt
```

---

### Port 3000 Already in Use

**Problem:** `EADDRINUSE: address already in use :::3000`

**Solution Option 1: Kill existing process**
```bash
# macOS/Linux:
lsof -i :3000
kill -9 <PID>

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Solution Option 2: Use different port**
```bash
# On macOS/Linux:
SCHEDULEFLOW_PORT=3001 node api_server.js

# On Windows:
$env:SCHEDULEFLOW_PORT = 3001
node api_server.js
```

---

### Tests Fail

**Problem:** Some unit tests failing

**Solution:**
```bash
# Re-run tests with verbose output:
python3 test_unit.py

# If specific test fails, check:
# 1. All dependencies installed: pip install -r requirements.txt
# 2. Both Python and Node running
# 3. API server responding: curl http://localhost:3000/api/system-info
```

---

### Performance Issues

**Problem:** API responses slow (>2 seconds)

**Check Queue Status:**
```bash
curl http://localhost:3000/api/queue-stats

# Output shows:
# {
#   "queued": 45,        # High number = queued work
#   "processing": 4,     # Usually 4
#   "avgWaitTime": 1500  # In milliseconds
# }
```

**Solution:**
- This is expected under heavy load (queue managing work)
- Responses will speed up as load decreases
- For production, consider Docker with multiple instances

---

## Getting Help

### Check API Status
```bash
curl http://localhost:3000/api/system-info
```

### Check Queue Stats
```bash
curl http://localhost:3000/api/queue-stats
```

### View API Documentation
```
Open browser: http://localhost:3000/api/docs
```

### Check Server Logs
```bash
# If running in terminal, logs display live
# If using PM2:
pm2 logs scheduleflow-api
```

---

## Next Steps

Once ScheduleFlow is running:

1. **Import a Schedule:**
   - Use the web interface: http://localhost:3000
   - Upload an XML/JSON schedule file

2. **Create a Schedule:**
   - Upload an M3U playlist
   - Define time slots
   - System auto-fills with content

3. **Export for Playout:**
   - Export as XML for CasparCG
   - Export as JSON for custom integration
   - Use `/api/export-schedule-xml` endpoint

---

## Summary

| Step | Time | Status |
|------|------|--------|
| Check prerequisites | 2 min | ✅ |
| Clone repository | 1 min | ✅ |
| Install npm deps | 2 min | ✅ |
| Install Python deps | 3 min | ✅ |
| Configure | 1 min | ✅ |
| Start services | 1 min | ✅ |
| Verify | 2 min | ✅ |
| **Total** | **12 min** | ✅ |

---

**Installation Guide Complete.** If you encounter issues not listed in [Troubleshooting](#troubleshooting), please check the detailed guides or contact support.
