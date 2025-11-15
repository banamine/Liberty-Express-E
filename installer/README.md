# 📦 M3U Matrix Installer System

## Quick Overview

This folder contains everything you need to deploy M3U Matrix ALL-IN-ONE to any Windows PC.

---

## 🚀 3 Deployment Options

### 1️⃣ USB Stick (Portable) - Recommended for Multiple PCs

**Run:** `CREATE_PORTABLE_PACKAGE.bat`

- Creates portable package in `portable_packages/` folder
- Copy to USB stick
- Plug into any Windows PC and run
- **No installation needed!**

---

### 2️⃣ Full Installation - Recommended for Single PC

**Run:** `BUILD_INSTALLER.bat`

- Creates `dist\M3U_Matrix_Installer.exe`
- Run the .exe on target PC
- Choose "Full Installation" mode
- Gets desktop shortcuts and Start Menu entry

---

### 3️⃣ Network Deployment - Recommended for Multiple PCs on Network

**Run:** `NETWORK_DEPLOY.bat`

- Deploys to network share (e.g., `\\MyServer\Share\M3U_Matrix`)
- Other PCs can run `INSTALL_FROM_NETWORK.bat`
- Updates all machines from one central location

---

## 🔄 Auto-Updates

**Run:** `AUTO_UPDATER.py` from installed directory

- Checks for new versions (GitHub or manual)
- Shows changelog
- Requires authorization key (set first time)
- Automatically downloads and installs
- Creates backup before updating

---

## 📋 Files in This Folder

| File | What It Does |
|------|--------------|
| `CREATE_PORTABLE_PACKAGE.bat` | ✅ **Start here** for USB stick |
| `BUILD_INSTALLER.bat` | Build standalone .exe installer |
| `NETWORK_DEPLOY.bat` | Deploy to network share |
| `M3U_MATRIX_INSTALLER.py` | Main installer (GUI) |
| `AUTO_UPDATER.py` | Auto-update system |
| `INSTALLER_GUIDE.md` | Complete documentation |
| `QUICK_START_INSTALLER.txt` | Quick reference |

---

## ⚡ Quick Start

**Want to run from USB stick?**
```
1. Double-click: CREATE_PORTABLE_PACKAGE.bat
2. Copy folder to USB stick
3. Done! Run START_M3U_MATRIX.bat from USB
```

**Want to install on one PC?**
```
1. Double-click: BUILD_INSTALLER.bat
2. Run: dist\M3U_Matrix_Installer.exe
3. Choose "Full Installation"
4. Done!
```

**Want to share on your network?**
```
1. Double-click: NETWORK_DEPLOY.bat
2. Enter network path (e.g., \\MyPC\Share)
3. Tell others to run INSTALL_FROM_NETWORK.bat
4. Done!
```

---

## 🔐 User Verification

The auto-updater requires authorization to prevent unauthorized updates:

1. **First time:** Set your own password/key
2. **Updates:** Enter your key to authorize
3. **Security:** Keys hashed with SHA-256

---

## 📖 Need More Help?

- **Quick reference:** `QUICK_START_INSTALLER.txt`
- **Complete guide:** `INSTALLER_GUIDE.md`
- **Troubleshooting:** See INSTALLER_GUIDE.md

---

## 🎯 Which Option Should I Choose?

| Scenario | Recommended Option |
|----------|-------------------|
| I want to run from USB stick | 1️⃣ Portable |
| I want to install on my PC | 2️⃣ Full Install |
| I want to share with family | 3️⃣ Network Deploy |
| I have multiple PCs | 1️⃣ Portable or 3️⃣ Network |
| I want best performance | 2️⃣ Full Install |

---

**Ready to deploy? Choose an option above and get started!** 🚀
