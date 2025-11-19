# 📦 M3U Matrix ALL-IN-ONE - Complete Installer Guide

## Overview
This guide covers all installation and deployment options for M3U Matrix ALL-IN-ONE, including portable USB installation, full Windows installation, network deployment, and auto-updates.

---

## 🎯 Installation Options

### Option 1: Portable Installation (USB Stick)
**Perfect for:** Running from USB stick, no installation needed

**Steps:**
1. Run `CREATE_PORTABLE_PACKAGE.bat`
2. Copy the generated folder to your USB stick
3. On any Windows PC with Python 3.11+:
   - Open folder on USB stick
   - Run: `pip install -r requirements.txt`
   - Double-click `START_M3U_MATRIX.bat`

**Advantages:**
- ✅ No installation required
- ✅ Run from any PC
- ✅ All data stays on USB stick
- ✅ Perfect for multiple machines

**Limitations:**
- ⚠️ Requires Python 3.11+ on target PC
- ⚠️ Slower than local installation (USB speed)

---

### Option 2: Full Windows Installation
**Perfect for:** Permanent installation on one PC

**Steps:**
1. Run `BUILD_INSTALLER.bat` to create installer
2. Run `dist\M3U_Matrix_Installer.exe`
3. Choose "Full Installation"
4. Select installation directory
5. Choose shortcut options
6. Click Install

**Advantages:**
- ✅ Desktop and Start Menu shortcuts
- ✅ Permanent installation
- ✅ Fast performance
- ✅ Professional setup

**Installation Locations:**
- Default: `C:\Program Files\M3U Matrix`
- Custom: Choose any location

---

### Option 3: Network Deployment
**Perfect for:** Sharing with other PCs on your network

**Steps:**
1. Run `NETWORK_DEPLOY.bat`
2. Enter network share path (e.g., `\\SERVER\Share\M3U_Matrix`)
3. Wait for deployment to complete
4. On other network PCs:
   - Navigate to network path
   - Run `INSTALL_FROM_NETWORK.bat`
   - Or copy folder locally

**Advantages:**
- ✅ Deploy to multiple PCs easily
- ✅ Centralized updates
- ✅ One-click installation for users
- ✅ Run directly from network (optional)

**Network Path Examples:**
- `\\MyPC\SharedFolder\M3U_Matrix`
- `\\192.168.1.100\Share\M3U_Matrix`
- `Z:\M3U_Matrix` (mapped network drive)

---

## 🔄 Auto-Update System

### Setup Auto-Updates

**For GitHub-based Updates:**
1. Upload project to GitHub repository
2. Edit `AUTO_UPDATER.py`:
   ```python
   GITHUB_API = "https://api.github.com/repos/YOUR_USERNAME/m3u-matrix/releases/latest"
   ```
3. Create releases with version tags (e.g., `v5.3.1`)
4. Users run `AUTO_UPDATER.py` to check for updates

**For Network-based Updates:**
1. Deploy latest version to network share
2. Users copy from network to update
3. Or re-run `INSTALL_FROM_NETWORK.bat`

### Using Auto-Updater

1. Run `AUTO_UPDATER.py` from installed directory
2. Click "Check for Updates"
3. View changelog
4. Click "Download & Install"
5. Application updates and restarts

---

## 🛠️ Building the Installer

### Prerequisites
```bash
pip install pyinstaller
```

### Build Standalone Installer
```bash
cd installer
BUILD_INSTALLER.bat
```

**Output:** `dist\M3U_Matrix_Installer.exe` (single-file installer)

### Build Portable Package
```bash
cd installer
CREATE_PORTABLE_PACKAGE.bat
```

**Output:** `portable_packages\M3U_Matrix_Portable_YYYYMMDD\` folder

**Optional:** Creates ZIP archive for easy sharing

---

## 📋 Complete Deployment Workflow

### Scenario 1: USB Stick for Multiple PCs

```
1. Your PC:
   └── Run CREATE_PORTABLE_PACKAGE.bat
   └── Copy to USB stick

2. Other PCs:
   └── Insert USB stick
   └── Install Python 3.11+
   └── Run: pip install -r requirements.txt
   └── Run: START_M3U_MATRIX.bat
   └── Done!
```

### Scenario 2: Network Deployment

```
1. Your PC (Master):
   └── Run NETWORK_DEPLOY.bat
   └── Enter network share path
   └── Deployment complete

2. Client PCs:
   └── Open \\SERVER\Share\M3U_Matrix
   └── Run INSTALL_FROM_NETWORK.bat
   └── Choose install location
   └── Done!
```

### Scenario 3: Full Installer Distribution

```
1. Your PC:
   └── Run BUILD_INSTALLER.bat
   └── Share dist\M3U_Matrix_Installer.exe

2. Other PCs:
   └── Run M3U_Matrix_Installer.exe
   └── Choose Full Installation
   └── Complete setup wizard
   └── Done!
```

---

## 🔧 Installer Components

### Files in `installer/` Directory

| File | Purpose |
|------|---------|
| `M3U_MATRIX_INSTALLER.py` | Main installer GUI application |
| `BUILD_INSTALLER.bat` | Creates standalone .exe installer |
| `CREATE_PORTABLE_PACKAGE.bat` | Creates portable USB package |
| `NETWORK_DEPLOY.bat` | Deploys to network share |
| `AUTO_UPDATER.py` | Auto-update checker and installer |
| `INSTALLER_GUIDE.md` | This documentation |

### Generated Files

| File/Folder | Description |
|-------------|-------------|
| `dist\M3U_Matrix_Installer.exe` | Standalone installer executable |
| `portable_packages\` | Portable package folders |
| `install_config.json` | Installation metadata |
| `PORTABLE_MODE.txt` | Marker for portable installations |

---

## 📁 Installation Directory Structure

```
M3U Matrix/
├── src/                          # Application source code
├── templates/                    # NEXUS TV templates
├── Sample Playlists/            # Example M3U files
├── logs/                        # Application logs
├── exports/                     # Exported playlists
├── backups/                     # Automatic backups
├── thumbnails/                  # Cached channel logos
├── epg_data/                    # EPG XML data
├── temp/                        # Temporary files
├── generated_pages/             # NEXUS TV pages
├── START_WEB_SERVER.bat         # Web server launcher
├── START_M3U_MATRIX.bat         # Application launcher (portable)
├── m3u_matrix_settings.json     # User settings
├── install_config.json          # Installation metadata
└── requirements.txt             # Python dependencies
```

---

## ⚙️ Settings and Configuration

### Installation Settings (`install_config.json`)
```json
{
  "version": "5.3.0",
  "install_date": "2025-11-15T...",
  "install_mode": "portable",
  "install_path": "C:\\M3U Matrix",
  "auto_update": true
}
```

### Application Settings (`m3u_matrix_settings.json`)
```json
{
  "window_geometry": "1600x950",
  "theme": "dark",
  "auto_check_channels": false,
  "cache_thumbnails": true,
  "use_ffmpeg_extraction": false
}
```

---

## 🚀 Quick Start Examples

### USB Stick Mode
```bash
# On your PC:
cd installer
CREATE_PORTABLE_PACKAGE.bat
# Copy portable_packages\M3U_Matrix_Portable_*\ to USB

# On other PC:
# Insert USB, open folder
pip install -r requirements.txt
START_M3U_MATRIX.bat
```

### Network Install
```bash
# On master PC:
cd installer
NETWORK_DEPLOY.bat
# Enter: \\MyServer\Share\M3U_Matrix

# On client PC:
# Open \\MyServer\Share\M3U_Matrix
INSTALL_FROM_NETWORK.bat
```

### Full Install
```bash
# Build installer:
cd installer
BUILD_INSTALLER.bat

# Distribute and run:
dist\M3U_Matrix_Installer.exe
```

---

## 🔐 User Verification & Security

### Installation Verification
- SHA-256 checksums for downloaded files
- Version verification against GitHub releases
- Digital signature support (optional)

### Update Verification
- Compares current vs latest version
- Shows changelog before update
- Requires user confirmation
- Backup before update (optional)

---

## 🐛 Troubleshooting

### Installer Won't Build
**Problem:** PyInstaller not found  
**Solution:**
```bash
pip install pyinstaller
```

### Portable Mode Not Working
**Problem:** Python not found  
**Solution:** Install Python 3.11+ and add to PATH

### Network Deployment Fails
**Problem:** Access denied to network share  
**Solution:** 
- Check network permissions
- Use UNC path: `\\SERVER\Share`
- Map network drive

### Auto-Update Not Working
**Problem:** GitHub API not configured  
**Solution:** Update `GITHUB_API` in `AUTO_UPDATER.py`

### Shortcuts Not Created
**Problem:** win32com not available  
**Solution:** Installer creates .bat files as fallback

---

## 📊 Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.3.0 | 2025-11-15 | Initial installer system |
| 5.2.0 | 2025-11-15 | Dynamic UI features |
| 5.1.0 | 2025-11-15 | Live mode features |
| 5.0.0 | 2025-11-15 | Hybrid mode |

---

## 🎯 Best Practices

### For USB Stick Deployment
1. ✅ Use high-speed USB 3.0+ stick
2. ✅ Create portable package with dependencies
3. ✅ Include Python installer on USB (optional)
4. ✅ Test on clean PC before distribution

### For Network Deployment
1. ✅ Use reliable network share
2. ✅ Set proper permissions (read/execute)
3. ✅ Keep one master copy updated
4. ✅ Provide clear instructions to users

### For Full Installation
1. ✅ Test installer on clean virtual machine
2. ✅ Create start menu and desktop shortcuts
3. ✅ Include uninstaller
4. ✅ Sign installer (for production)

---

## 📞 Support

For issues with installation:
1. Check this guide first
2. Review troubleshooting section
3. Check application logs in `logs/` folder
4. Verify Python version: `python --version`

---

## 🎓 Advanced Topics

### Creating Custom Installers
Modify `M3U_MATRIX_INSTALLER.py` to add:
- Custom branding
- Additional installation options
- Pre-configuration settings
- License agreement

### Automated Network Updates
Create scheduled task to:
1. Check for updates daily
2. Download to network share
3. Notify users of new version

### Enterprise Deployment
Use Group Policy or SCCM to:
1. Deploy silently with parameters
2. Configure default settings
3. Manage updates centrally

---

**Your all-in-one installer system is ready!** 🚀

Choose the deployment method that works best for your needs and start distributing M3U Matrix to all your machines!
