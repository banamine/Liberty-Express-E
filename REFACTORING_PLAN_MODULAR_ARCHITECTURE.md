# Refactoring Plan: Modular Architecture for M3U_MATRIX_PRO.py

**Date:** November 23, 2025  
**Status:** Plan document (not yet implemented)  
**Scope:** Break monolithic 212-method class into 8 independent modules  
**Effort:** ~40-60 hours development + testing

---

## Executive Summary

### Current State (Monolithic)
```
M3UMatrix (1 class, 212 methods, 7,270 lines)
├─ UI logic (build_ui, fill, etc.)
├─ M3U parsing (parse_m3u_file, build_m3u)
├─ Validation (validate_channel, start_check)
├─ Data management (load_m3u, save_json)
├─ Scheduling (generate_schedule)
├─ Export (export_to_xml, export_to_json)
└─ Configuration (load_settings, save_settings)
    ↑ ALL TIGHTLY COUPLED
```

### Target State (Modular)
```
8 Independent Modules
├─ m3u_parser.py (M3UParser class - 25 methods)
├─ channel_manager.py (ChannelManager class - 30 methods)
├─ validator.py (ChannelValidator class - 15 methods)
├─ schedule_engine.py (ScheduleEngine class - 20 methods)
├─ export_manager.py (ExportManager class - 15 methods)
├─ config_manager.py (ConfigManager class - 12 methods)
├─ file_handler.py (FileHandler class - 18 methods)
└─ ui_controller.py (UIController class - 60 methods)

+ m3u_matrix_app.py (Main orchestrator, 12 methods)
```

**Benefits:**
- ✅ Independent testing (no GUI dependency)
- ✅ Reusable components (API, CLI, GUI)
- ✅ Clear responsibilities
- ✅ Easier debugging
- ✅ Better maintainability

---

## Phase 1: Extract 8 Core Modules

### Module 1: M3UParser
**File:** `src/videos/m3u_parser.py`

**Responsibility:** Parse and build M3U files (no UI, no data persistence)

**Classes:**
```python
class M3UParser:
    """M3U file parsing and generation."""
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse M3U file and return list of channels."""
        # From: parse_m3u_file()
        
    def parse_string(self, content: str) -> List[Dict]:
        """Parse M3U content string."""
        # Helper method
        
    def build_m3u(self, channels: List[Dict]) -> str:
        """Generate M3U content from channels."""
        # From: build_m3u()
        
    def validate_syntax(self, content: str) -> bool:
        """Validate M3U syntax."""
        # New validation
```

**Methods to move (from M3UMatrix):**
- `parse_m3u_file()` → `parse_file()`
- `build_m3u()` → `build_m3u()`
- Regex patterns and helpers
- EXTGRP parsing logic
- Custom tag handling

**Dependencies:**
- None (pure data processing)

**Type Hints Required:**
```python
def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
    """Parse M3U file.
    
    Args:
        file_path: Path to .m3u file
        
    Returns:
        List of channel dictionaries with keys:
        - num: Channel number
        - name: Display name
        - url: Stream URL
        - logo: Channel logo URL
        - group: Category
        - etc.
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If M3U syntax invalid
    """
```

---

### Module 2: ChannelManager
**File:** `src/videos/channel_manager.py`

**Responsibility:** Manage channel data (add, edit, delete, reorder)

**Classes:**
```python
class Channel:
    """Represents a single channel."""
    num: int
    name: str
    url: str
    group: str
    logo: Optional[str]
    uuid: str
    # ... other fields

class ChannelManager:
    """Manage channel collection."""
    
    def add_channel(self, channel: Channel) -> str:
        """Add channel, return UUID."""
        
    def update_channel(self, uuid: str, **kwargs) -> bool:
        """Update channel by UUID."""
        
    def delete_channel(self, uuid: str) -> bool:
        """Delete channel by UUID."""
        
    def get_all(self) -> List[Channel]:
        """Get all channels."""
        
    def reorder(self, channel_uuids: List[str]) -> bool:
        """Reorder channels by UUID list."""
        
    def search(self, query: str) -> List[Channel]:
        """Search channels by name/group."""
```

**Methods to move (from M3UMatrix):**
- `add_channel()`
- `delete_channel()`
- `update_channel()`
- `reorder_channels()`
- `get_channel_by_num()`
- UUID handling logic
- Channel validation logic

**Dependencies:**
- None (pure data structure)

---

### Module 3: ChannelValidator
**File:** `src/videos/validator.py`

**Responsibility:** Validate channel accessibility (no UI, no file I/O)

**Classes:**
```python
class ValidationResult:
    """Result of validation."""
    status: str  # 'working', 'broken', 'timeout'
    message: str
    timestamp: datetime
    response_time: float

class ChannelValidator:
    """Validate channel URLs."""
    
    def validate(self, url: str, timeout: int = 5) -> ValidationResult:
        """Validate single URL."""
        
    def validate_batch(self, 
                      urls: List[str], 
                      callback: Optional[Callable] = None
                      ) -> List[ValidationResult]:
        """Validate multiple URLs with progress callback."""
        
    def validate_http(self, url: str, timeout: int) -> ValidationResult:
        """Validate HTTP/HTTPS stream."""
        
    def validate_rtmp(self, url: str, timeout: int) -> ValidationResult:
        """Validate RTMP stream."""
        
    def validate_hls(self, url: str) -> ValidationResult:
        """Validate HLS playlist."""
```

**Methods to move (from M3UMatrix):**
- `validate_channel()` → `validate()`
- `validate_stream_protocol()`
- HTTP validation logic
- RTMP validation logic
- HLS validation logic

**Dependencies:**
- requests library

**Type Hints Example:**
```python
def validate(self, url: str, timeout: int = 5) -> ValidationResult:
    """Validate channel URL accessibility.
    
    Args:
        url: Stream URL (http, rtmp, rtsp, hls)
        timeout: Request timeout in seconds
        
    Returns:
        ValidationResult with status, message, response time
        
    Raises:
        ValueError: If URL format invalid
        TimeoutError: If request exceeds timeout
    """
```

---

### Module 4: ScheduleEngine
**File:** `src/videos/schedule_engine.py`

**Responsibility:** Generate broadcast schedules

**Classes:**
```python
class Schedule:
    """Broadcast schedule."""
    channels: Dict[str, List[ScheduleEntry]]
    start_time: datetime
    duration: timedelta
    
class ScheduleEntry:
    """Single schedule entry."""
    channel_id: str
    time: datetime
    video_url: str
    duration: timedelta

class ScheduleEngine:
    """Generate and manage schedules."""
    
    def generate(self, 
                channels: List[Channel],
                config: Dict
                ) -> Schedule:
        """Generate schedule from channels."""
        
    def add_recurring(self, rule: str, channels: List[Channel]):
        """Add recurring schedule entries."""
        
    def apply_cooldown(self, schedule: Schedule, cooldown_hours: int):
        """Apply 48-hour cooldown between identical videos."""
        
    def validate_schedule(self, schedule: Schedule) -> List[str]:
        """Validate schedule for conflicts."""
```

**Methods to move (from M3UMatrix):**
- `generate_schedule()`
- Cooldown logic
- Recurring event logic
- Conflict detection
- Category balancing

**Dependencies:**
- datetime library

---

### Module 5: ExportManager
**File:** `src/videos/export_manager.py`

**Responsibility:** Export schedules to various formats

**Classes:**
```python
class ExportManager:
    """Export schedule to multiple formats."""
    
    def to_xml(self, schedule: Schedule, output_path: str):
        """Export to XML (TVGuide format)."""
        
    def to_json(self, schedule: Schedule, output_path: str):
        """Export to JSON."""
        
    def to_m3u(self, channels: List[Channel], output_path: str):
        """Export to M3U playlist."""
        
    def to_casparcg(self, schedule: Schedule) -> str:
        """Export to CasparCG format."""
        
    def to_obs(self, schedule: Schedule) -> Dict:
        """Export to OBS config format."""
        
    def to_vmix(self, schedule: Schedule) -> str:
        """Export to vMix format."""
```

**Methods to move (from M3UMatrix):**
- `export_to_xml()` → `to_xml()`
- `export_to_json()` → `to_json()`
- `export_to_m3u()` → `to_m3u()`
- Playout engine exports
- Format validation

**Dependencies:**
- xml.etree.ElementTree
- json library
- pathlib

---

### Module 6: ConfigManager
**File:** `src/videos/config_manager.py`

**Responsibility:** Manage application settings and configuration

**Classes:**
```python
class Config:
    """Application configuration."""
    output_dir: str
    theme: str
    default_timeout: int
    cooldown_hours: int
    # ... other settings

class ConfigManager:
    """Manage application settings."""
    
    def load(self) -> Config:
        """Load settings from file."""
        
    def save(self, config: Config):
        """Save settings to file."""
        
    def reset_defaults(self):
        """Reset to default settings."""
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get single setting."""
        
    def set(self, key: str, value: Any):
        """Set single setting."""
        
    def validate(self) -> List[str]:
        """Validate all settings, return errors."""
```

**Methods to move (from M3UMatrix):**
- `load_settings()` → `load()`
- `save_settings()` → `save()`
- Settings validation
- Settings initialization
- Default values

**Dependencies:**
- json library
- pathlib

---

### Module 7: FileHandler
**File:** `src/videos/file_handler.py`

**Responsibility:** File system operations (load, save, import, export)

**Classes:**
```python
class FileHandler:
    """Handle file operations."""
    
    def load_m3u(self, path: str) -> List[Dict]:
        """Load M3U file."""
        
    def save_m3u(self, path: str, content: str):
        """Save M3U file."""
        
    def load_json(self, path: str) -> Dict:
        """Load JSON file."""
        
    def save_json(self, path: str, data: Dict):
        """Save JSON file."""
        
    def import_files(self, paths: List[str]) -> List[Dict]:
        """Import multiple files (folder scan)."""
        
    def create_backup(self, output_dir: str) -> str:
        """Create backup of all files."""
        
    def ensure_output_dir(self, path: str):
        """Ensure output directory exists."""
```

**Methods to move (from M3UMatrix):**
- `load()` → `load_m3u()`
- `save_json()`
- File import logic
- Folder scanning
- Backup creation
- Directory management

**Dependencies:**
- pathlib
- json library
- os library

---

### Module 8: UIController
**File:** `src/videos/ui_controller.py`

**Responsibility:** All Tkinter UI logic (ONLY UI, NO BUSINESS LOGIC)

**Classes:**
```python
class UIController:
    """Manage Tkinter GUI."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
    def build_ui(self):
        """Create all UI elements."""
        
    def fill_channel_list(self, channels: List[Channel]):
        """Populate channel treeview."""
        
    def update_status(self, message: str):
        """Update status bar."""
        
    def show_error(self, title: str, message: str):
        """Show error dialog."""
        
    def show_progress(self, title: str, max_value: int) -> ProgressDialog:
        """Show progress dialog."""
        
    def ask_for_file(self, file_types: List[str]) -> Optional[str]:
        """Ask user to select file."""
        
    # 60+ more UI methods
```

**Important:** This class should ONLY:
- ✅ Create UI elements
- ✅ Handle clicks/input
- ✅ Display data
- ❌ Never do business logic
- ❌ Never parse M3U
- ❌ Never validate streams
- ❌ Never access file system directly

**Example of CORRECT vs WRONG:**

```python
# WRONG - UI doing business logic
def on_validate_click(self):
    for channel in self.channels:  # ← Business logic!
        status = self.validate_channel(channel)  # ← UI doing validation!
        self.tv.item(...).update(...)

# CORRECT - UI calling business logic
def on_validate_click(self):
    channels = self.app.channel_manager.get_all()
    results = self.app.validator.validate_batch(
        [ch.url for ch in channels],
        callback=self.update_progress
    )
    for result in results:
        self.update_channel_status(result)
```

**Methods to move (from M3UMatrix):**
- `build_ui()` and all UI-related
- `fill()` → `fill_channel_list()`
- `show_error_dialog()`
- `create_progress_dialog()`
- Dialog creation
- Button/menu setup
- Treeview manipulation

**Dependencies:**
- tkinter
- tkinterdnd2

---

## Phase 2: Main Orchestrator Class

### Module 9: M3UMatrixApp
**File:** `src/videos/m3u_matrix_app.py`

**Responsibility:** Coordinate all modules (facade pattern)

**Classes:**
```python
class M3UMatrixApp:
    """Main application - coordinates all modules."""
    
    def __init__(self, headless: bool = False):
        # Initialize all modules
        self.parser = M3UParser()
        self.channel_manager = ChannelManager()
        self.validator = ChannelValidator()
        self.scheduler = ScheduleEngine()
        self.exporter = ExportManager()
        self.config_manager = ConfigManager()
        self.file_handler = FileHandler()
        
        if not headless:
            self.ui = UIController(tk.Tk())
        
    def load_m3u_file(self, path: str):
        """Workflow: Load M3U file."""
        # 1. Use file_handler to load
        content = self.file_handler.load_m3u(path)
        # 2. Use parser to parse
        channels = self.parser.parse_string(content)
        # 3. Use channel_manager to store
        for ch in channels:
            self.channel_manager.add_channel(ch)
        # 4. Update UI (if not headless)
        if hasattr(self, 'ui'):
            self.ui.fill_channel_list(channels)
    
    def validate_channels(self, callback=None):
        """Workflow: Validate all channels."""
        channels = self.channel_manager.get_all()
        urls = [ch.url for ch in channels]
        results = self.validator.validate_batch(urls, callback)
        return results
    
    def generate_schedule(self):
        """Workflow: Generate schedule."""
        channels = self.channel_manager.get_all()
        config = self.config_manager.load()
        schedule = self.scheduler.generate(channels, config.to_dict())
        return schedule
    
    def export_schedule(self, format: str, output_path: str):
        """Workflow: Export schedule."""
        schedule = self.generate_schedule()
        if format == 'xml':
            self.exporter.to_xml(schedule, output_path)
        elif format == 'json':
            self.exporter.to_json(schedule, output_path)
        # etc.
    
    def run_gui(self):
        """Run GUI mode."""
        self.ui.build_ui()
        self.root.mainloop()
    
    def run_headless(self):
        """Run daemon mode (listens for API)."""
        # Stays alive for API calls
        while True:
            time.sleep(1)
```

---

## Phase 3: Dependency Diagram

### Current State (Monolithic Chaos)
```
M3UMatrix
├─ self.root (Tkinter window)
├─ self.channels (data)
├─ self.tv (UI widget)
├─ self.stat (UI widget)
├─ ... 26 more instance variables
└─ 212 methods all referencing each other
```

### Target State (Clean Dependencies)
```
M3UMatrixApp (Orchestrator)
├─ M3UParser (pure data)
├─ ChannelManager (data structure)
├─ ChannelValidator (HTTP requests, no UI)
├─ ScheduleEngine (algorithm, no UI)
├─ ExportManager (file writing, no UI)
├─ ConfigManager (settings, no UI)
├─ FileHandler (file I/O, no UI)
└─ UIController (UI only, calls back to app)
    └─ Tkinter (UI library)
```

**Key principle:** Business logic layers don't know about UI.

```
UI Layer (UIController)
    ↓ callbacks
App Layer (M3UMatrixApp)
    ↓ method calls
Data/Logic Layers (Parser, Validator, etc.)
```

---

## Step-by-Step Refactoring Sequence

### Step 1: Extract M3UParser
1. Create `src/videos/m3u_parser.py`
2. Copy all M3U parsing methods
3. Add type hints
4. Add comprehensive docstrings
5. Test in isolation (no UI)
6. Replace calls in M3UMatrix: `self.parse_m3u_file()` → `parser.parse_file()`

### Step 2: Extract ChannelManager
1. Create `src/videos/channel_manager.py`
2. Create Channel dataclass
3. Move channel management methods
4. Replace calls: `self.channels` → `channel_manager.get_all()`

### Step 3: Extract ChannelValidator
1. Create `src/videos/validator.py`
2. Move validation methods
3. Remove UI dialogs from validation
4. Keep validation pure (no side effects)
5. Use callbacks for progress

### Step 4: Extract ScheduleEngine
1. Create `src/videos/schedule_engine.py`
2. Move schedule generation
3. Move cooldown logic
4. Move recurring event logic

### Step 5: Extract ExportManager
1. Create `src/videos/export_manager.py`
2. Move all export methods
3. No UI in export (no progress dialogs)

### Step 6: Extract ConfigManager
1. Create `src/videos/config_manager.py`
2. Move settings management
3. Settings files stay in M3U_Matrix_Output/

### Step 7: Extract FileHandler
1. Create `src/videos/file_handler.py`
2. Move file I/O
3. Folder operations
4. Backup creation

### Step 8: Extract UIController
1. Create `src/videos/ui_controller.py`
2. Move all Tkinter code
3. UI methods only (no business logic)
4. Accept callbacks from M3UMatrixApp

### Step 9: Create M3UMatrixApp Orchestrator
1. Create `src/videos/m3u_matrix_app.py`
2. Instantiate all 8 modules
3. Implement workflows
4. Handle both headless and GUI modes

### Step 10: Refactor Old M3UMatrix
1. Keep original as-is for now (for reference)
2. Rename to `M3UMatrix_OLD.py`
3. Create new minimal wrapper that uses modules

### Step 11: Testing
1. Test each module independently
2. Test workflows (load → validate → export)
3. Test GUI with new architecture
4. Test headless mode with new architecture

### Step 12: Cleanup
1. Delete `M3UMatrix_OLD.py`
2. Update imports in `api_server.js`
3. Update imports in other files
4. Update documentation

---

## Type Hints Checklist

For each module, add these type hints:

```python
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Example for M3UParser
def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
    """Parse M3U file."""
    
def build_m3u(self, channels: List[Dict]) -> str:
    """Generate M3U content."""

# Example for ChannelValidator
def validate(self, url: str, timeout: int = 5) -> 'ValidationResult':
    """Validate URL."""
    
def validate_batch(self, 
                  urls: List[str], 
                  callback: Optional[Callable[[int, str], None]] = None
                  ) -> List['ValidationResult']:
    """Validate multiple URLs."""
```

---

## Documentation Template

For each module, add these docstrings:

```python
"""
Module: m3u_parser
==================
Responsibility: Parse M3U files and generate M3U content.
Dependencies: None (pure data processing)
Used by: M3UMatrixApp, FileHandler
API: M3UParser class with parse_file(), build_m3u() methods

Examples:
    parser = M3UParser()
    channels = parser.parse_file('playlist.m3u')
    content = parser.build_m3u(channels)
"""

class M3UParser:
    """M3U file parser and generator.
    
    Handles parsing M3U playlist files with support for:
    - Standard M3U/M3U8 format
    - EXTGRP group tags
    - Custom metadata
    - HLS playlists
    
    Example:
        parser = M3UParser()
        channels = parser.parse_file('live.m3u')
    """
```

---

## Architecture Diagram (Text)

```
┌─────────────────────────────────────────────────────────────┐
│                    M3UMatrixApp                              │
│            (Orchestrator/Facade Pattern)                     │
└─────────────────────────────────────────────────────────────┘
    ↓              ↓              ↓              ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Parser   │ │ Channel  │ │Validator │ │ Schedule │
│          │ │ Manager  │ │          │ │ Engine   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
    ↓              ↓              ↓              ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Config   │ │ Export   │ │ File     │ │ UI       │
│ Manager  │ │ Manager  │ │ Handler  │ │ Controller
└──────────┘ └──────────┘ └──────────┘ └──────────┘
                                           ↓
                                      ┌──────────┐
                                      │ Tkinter  │
                                      └──────────┘
```

---

## Testing Strategy

### Unit Tests (Each Module)

```python
# tests/test_m3u_parser.py
def test_parse_m3u_file():
    parser = M3UParser()
    channels = parser.parse_file('sample.m3u')
    assert len(channels) > 0
    assert 'name' in channels[0]

def test_parse_invalid_file():
    parser = M3UParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_file('nonexistent.m3u')

# tests/test_validator.py
def test_validate_http():
    validator = ChannelValidator()
    result = validator.validate('http://example.com/video.mp4')
    assert result.status in ['working', 'broken', 'timeout']
```

### Integration Tests (Workflows)

```python
def test_load_validate_export():
    app = M3UMatrixApp(headless=True)
    
    # Load
    app.load_m3u_file('test.m3u')
    channels = app.channel_manager.get_all()
    assert len(channels) > 0
    
    # Validate
    results = app.validate_channels()
    assert len(results) == len(channels)
    
    # Export
    app.export_schedule('json', 'output.json')
    assert os.path.exists('output.json')
```

### GUI Tests (Headless)

```python
def test_gui_load():
    app = M3UMatrixApp(headless=False)
    app.ui.ask_for_file = mock_file_dialog  # Mock file picker
    app.ui.on_load_click()
    # Verify channels appear in treeview
```

---

## Migration Checklist

- [ ] Create 8 module files
- [ ] Move methods to appropriate modules
- [ ] Add type hints to all methods
- [ ] Add comprehensive docstrings
- [ ] Add module-level documentation
- [ ] Create M3UMatrixApp orchestrator
- [ ] Update imports in api_server.js
- [ ] Update imports in other files
- [ ] Write unit tests for each module
- [ ] Write integration tests for workflows
- [ ] Test GUI with new architecture
- [ ] Test headless with new architecture
- [ ] Create module dependency docs
- [ ] Update main documentation
- [ ] Delete old monolithic class
- [ ] Verify CI/CD passes
- [ ] Test on production-like environment

---

## Effort Estimation

| Task | Hours | Notes |
|------|-------|-------|
| Create 8 module files | 2 | Copy/paste methods |
| Add type hints | 8 | ~25 hours ÷ 212 methods |
| Add docstrings | 8 | ~40 missing docstrings |
| Refactor UIController | 8 | Remove business logic |
| Create M3UMatrixApp | 4 | Orchestrator logic |
| Unit tests | 10 | Test each module |
| Integration tests | 6 | Test workflows |
| Debugging/fixes | 8 | Unexpected issues |
| Documentation | 4 | Update all docs |
| **Total** | **~48 hours** | ~1 week for 1 developer |

---

## Success Criteria

After refactoring:
- ✅ 8 independent modules with clear responsibilities
- ✅ 100% docstring coverage (212/212 methods)
- ✅ 100% type hints on all methods
- ✅ Each module testable in isolation
- ✅ No business logic in UIController
- ✅ All existing functionality preserved
- ✅ Unit test coverage >80%
- ✅ API and headless modes working
- ✅ GUI mode working identically to before

---

## Risk Mitigation

**Risk:** Breaking existing functionality  
**Mitigation:** Keep original code, test thoroughly before deletion

**Risk:** Circular dependencies  
**Mitigation:** Use dependency diagram, test imports

**Risk:** Performance regression  
**Mitigation:** Profile before/after, benchmark key operations

**Risk:** Incomplete type hints  
**Mitigation:** Use type checker (mypy) to verify all methods

---

## Next Steps

1. Review this plan with team
2. Assign modules to developers (1-2 modules each)
3. Set up testing framework
4. Start with Phase 1, Step 1 (M3UParser)
5. Test each module before moving to next
6. Integrate gradually
7. Deploy when all phases complete

---

## References

- **Monolithic code:** Current `M3UMatrix` class (212 methods)
- **Target:** Clean architecture with separation of concerns
- **Pattern:** Facade pattern (M3UMatrixApp coordinates modules)
- **Testing:** Each module independently testable

**Good luck with the refactoring!**

