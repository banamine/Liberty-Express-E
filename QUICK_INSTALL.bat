@echo off
setlocal EnableDelayedExpansion
color 0B
title M3U Matrix - Quick Installation

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          M3U MATRIX ALL-IN-ONE - Quick Installation             ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Get current directory
set "INSTALL_DIR=%~dp0"
cd /d "%INSTALL_DIR%"

echo 📁 Installation Directory: %INSTALL_DIR%
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CHECKING REQUIREMENTS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is NOT installed!
    echo.
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected
echo.

REM Check Node.js
echo [2/3] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Node.js is NOT installed
    echo    This is optional but recommended for the web server
    echo    Download from: https://nodejs.org/
    echo.
    set NODE_INSTALLED=0
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js !NODE_VERSION! detected
    echo.
    set NODE_INSTALLED=1
)

REM Check pip
echo [3/3] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is NOT available!
    echo.
    echo Installing pip...
    python -m ensurepip --upgrade
)
echo ✅ pip is available
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    INSTALLING DEPENDENCIES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Install Python packages
echo Installing Python packages...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Some packages failed to install
    echo    Trying individual installation...
    echo.
    pip install requests
    pip install Pillow
    pip install tkinterdnd2
)
echo.
echo ✅ Python packages installed
echo.

REM Install Node.js serve (optional)
if !NODE_INSTALLED! equ 1 (
    echo Installing web server (serve)...
    call npm install -g serve
    if %errorlevel% equ 0 (
        echo ✅ Web server installed
    ) else (
        echo ⚠️  Web server installation failed (optional)
    )
    echo.
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING DIRECTORIES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create necessary directories
set DIRS=logs exports backups thumbnails epg_data temp generated_pages

for %%d in (%DIRS%) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo ✅ Created: %%d
    ) else (
        echo ✓  Exists: %%d
    )
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING SHORTCUTS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create desktop launcher
echo @echo off > "Launch_M3U_Matrix.bat"
echo cd /d "%INSTALL_DIR%" >> "Launch_M3U_Matrix.bat"
echo python src\M3U_MATRIX_PRO.py >> "Launch_M3U_Matrix.bat"
echo ✅ Created: Launch_M3U_Matrix.bat
echo.

REM Create web server launcher
echo @echo off > "Launch_Web_Player.bat"
echo cd /d "%INSTALL_DIR%" >> "Launch_Web_Player.bat"
echo start http://localhost:5000 >> "Launch_Web_Player.bat"
echo npx serve -l 5000 --no-clipboard >> "Launch_Web_Player.bat"
echo ✅ Created: Launch_Web_Player.bat
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING DEFAULT SETTINGS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create default settings if not exists
if not exist "m3u_matrix_settings.json" (
    echo {> m3u_matrix_settings.json
    echo   "window_geometry": "1600x950",>> m3u_matrix_settings.json
    echo   "theme": "dark",>> m3u_matrix_settings.json
    echo   "auto_check_channels": false,>> m3u_matrix_settings.json
    echo   "cache_thumbnails": true,>> m3u_matrix_settings.json
    echo   "use_ffmpeg_extraction": false>> m3u_matrix_settings.json
    echo }>> m3u_matrix_settings.json
    echo ✅ Created default settings
) else (
    echo ✓  Settings file already exists
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    INSTALLATION COMPLETE!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ M3U Matrix is ready to use!
echo.
echo 📁 Installed at: %INSTALL_DIR%
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    QUICK START
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo To launch M3U Matrix PRO (Desktop App):
echo    └─ Double-click: Launch_M3U_Matrix.bat
echo.
echo To launch NEXUS TV Web Player:
echo    └─ Double-click: Launch_Web_Player.bat
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    NETWORK SETUP (Optional)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo To connect with other PCs on your network:
echo    └─ Run: installer\SETUP_PUNK_LIBERTY.bat
echo    └─ Or: installer\ONE_CLICK_NETWORK_CONNECT.bat
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p LAUNCH="Would you like to launch M3U Matrix now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    echo.
    echo Launching M3U Matrix PRO...
    start "" "Launch_M3U_Matrix.bat"
)

echo.
echo Thank you for installing M3U Matrix ALL-IN-ONE! 🎬
echo.
pause
endlocal
