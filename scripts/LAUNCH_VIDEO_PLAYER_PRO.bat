@echo off
echo ========================================
echo   VIDEO PLAYER PRO - Media Workbench
echo ========================================
echo.
echo Starting Video Player Pro...
echo.

cd /d "%~dp0..\Applications"
python VIDEO_PLAYER_PRO.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start Video Player Pro
    echo Please ensure Python is installed and in your PATH
    pause
)