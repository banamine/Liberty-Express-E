@echo off
setlocal EnableDelayedExpansion
echo ========================================
echo M3U MATRIX - Build Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building installer executable...
echo.

REM Check what folders exist
set ADD_DATA_ARGS=--add-data "../src;src" --add-data "../templates;templates"

if exist "..\Sample Playlists" (
    echo Including Sample Playlists folder...
    set ADD_DATA_ARGS=%ADD_DATA_ARGS% --add-data "../Sample Playlists;Sample Playlists"
) else (
    echo Skipping Sample Playlists (folder not found)
)

REM Build the installer
pyinstaller --onefile ^
    --windowed ^
    --name "M3U_Matrix_Installer" ^
    --icon=NONE ^
    !ADD_DATA_ARGS! ^
    --add-data "../*.md;." ^
    --add-data "../*.txt;." ^
    --add-data "../*.py;." ^
    --add-data "../*.bat;." ^
    M3U_MATRIX_INSTALLER.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Installer location: dist\M3U_Matrix_Installer.exe
echo.
echo You can now:
echo 1. Run the installer directly
echo 2. Copy to USB stick for portable installation
echo 3. Share with other machines on your network
echo.
pause
endlocal
