@echo off
echo ============================================
echo    M3U MATRIX PRO - Windows Launcher
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo Starting M3U Matrix Pro...
echo.

REM Run the application from project root
python src\M3U_MATRIX_PRO.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo    ERROR: Application failed to start
    echo ============================================
    echo.
    echo Common fixes:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Make sure you're running from the project root folder
    echo 3. Check WINDOWS_SETUP.md for troubleshooting
    echo.
    pause
)
