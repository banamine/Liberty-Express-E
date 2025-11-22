# M3U Matrix Pro - Directory Structure Documentation

## 📁 Reorganized Project Structure (November 19, 2025)

```
M3U_Matrix_Pro/
│
├── 📱 Applications/               # Main Python Applications
│   ├── M3U_MATRIX_PRO.py         # IPTV Playlist Manager
│   └── VIDEO_PLAYER_PRO.py       # Media Player Workbench
│
├── 🔧 Core_Modules/               # All Core Logic & Modules
│   ├── page_generator.py         # Page generation engine
│   ├── output_manager.py         # File/directory management
│   ├── ndi_output.py            # NDI broadcast support
│   ├── m3u_validation.py        # M3U parsing & validation
│   ├── redis_exporter.py        # Redis export functionality
│   ├── redis_api_server.py      # Redis API server
│   ├── rumble_helper.py         # Rumble integration
│   ├── rumble_category_browser.py # Rumble browser UI
│   ├── dashboard.py             # Dashboard components
│   └── patch_m3u_matrix.py      # Patch utilities
│
├── 📜 scripts/                    # Launch Scripts & Utilities
│   ├── LAUNCH_M3U_MATRIX_PRO.bat    # Windows launcher (M3U)
│   ├── launch_m3u_matrix_pro.sh     # Linux/Mac launcher (M3U)
│   ├── LAUNCH_VIDEO_PLAYER_PRO.bat  # Windows launcher (Video)
│   ├── launch_video_player_pro.sh   # Linux/Mac launcher (Video)
│   ├── run_m3u_matrix.sh           # Run script
│   ├── create_portable_distribution.bat # Distribution builder
│   ├── package_for_distribution.bat    # Package builder
│   └── test_portable.bat           # Testing script
│
├── 🌐 Web_Players/                # HTML Player Templates
│   ├── nexus_tv.html            # 24-hour scheduled player
│   ├── buffer_tv.html           # TV with buffering controls
│   ├── multi_channel.html       # 1-6 simultaneous channels
│   ├── simple_player.html       # Clean video player
│   ├── web_iptv.html           # Sequential channel player
│   ├── rumble_channel.html     # Rumble video player
│   ├── stream_hub.html         # Live TV hub
│   ├── standalone_secure.html  # Secure standalone player
│   └── classic_tv.html         # Edge-to-edge classic TV
│
├── 🧪 tests/                      # All Test Files
│   ├── test_m3u_matrix.py       # Original test suite
│   └── test_m3u_matrix_comprehensive.py # 50+ edge case tests
│
├── 📚 Documentation/              # User Guides & Docs
│   ├── README.md                # Main documentation
│   ├── NDI_BROADCAST_GUIDE.md  # NDI setup guide
│   └── INSTALLER_GUIDE.md      # Installation guide
│
├── 💾 M3U_Matrix_Output/          # All Generated Content
│   ├── generated_pages/         # Generated player pages
│   │   └── index.html          # Navigation hub
│   ├── playlists/              # Saved playlists
│   ├── thumbnails/             # Video thumbnails
│   └── exports/                # Exported files
│
├── 📁 Sample_Playlists/           # Demo M3U Files
│   └── [Various .m3u files]
│
└── 📄 Root Files
    ├── README.md                # Main project README
    ├── replit.md               # Replit configuration
    ├── requirements.txt        # Python dependencies
    ├── package.json           # Node.js dependencies
    ├── LICENSE                # License file
    └── AUDIT_REPORT.txt       # System audit report
```

## 🚀 How to Use

### Starting the Applications

#### Windows:
```batch
# Launch M3U Matrix Pro
scripts\LAUNCH_M3U_MATRIX_PRO.bat

# Launch Video Player Pro
scripts\LAUNCH_VIDEO_PLAYER_PRO.bat
```

#### Linux/Mac:
```bash
# Launch M3U Matrix Pro
./scripts/launch_m3u_matrix_pro.sh

# Launch Video Player Pro
./scripts/launch_video_player_pro.sh
```

## 📦 Module Organization

### Core_Modules/
This directory contains all core business logic:
- **M3U Processing**: `m3u_validation.py` handles parsing and validation
- **Page Generation**: `page_generator.py` creates HTML player pages
- **Output Management**: `output_manager.py` manages file structure
- **NDI Broadcasting**: `ndi_output.py` provides broadcast capabilities
- **Redis Integration**: `redis_exporter.py`, `redis_api_server.py` for caching
- **Rumble Support**: `rumble_helper.py`, `rumble_category_browser.py` for Rumble

### scripts/
Contains all launch scripts and utilities:
- Platform-specific launchers (Windows .bat, Unix .sh)
- Distribution and packaging scripts
- Testing utilities

### Web_Players/
Self-contained HTML player templates:
- Each template is a complete, standalone HTML file
- No external dependencies (all libraries bundled)
- 100% offline capability for local files

### tests/
Comprehensive test coverage:
- Unit tests for core functionality
- Edge case testing (50+ tests)
- Performance benchmarks

## 🔄 Import Structure

All Python imports now use the centralized Core_Modules:

```python
# Example imports in Applications/
from Core_Modules.page_generator import NexusTVPageGenerator
from Core_Modules.output_manager import get_output_manager
from Core_Modules.m3u_validation import validate_channel
from Core_Modules.redis_exporter import get_redis_exporter
```

## ✅ Benefits of New Structure

1. **Clear Separation**: Applications, modules, scripts, and tests are cleanly separated
2. **Easy Navigation**: Logical grouping makes finding files intuitive
3. **Maintainability**: Related functionality is grouped together
4. **Scalability**: Easy to add new modules or features
5. **Testing**: All tests in one place for easy execution
6. **Distribution**: Scripts directory makes packaging easier

## 🔧 Migration Notes

### Files Moved:
- `src/utils/validation.py` → `Core_Modules/m3u_validation.py`
- `src/redis_exporter.py` → `Core_Modules/redis_exporter.py`
- `redis/api_server.py` → `Core_Modules/redis_api_server.py`
- `src/services/rumble_helper.py` → `Core_Modules/rumble_helper.py`
- `src/ui/rumble_category_browser.py` → `Core_Modules/rumble_category_browser.py`
- All launch scripts → `scripts/`
- All test files → `tests/`

### Import Updates:
- All imports updated to use `Core_Modules.` prefix
- Launch scripts updated to navigate from `scripts/` directory
- Test imports updated to reference new module locations

## 📝 Testing

Run all tests from the project root:

```bash
# Run original tests
python -m pytest tests/test_m3u_matrix.py

# Run comprehensive tests
python tests/test_m3u_matrix_comprehensive.py
```

## 🎯 Next Steps

1. **Verify Functionality**: Test all features work with new structure
2. **Update Documentation**: Ensure all docs reflect new paths
3. **CI/CD Updates**: Update any build scripts for new structure
4. **Distribution Testing**: Test portable distribution creation

---

*Directory reorganization completed on November 19, 2025*
*This structure follows best practices for Python project organization*