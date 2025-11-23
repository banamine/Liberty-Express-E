# Communication Layer Integration - Implementation Guide

**Date:** November 23, 2025  
**Status:** Ready to implement  
**Scope:** Integrate api_server.js with live M3UMatrixApp instance  
**Estimated Time:** 25-30 hours

---

## Overview: The Fix

### Current (Broken)
```
API Server (Node.js)
    ↓ Spawns new Python process
M3UMatrix (temporary, dies after request)
    ↓ Writes to files
File system
    ↓ Multiple processes fight over files = CORRUPTION
```

### Target (Fixed)
```
API Server (Node.js)
    ↓ Direct method calls
M3UMatrixApp (Python, always running)
    ↓ Writes to files
File system
    ↓ Single writer = NO CORRUPTION
```

---

## Phase 1: Create M3UMatrixApp Orchestrator (Python)

### File: `src/videos/m3u_matrix_app.py`

This is the **main application class** that coordinates all operations.

```python
"""
M3U Matrix App - Production application layer.

This is the single instance that runs throughout the application lifetime.
All operations (API, GUI, headless) go through this instance.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import time

# Import the modules we'll create later
# from m3u_parser import M3UParser
# from channel_manager import ChannelManager
# from validator import ChannelValidator
# from schedule_engine import ScheduleEngine
# from export_manager import ExportManager
# from config_manager import ConfigManager
# from file_handler import FileHandler
# (For now, use existing M3UMatrix methods as fallback)

class M3UMatrixApp:
    """
    Main application orchestrator.
    
    This single instance:
    - Loads on startup (once)
    - Stays alive throughout application lifetime
    - Handles all API requests
    - Handles GUI operations
    - Handles headless operations
    - Manages file system access
    
    No process spawning. One source of truth.
    """
    
    def __init__(self, headless: bool = False):
        """Initialize the app."""
        self.headless = headless
        self.logger = logging.getLogger(__name__)
        
        # State
        self.channels = []
        self.schedule = {}
        self.config = {}
        self.last_save_time = datetime.now()
        
        # For GUI mode
        self.ui = None
        self.root = None
        if not headless:
            try:
                import tkinter as tk
                from tkinterdnd2 import TkinterDnD
                self.root = TkinterDnD.Tk()
                # Note: Don't initialize full GUI yet
                # Will be done by UIController
            except Exception as e:
                self.logger.error(f"Could not initialize Tkinter: {e}")
                self.headless = True
        
        self.logger.info(f"M3UMatrixApp initialized ({'headless' if headless else 'GUI'})")
    
    # ===== FILE OPERATIONS =====
    
    def load_m3u_file(self, filepath: str) -> Dict[str, Any]:
        """Load M3U file and populate channels."""
        try:
            from page_generator import M3UMatrixFileHandler
            handler = M3UMatrixFileHandler()
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse M3U
            channels = self._parse_m3u_content(content)
            self.channels = channels
            
            self.logger.info(f"Loaded {len(channels)} channels from {filepath}")
            return {
                'status': 'success',
                'channels_loaded': len(channels),
                'filepath': filepath
            }
        except Exception as e:
            self.logger.error(f"Failed to load M3U: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def save_json_state(self, filepath: str) -> Dict[str, Any]:
        """Save current state to JSON file (WITH FILE LOCKING)."""
        try:
            # TODO: Add file locking here
            # import fcntl  # Unix
            # or lockfile library
            
            data = {
                'channels': self.channels,
                'schedule': self.schedule,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.last_save_time = datetime.now()
            self.logger.info(f"Saved state to {filepath}")
            return {'status': 'success', 'filepath': filepath}
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # ===== PARSING =====
    
    def _parse_m3u_content(self, content: str) -> List[Dict]:
        """Parse M3U content string and return channels."""
        # Use existing M3UMatrix.parse_m3u_file logic
        # This is a temporary bridge until we modularize
        channels = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Parse channel info
                parts = line.split(',', 1)
                channel = {
                    'name': parts[1] if len(parts) > 1 else 'Unknown',
                    'url': '',  # Will be set on next URL line
                }
                channels.append(channel)
            elif line and not line.startswith('#'):
                if channels:
                    channels[-1]['url'] = line
        
        return channels
    
    # ===== VALIDATION =====
    
    def validate_channels(self, 
                         progress_callback: Optional[callable] = None
                         ) -> Dict[str, Any]:
        """Validate all channels."""
        results = {
            'working': 0,
            'broken': 0,
            'timeout': 0,
            'total': len(self.channels)
        }
        
        for i, channel in enumerate(self.channels):
            if progress_callback:
                progress_callback({
                    'current': i + 1,
                    'total': len(self.channels),
                    'channel': channel.get('name', 'Unknown')
                })
            
            # Use existing validation logic
            status = self._validate_single_channel(channel)
            results[status] += 1
        
        self.logger.info(f"Validation complete: {results}")
        return results
    
    def _validate_single_channel(self, channel: Dict) -> str:
        """Validate single channel URL."""
        import requests
        url = channel.get('url', '')
        
        if not url:
            return 'broken'
        
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            if response.status_code in (200, 206, 403):
                return 'working'
            else:
                return 'broken'
        except requests.exceptions.Timeout:
            return 'timeout'
        except Exception:
            return 'broken'
    
    # ===== SCHEDULING =====
    
    def generate_schedule(self) -> Dict[str, Any]:
        """Generate broadcast schedule."""
        try:
            # Use existing schedule generation logic
            schedule = {
                'generated_at': datetime.now().isoformat(),
                'channels': len(self.channels),
                'status': 'success'
            }
            self.schedule = schedule
            self.logger.info("Schedule generated")
            return schedule
        except Exception as e:
            self.logger.error(f"Schedule generation failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # ===== EXPORT =====
    
    def export_to_json(self, filepath: str) -> Dict[str, Any]:
        """Export schedule to JSON."""
        try:
            data = {
                'channels': self.channels,
                'schedule': self.schedule,
                'exported_at': datetime.now().isoformat()
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Exported to {filepath}")
            return {'status': 'success', 'filepath': filepath}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def export_to_xml(self, filepath: str) -> Dict[str, Any]:
        """Export schedule to XML (TVGuide format)."""
        try:
            # Use existing export logic
            xml_content = self._generate_xml()
            with open(filepath, 'w') as f:
                f.write(xml_content)
            
            self.logger.info(f"Exported to {filepath}")
            return {'status': 'success', 'filepath': filepath}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _generate_xml(self) -> str:
        """Generate XML content (placeholder)."""
        return '<?xml version="1.0"?><schedule></schedule>'
    
    # ===== CHANNEL MANAGEMENT =====
    
    def add_channel(self, channel: Dict) -> Dict[str, Any]:
        """Add a channel."""
        self.channels.append(channel)
        self.logger.info(f"Channel added: {channel.get('name')}")
        return {'status': 'success', 'channel_id': len(self.channels) - 1}
    
    def update_channel(self, channel_id: int, **kwargs) -> Dict[str, Any]:
        """Update a channel."""
        if 0 <= channel_id < len(self.channels):
            self.channels[channel_id].update(kwargs)
            self.logger.info(f"Channel updated: {channel_id}")
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Channel not found'}
    
    def delete_channel(self, channel_id: int) -> Dict[str, Any]:
        """Delete a channel."""
        if 0 <= channel_id < len(self.channels):
            self.channels.pop(channel_id)
            self.logger.info(f"Channel deleted: {channel_id}")
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Channel not found'}
    
    def get_channels(self) -> List[Dict]:
        """Get all channels."""
        return self.channels
    
    # ===== STATUS =====
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status."""
        return {
            'mode': 'headless' if self.headless else 'gui',
            'channels_loaded': len(self.channels),
            'last_save': self.last_save_time.isoformat(),
            'memory_usage': 'TODO: implement',
            'uptime': 'TODO: implement'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }
```

---

## Phase 2: Modify api_server.js to Use M3UMatrixApp

### Key Changes to `api_server.js`

**Before (Current):**
```javascript
// Spawns new Python process for each request
app.post('/api/parse-m3u', (req, res) => {
    const process = spawn('python', ['M3U_MATRIX_PRO.py', '--parse', req.body.file]);
    process.on('close', (code) => {
        res.json(result);
    });
});
```

**After (Fixed):**
```javascript
// Calls live M3UMatrixApp instance
const { PythonShell } = require('python-shell');
let m3uApp = null;

// Initialize M3UMatrixApp once on startup
function initializeApp() {
    PythonShell.run('startup_m3u_app.py', {}, (err) => {
        if (err) throw err;
        m3uApp = require('child_process').spawn('python', [
            'src/videos/m3u_matrix_app_daemon.py'
        ]);
    });
}

// Call it directly
app.post('/api/parse-m3u', async (req, res) => {
    try {
        const result = await callPythonMethod('load_m3u_file', {
            filepath: req.body.file
        });
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Helper to call Python methods via IPC/socket
async function callPythonMethod(method, args) {
    // Use socket or IPC to call M3UMatrixApp methods
    // Returns result
}
```

---

## Phase 3: Start M3UMatrixApp as Daemon

### File: `src/videos/m3u_matrix_app_daemon.py`

```python
"""
M3U Matrix App Daemon

Starts M3UMatrixApp instance that stays alive for the entire application lifetime.
API server calls methods on this instance via socket/IPC.
"""

import socket
import json
import logging
from m3u_matrix_app import M3UMatrixApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create single global instance
app = M3UMatrixApp(headless=True)

# Listen for method calls from API server
def start_socket_server():
    """Start socket server for API to call methods."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 9999))  # Internal IPC port
    server.listen(1)
    
    logger.info("M3UMatrixApp daemon listening on port 9999")
    
    while True:
        client, addr = server.accept()
        handle_request(client)
        client.close()

def handle_request(client):
    """Handle method call request."""
    data = client.recv(4096).decode('utf-8')
    request = json.loads(data)
    
    method = request['method']
    args = request.get('args', {})
    
    # Call method on app instance
    method_func = getattr(app, method, None)
    if method_func:
        try:
            result = method_func(**args)
            response = {'status': 'success', 'result': result}
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
    else:
        response = {'status': 'error', 'message': f'Method not found: {method}'}
    
    client.send(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    start_socket_server()
```

---

## Phase 4: Update api_server.js to Call Daemon

### Changes to `api_server.js`

```javascript
// At top of file
const socket = require('net');
const util = require('util');

// Connection pool to Python daemon
let pythonConnections = [];

function callM3UMethod(method, args = {}) {
    return new Promise((resolve, reject) => {
        const client = socket.createConnection(9999, '127.0.0.1', () => {
            const request = JSON.stringify({ method, args });
            client.write(request);
        });
        
        let response = '';
        client.on('data', (data) => {
            response += data.toString();
        });
        
        client.on('end', () => {
            try {
                const result = JSON.parse(response);
                if (result.status === 'success') {
                    resolve(result.result);
                } else {
                    reject(new Error(result.message));
                }
            } catch (e) {
                reject(e);
            }
            client.destroy();
        });
        
        client.on('error', reject);
    });
}

// Example: Parse M3U endpoint
app.post('/api/parse-m3u', validateAdminKey, async (req, res) => {
    try {
        const result = await callM3UMethod('load_m3u_file', {
            filepath: req.body.filepath
        });
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Example: Get channels
app.get('/api/channels', async (req, res) => {
    try {
        const channels = await callM3UMethod('get_channels');
        res.json({ channels });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Example: Validate channels
app.post('/api/validate', validateAdminKey, async (req, res) => {
    try {
        const results = await callM3UMethod('validate_channels');
        res.json(results);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Example: Export schedule
app.post('/api/export', validateAdminKey, async (req, res) => {
    try {
        const result = await callM3UMethod('export_to_json', {
            filepath: req.body.filepath
        });
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Example: Get status
app.get('/api/status', async (req, res) => {
    try {
        const status = await callM3UMethod('get_status');
        res.json(status);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

---

## Phase 5: Start Daemon on API Server Startup

### Modify `api_server.js` startup:

```javascript
const { spawn } = require('child_process');
const path = require('path');

let pythonDaemon = null;

// Start Python daemon when API server starts
function startPythonDaemon() {
    console.log('Starting M3UMatrixApp daemon...');
    
    pythonDaemon = spawn('python', [
        path.join(__dirname, '..', 'videos', 'm3u_matrix_app_daemon.py')
    ]);
    
    pythonDaemon.stdout.on('data', (data) => {
        console.log(`[Python] ${data}`);
    });
    
    pythonDaemon.stderr.on('data', (data) => {
        console.error(`[Python Error] ${data}`);
    });
    
    pythonDaemon.on('close', (code) => {
        console.error(`Python daemon died with code ${code}`);
        // Auto-restart?
        setTimeout(startPythonDaemon, 5000);
    });
}

// Start daemon before starting API server
startPythonDaemon();

// Wait a moment for daemon to start
setTimeout(() => {
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
        console.log(`API Server listening on port ${PORT}`);
    });
}, 2000);

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down...');
    if (pythonDaemon) {
        pythonDaemon.kill();
    }
    process.exit(0);
});
```

---

## Phase 6: Add File Locking (Safety)

### Modify `m3u_matrix_app.py` save operations:

```python
import fcntl  # Unix file locking

def save_json_state(self, filepath: str) -> Dict[str, Any]:
    """Save state with file locking."""
    try:
        lockfile = filepath + '.lock'
        
        # Acquire lock
        with open(lockfile, 'w') as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)  # Exclusive lock
                
                # Now safe to write
                data = {
                    'channels': self.channels,
                    'schedule': self.schedule,
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)  # Release lock
        
        self.logger.info(f"Saved state to {filepath}")
        return {'status': 'success', 'filepath': filepath}
    except Exception as e:
        self.logger.error(f"Failed to save state: {e}")
        return {'status': 'error', 'message': str(e)}
```

---

## Phase 7: Add Crash Recovery

### Add to `m3u_matrix_app.py`:

```python
def load_with_recovery(self, filepath: str) -> Dict[str, Any]:
    """Load file with crash recovery."""
    backup_file = filepath + '.backup'
    
    try:
        # Check if main file is corrupted
        with open(filepath, 'r') as f:
            json.load(f)  # Will fail if corrupted
        
        # Load normally
        return self.load_m3u_file(filepath)
    
    except json.JSONDecodeError:
        # Main file corrupted, try backup
        self.logger.warning(f"Corrupted file, attempting recovery from {backup_file}")
        
        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)
            self.channels = data.get('channels', [])
            self.logger.info(f"Recovered from backup")
            return {
                'status': 'recovered',
                'message': 'File was corrupted, recovered from backup',
                'channels_loaded': len(self.channels)
            }
        except:
            return {'status': 'error', 'message': 'Both main and backup files corrupted'}

def auto_backup(self):
    """Create backup before each save."""
    backup_file = self.state_file + '.backup'
    
    # Keep previous backup
    if os.path.exists(backup_file):
        os.rename(backup_file, backup_file + '.prev')
    
    # Copy current to backup
    if os.path.exists(self.state_file):
        shutil.copy(self.state_file, backup_file)
```

---

## Implementation Sequence

### Step 1: Create M3UMatrixApp Class
- [ ] Create `src/videos/m3u_matrix_app.py`
- [ ] Implement core methods (load, save, validate, export, etc.)
- [ ] Test: Can import without errors

### Step 2: Create Daemon
- [ ] Create `src/videos/m3u_matrix_app_daemon.py`
- [ ] Implement socket server
- [ ] Test: Python daemon starts and listens on port 9999

### Step 3: Modify API Server
- [ ] Add `callM3UMethod()` helper function
- [ ] Modify endpoints to call daemon instead of spawning process
- [ ] Update startup to start daemon first
- [ ] Test: API calls work without spawning processes

### Step 4: Add File Locking
- [ ] Add fcntl-based file locking
- [ ] Test: Multiple writes don't corrupt data

### Step 5: Add Crash Recovery
- [ ] Implement backup mechanism
- [ ] Add recovery loader
- [ ] Test: Corrupted file recovery works

### Step 6: Test Everything
- [ ] Load M3U file via API
- [ ] Validate channels via API
- [ ] Generate schedule via API
- [ ] Export via API
- [ ] Verify no file corruption under concurrent load

---

## Testing Strategy

### Unit Tests

```python
# tests/test_m3u_app.py
def test_load_m3u():
    app = M3UMatrixApp(headless=True)
    result = app.load_m3u_file('test.m3u')
    assert result['status'] == 'success'

def test_file_locking():
    """Test that concurrent writes don't corrupt data."""
    app1 = M3UMatrixApp()
    app2 = M3UMatrixApp()
    
    app1.channels = [{'name': 'Channel 1', 'url': 'http://...'}]
    app2.channels = [{'name': 'Channel 2', 'url': 'http://...'}]
    
    # Both try to save simultaneously
    app1.save_json_state('test.json')
    app2.save_json_state('test.json')
    
    # Verify file is not corrupted
    with open('test.json') as f:
        data = json.load(f)
    assert data is not None

def test_crash_recovery():
    """Test that corrupted file can be recovered."""
    # Corrupt a file
    with open('test.json', 'w') as f:
        f.write('{ INVALID JSON }')
    
    app = M3UMatrixApp()
    result = app.load_with_recovery('test.json')
    assert result['status'] in ['recovered', 'error']
```

### Integration Tests

```javascript
// tests/test_api_integration.js
async function testLoadM3U() {
    const response = await fetch('/api/parse-m3u', {
        method: 'POST',
        body: JSON.stringify({ filepath: 'test.m3u' }),
        headers: { 'Authorization': 'Bearer ' + ADMIN_KEY }
    });
    
    const result = await response.json();
    assert(result.status === 'success');
    assert(result.channels_loaded > 0);
}

async function testConcurrentRequests() {
    // Send 10 requests simultaneously
    const promises = Array(10).fill(null).map(() =>
        fetch('/api/validate', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer ' + ADMIN_KEY }
        })
    );
    
    const results = await Promise.all(promises);
    
    // All should succeed
    results.forEach(r => {
        assert(r.status === 200);
    });
    
    // Verify file wasn't corrupted
    const statusResponse = await fetch('/api/status');
    const status = await statusResponse.json();
    assert(status.channels_loaded > 0);
}
```

---

## Rollback Plan

If integration breaks:

1. **Keep old API endpoints working** - Don't delete spawning code yet
2. **Add feature flag** - Use environment variable to enable/disable daemon
   ```javascript
   const USE_DAEMON = process.env.USE_DAEMON === 'true';
   
   if (USE_DAEMON) {
       result = await callM3UMethod(...);  // New way
   } else {
       result = await spawnProcess(...);   // Old way
   }
   ```
3. **Easy rollback** - Set `USE_DAEMON=false` in .env if problems

---

## Success Criteria

✅ All these must pass:
- [ ] M3UMatrixApp imports without errors
- [ ] Daemon starts and listens on port 9999
- [ ] API calls return correct results
- [ ] No file corruption under concurrent load
- [ ] Crash recovery works
- [ ] Performance is better (daemon method vs spawning)
- [ ] All existing API endpoints still work
- [ ] GUI mode still works (if headless=false)

---

## Effort Breakdown

| Task | Hours | Notes |
|------|-------|-------|
| Create M3UMatrixApp | 4 | Core orchestrator |
| Create daemon | 3 | Socket server |
| Modify API endpoints | 5 | Convert to call daemon |
| Add file locking | 3 | fcntl integration |
| Add crash recovery | 4 | Backup/restore logic |
| Testing | 6 | Unit + integration |
| Debugging/fixes | 4 | Unexpected issues |
| **Total** | **~29 hours** | 1 week for 1 person |

---

## Next: When Ready

Once this guide is ready, you can:

1. **Implement yourself** - Follow the steps above
2. **Assign to developers** - Share this guide with your team
3. **Outsource** - Use this as specification for contractor

**The guide is complete and implementation-ready.**

