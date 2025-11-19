# M3U MATRIX PRO - WINDOWS BUILD FIX

## Problem Solved
When running the packaged executable on Windows (N:\Liberty-Express-1\Liberty-Express-\), generated pages were not appearing in the `generated_pages` folder next to the executable.

## Root Cause
The page generators were using `Path("generated_pages")` which creates folders relative to the current working directory. When PyInstaller runs, this could be:
- A temporary extraction folder (for onefile builds)
- The wrong directory (for onedir builds)

## Solution Applied
Created `page_generator_fix.py` that:
1. Detects if running as a PyInstaller executable
2. Creates `generated_pages` next to the executable (not in temp folders)
3. Correctly locates bundled templates

## How It Works

### When Running as Executable:
```
N:\Liberty-Express-1\Liberty-Express-\
├── M3U_Matrix_Pro.exe
├── generated_pages\        ← Pages saved HERE (next to exe)
│   ├── nexus_tv\
│   ├── buffer_tv\
│   ├── multi_channel\
│   └── ...
└── templates\
```

### When Running as Python Script:
Uses normal relative paths for development.

## Testing the Fix

1. **Rebuild with the fixed spec:**
   ```batch
   pyinstaller --clean M3U_Matrix_Pro_Fixed.spec
   ```

2. **Run the executable:**
   ```batch
   dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe
   ```

3. **Generate a page:**
   - Import an M3U playlist
   - Click any generator button (NEXUS TV, Buffer TV, etc.)
   - Name your page

4. **Check for pages:**
   Look in `dist\M3U_Matrix_Pro\generated_pages\`
   
   Your pages should now appear there!

## Key Changes Made

1. **page_generator_fix.py** - Path detection and fixing module
2. **M3U_MATRIX_PRO.py** - Updated imports to use fixed paths when frozen
3. **Path Resolution** - Pages save next to executable, not in temp folders

## Distribution

When distributing your app, include the entire folder:
```
M3U_Matrix_Pro\
├── M3U_Matrix_Pro.exe
├── python311.dll
├── templates\              (all 6 templates)
├── src\data\              (Rumble channels)
├── generated_pages\       (created on first use)
└── [other dependencies]
```

Users will find their generated pages in the `generated_pages` folder next to the executable!

## Verification

After generating pages, check:
- `N:\Liberty-Express-1\Liberty-Express-\generated_pages\` should contain new folders
- Each template type creates its own subfolder (nexus_tv, buffer_tv, etc.)
- HTML files are created with embedded playlists

The fix ensures pages are always saved in the correct location!