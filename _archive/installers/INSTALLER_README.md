# M3U MATRIX PRO - Windows Installer Build Guide

## Overview

This directory contains all files needed to create professional Windows installers for M3U Matrix Pro.

**Two installer packages available:**
- **FULL Package:** Includes all features, sample playlists, complete documentation
- **LITE Package:** Minimal install, optimized for size (no samples)

---

## Requirements

### Software Required

1. **Python 3.11+** - Must be installed and in PATH
   - Download: https://www.python.org/downloads/

2. **PyInstaller** - Python to EXE converter
   ```bash
   pip install pyinstaller
   ```

3. **Inno Setup 6** - Windows installer compiler
   - Download: https://jrsoftware.org/isinfo.php
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

4. **Required Python Packages**
   ```bash
   pip install tkinterdnd2 pillow requests
   ```

---

## Quick Start

### Build Both Installers (Recommended)

```batch
build_all_installers.bat
```

This will create:
- `M3U_Matrix_Pro_Setup_v1.0.0_FULL.exe` (~50-80 MB)
- `M3U_Matrix_Pro_Setup_v1.0.0_LITE.exe` (~40-60 MB)

### Build Individual Packages

**FULL Package:**
```batch
build_installer_full.bat
```

**LITE Package:**
```batch
build_installer_lite.bat
```

---

## Build Process

### Step 1: PyInstaller (Python → EXE)

PyInstaller bundles the Python application into a standalone executable:

**Input:** 
- `src/videos/M3U_MATRIX_PRO.py` (main app)
- `src/page_generator.py` (generators)
- `src/ui/` (UI components)
- `templates/` (6 player templates)
- `src/data/` (Rumble channels DB)

**Output:** 
- `dist/M3U_Matrix_Pro/` (folder with EXE + dependencies)

**Configuration:** `M3U_Matrix_Pro.spec`

### Step 2: Inno Setup (EXE → Installer)

Inno Setup creates a Windows installer from the PyInstaller output:

**Features:**
- ✅ Directory selection dialog
- ✅ Desktop shortcut option (unchecked by default)
- ✅ Start Menu shortcuts (always created)
- ⚠️ Taskbar pin attempt (Windows 11 requires manual confirmation)
- ✅ Uninstaller included

**Configurations:**
- `installer_full.iss` - FULL package script
- `installer_lite.iss` - LITE package script

---

## Output Files

### After Building

```
installers/
├── M3U_Matrix_Pro_Setup_v1.0.0_FULL.exe  (FULL installer)
└── M3U_Matrix_Pro_Setup_v1.0.0_LITE.exe  (LITE installer)
```

### Installation Locations

**User selects during install (default: `C:\Program Files\M3U Matrix Pro\`)**

Installed files:
```
M3U Matrix Pro/
├── M3U_Matrix_Pro.exe          (Main application)
├── templates/                   (6 player templates)
│   ├── nexus_tv_template.html
│   ├── rumble_channel_template.html
│   ├── multi_channel_template.html
│   ├── buffer_tv_template.html
│   ├── web-iptv-extension/
│   └── simple-player/
├── src/
│   └── data/
│       └── rumble_channels.json (30 Rumble channels)
├── Sample Playlists/            (FULL package only)
├── M3U_MATRIX_README.md
└── logo.ico
```

---

## Package Comparison

| Feature | FULL Package | LITE Package |
|---------|--------------|--------------|
| **Size** | ~50-80 MB | ~40-60 MB |
| **Application** | ✅ Included | ✅ Included |
| **Templates (6)** | ✅ Included | ✅ Included |
| **Rumble Browser** | ✅ 30 channels | ✅ 30 channels |
| **Sample Playlists** | ✅ Included | ❌ Not included |
| **Documentation** | ✅ Full | ✅ Basic |
| **Compression** | Standard | Ultra |

**Recommendation:** 
- **FULL** for first-time users who want samples to test with
- **LITE** for advanced users or minimal downloads

---

## Installer Features

### What Installers Do

1. **Install Prompt:** User selects installation directory
2. **Desktop Shortcut:** Optional checkbox (unchecked by default)
3. **Start Menu:** Always creates Start Menu shortcuts
4. **Taskbar Pin:** Attempts to pin to taskbar (Windows 11 blocks automatic pinning - users must manually pin from Start Menu)
5. **Launch Option:** "Launch M3U Matrix Pro" checkbox after install

### What Users Get

- ✅ Fully standalone application (no Python required)
- ✅ All 6 page generators (NEXUS TV, Rumble, Simple, Web IPTV, Multi-Channel, Buffer TV)
- ✅ Rumble Browser with 30 pre-loaded channels
- ✅ Complete template system
- ✅ Uninstaller for clean removal

---

## Troubleshooting

### PyInstaller Build Fails

**Error:** `ModuleNotFoundError: No module named 'tkinterdnd2'`
```bash
pip install tkinterdnd2 pillow requests
```

**Error:** `pyinstaller: command not found`
```bash
pip install pyinstaller
```

### Inno Setup Build Fails

**Error:** `ISCC.exe not found`
- Install Inno Setup from https://jrsoftware.org/isinfo.php
- Default path: `C:\Program Files (x86)\Inno Setup 6\`

**Error:** `Source file not found: dist\M3U_Matrix_Pro\*`
- Run PyInstaller first: `pyinstaller M3U_Matrix_Pro.spec`

### Installer Won't Run

**Error:** Windows Defender / SmartScreen warning
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- Or: Sign executable with code signing certificate

---

## Advanced Customization

### Change App Version

Edit version in **both** files:
1. `installer_full.iss` → Line 5: `#define MyAppVersion "1.0.0"`
2. `installer_lite.iss` → Line 5: `#define MyAppVersion "1.0.0"`

### Add More Sample Playlists (FULL only)

Add files to `Sample Playlists/` directory - they'll be included automatically

### Customize Icon

Replace `logo.ico` with your custom icon (256x256 recommended)

### Change Install Directory

Edit installer scripts:
```pascal
DefaultDirName={autopf}\YOUR_APP_NAME
```

---

## Distribution

### File Sharing

Upload installers to:
- ✅ GitHub Releases
- ✅ Google Drive / Dropbox
- ✅ Your website
- ✅ File hosting services

### Recommended Distribution Text

```
M3U MATRIX PRO v1.0.0 - IPTV Management & Streaming Platform

Two installer options available:

🔷 FULL Package (~50 MB)
   - Includes sample playlists for testing
   - Complete documentation
   - Recommended for first-time users

🔷 LITE Package (~40 MB)
   - Minimal installation
   - No sample playlists
   - Optimized for size

System Requirements:
- Windows 7, 8, 10, or 11 (64-bit)
- 200 MB free disk space
- No Python installation required
```

---

## Code Signing (Optional but Recommended)

To remove Windows Defender warnings, sign your executable:

1. **Get Code Signing Certificate**
   - Purchase from: DigiCert, Sectigo, etc.
   - Cost: ~$100-300/year

2. **Sign Executable**
   ```batch
   signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe"
   ```

3. **Sign Installer**
   ```batch
   signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "installers\M3U_Matrix_Pro_Setup_v1.0.0_FULL.exe"
   ```

---

## Support

For issues or questions:
- Check `M3U_MATRIX_PRO_COMPETENCY_REPORT.md` for validation results
- Review `M3U_MATRIX_README.md` for application documentation

---

## Files Reference

| File | Purpose |
|------|---------|
| `M3U_Matrix_Pro.spec` | PyInstaller configuration |
| `installer_full.iss` | Inno Setup script (FULL) |
| `installer_lite.iss` | Inno Setup script (LITE) |
| `build_installer_full.bat` | Build FULL package |
| `build_installer_lite.bat` | Build LITE package |
| `build_all_installers.bat` | Build both packages |
| `INSTALLER_README.md` | This file |

---

**Ready to build? Run `build_all_installers.bat` to get started!** 🚀
