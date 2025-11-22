# Manual Setup: Portable Python Distribution for M3U Matrix Pro

If the automated script doesn't work, follow these manual steps:

## Step 1: Download Portable Python

1. Go to: https://www.python.org/ftp/python/3.11.9/
2. Download: `python-3.11.9-embed-amd64.zip` (about 8 MB)
3. Create a folder: `M3U_Matrix_Pro_Portable`
4. Extract the ZIP into: `M3U_Matrix_Pro_Portable\python\`

## Step 2: Configure Python for Packages

1. In `M3U_Matrix_Pro_Portable\python\`, find `python311._pth`
2. Edit it (Notepad) to contain exactly:
```
python311.zip
.
Lib
Lib\site-packages
import site
```

3. Create these folders:
   - `M3U_Matrix_Pro_Portable\python\Lib\`
   - `M3U_Matrix_Pro_Portable\python\Lib\site-packages\`

## Step 3: Install pip

1. Download: https://bootstrap.pypa.io/get-pip.py
2. Save to: `M3U_Matrix_Pro_Portable\python\`
3. Open Command Prompt in that folder
4. Run: `python.exe get-pip.py`

## Step 4: Install Dependencies

In the same Command Prompt:
```batch
python.exe -m pip install requests
python.exe -m pip install pillow
python.exe -m pip install tkinterdnd2-universal
```

## Step 5: Copy Application Files

Create this structure:
```
M3U_Matrix_Pro_Portable/
├── python/                    (from steps above)
├── app/
│   ├── src/
│   │   ├── videos/
│   │   │   └── M3U_MATRIX_PRO.py
│   │   ├── data/
│   │   │   └── rumble_channels.json
│   │   ├── page_generator.py
│   │   ├── rumble_helper.py
│   │   └── utils.py
│   └── templates/
│       └── (all 6 template folders)
├── Sample Playlists/          (optional)
└── generated_pages/           (create empty folder)
```

## Step 6: Create Launcher

Create `Launch_M3U_Matrix_Pro.bat` in the main folder:
```batch
@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0app\src;%~dp0app
set PYTHONHOME=
echo Starting M3U Matrix Pro...
"%~dp0python\python.exe" "%~dp0app\src\videos\M3U_MATRIX_PRO.py"
if %errorlevel% neq 0 pause
```

## Done!

Your portable distribution is ready. The entire folder can be:
- Copied to any Windows PC
- Run from USB drive
- Used without Python installation

Total size: ~100-150 MB (vs 500+ MB for PyInstaller)