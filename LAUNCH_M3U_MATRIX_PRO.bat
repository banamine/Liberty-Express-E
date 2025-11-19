@echo off
echo ========================================
echo     M3U MATRIX PRO - IPTV Manager
echo ========================================
echo.
echo Starting M3U Matrix Pro...
echo.

cd /d "%~dp0Applications"
python M3U_MATRIX_PRO.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start M3U Matrix Pro
    echo Please ensure Python is installed and in your PATH
    pause
)