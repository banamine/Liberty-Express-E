@echo off
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

REM Build the installer
pyinstaller --onefile ^
    --windowed ^
    --name "M3U_Matrix_Installer" ^
    --icon=NONE ^
    --add-data "../src;src" ^
    --add-data "../templates;templates" ^
    --add-data "../Sample Playlists;Sample Playlists" ^
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
