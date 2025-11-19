# M3U MATRIX PRO - QUICK FIX FOR DLL ERROR

## Problem
The original PyInstaller build created a folder distribution that couldn't find `python313.dll`, causing:
```
Failed to load Python DLL
LoadLibrary: The specified module could not be found.
```

## Solution
Use the **SINGLE FILE** build that bundles everything into one executable.

---

## Quick Build Instructions

### 1. Install Requirements (if not already installed)
```bash
pip install pyinstaller
pip install tkinterdnd2 pillow requests
```

### 2. Build Single Executable
```batch
build_single_exe.bat
```

This creates: `dist\M3U_Matrix_Pro.exe` (single file, ~30-50 MB)

### 3. Run the Application
Simply double-click `dist\M3U_Matrix_Pro.exe` - no other files needed!

---

## What's Different?

| Original Build | Single File Build |
|----------------|------------------|
| Multiple files in folder | ONE .exe file |
| DLL loading issues | Everything bundled |
| ~4.5 MB exe + dependencies | ~30-50 MB single exe |
| Can break if files missing | Always works |

---

## Benefits of Single File

✅ **No DLL Errors** - Python DLL bundled inside  
✅ **Portable** - Copy anywhere, it just works  
✅ **No Dependencies** - No Python installation needed  
✅ **Simple Distribution** - One file to share  

---

## For Installer Creation (Optional)

Once you have the working single exe:

1. **Install Inno Setup** from https://jrsoftware.org/isinfo.php
2. Use the updated installer scripts to package the single exe
3. Or just distribute the exe directly - it's fully standalone!

---

## Troubleshooting

**Build fails with "pyinstaller not found"**
```bash
pip install pyinstaller
```

**Import errors during build**
```bash
pip install tkinterdnd2 pillow requests
```

**Antivirus warning**
- This is normal for unsigned executables
- Add exception or use code signing certificate

---

## File Size Note

The single exe is larger (~30-50 MB vs ~5 MB) because it includes:
- Python interpreter
- All Python libraries
- All dependencies
- All templates and data

This is a worthwhile tradeoff for reliability and ease of distribution!