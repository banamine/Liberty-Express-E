@echo off
echo ========================================
echo M3U MATRIX - Create Portable Package
echo ========================================
echo.

set PACKAGE_NAME=M3U_Matrix_Portable_%date:~-4%%date:~-7,2%%date:~-10,2%
set PACKAGE_DIR=portable_packages\%PACKAGE_NAME%

echo Creating portable package: %PACKAGE_NAME%
echo.

REM Create package directory
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

REM Copy application files
echo Copying application files...
xcopy /E /I /Y ..\src "%PACKAGE_DIR%\src"
xcopy /E /I /Y ..\templates "%PACKAGE_DIR%\templates"
xcopy /E /I /Y "..\Sample Playlists" "%PACKAGE_DIR%\Sample Playlists"

REM Copy documentation
copy /Y ..\*.md "%PACKAGE_DIR%\"
copy /Y ..\*.txt "%PACKAGE_DIR%\"
copy /Y ..\requirements.txt "%PACKAGE_DIR%\"

REM Copy startup scripts
copy /Y ..\START_WEB_SERVER.py "%PACKAGE_DIR%\"
copy /Y ..\START_WEB_SERVER.bat "%PACKAGE_DIR%\"

REM Create necessary directories
mkdir "%PACKAGE_DIR%\logs"
mkdir "%PACKAGE_DIR%\exports"
mkdir "%PACKAGE_DIR%\backups"
mkdir "%PACKAGE_DIR%\thumbnails"
mkdir "%PACKAGE_DIR%\epg_data"
mkdir "%PACKAGE_DIR%\temp"
mkdir "%PACKAGE_DIR%\generated_pages"

REM Create portable mode marker
echo This is a portable installation. > "%PACKAGE_DIR%\PORTABLE_MODE.txt"
echo You can copy this entire folder to any location (USB stick, external drive, etc.) >> "%PACKAGE_DIR%\PORTABLE_MODE.txt"
echo and run it without installation. >> "%PACKAGE_DIR%\PORTABLE_MODE.txt"

REM Create launcher batch file
echo @echo off > "%PACKAGE_DIR%\START_M3U_MATRIX.bat"
echo echo Starting M3U Matrix PRO... >> "%PACKAGE_DIR%\START_M3U_MATRIX.bat"
echo cd /d "%%~dp0" >> "%PACKAGE_DIR%\START_M3U_MATRIX.bat"
echo python src\M3U_MATRIX_PRO.py >> "%PACKAGE_DIR%\START_M3U_MATRIX.bat"
echo pause >> "%PACKAGE_DIR%\START_M3U_MATRIX.bat"

REM Create README for portable package
echo ========================================= > "%PACKAGE_DIR%\README_PORTABLE.txt"
echo M3U MATRIX ALL-IN-ONE - Portable Package >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo ========================================= >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo. >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo This is a portable version that requires NO installation. >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo. >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo QUICK START: >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo 1. Ensure Python 3.11+ is installed >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo 2. Run: pip install -r requirements.txt >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo 3. Double-click START_M3U_MATRIX.bat >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo. >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo USB STICK USAGE: >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo - Copy entire folder to USB stick >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo - Run from any Windows PC with Python installed >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo - All data stays on the USB stick >> "%PACKAGE_DIR%\README_PORTABLE.txt"
echo. >> "%PACKAGE_DIR%\README_PORTABLE.txt"

echo.
echo ========================================
echo Package created successfully!
echo ========================================
echo.
echo Location: %PACKAGE_DIR%
echo.
echo To use:
echo 1. Copy entire folder to USB stick or share on network
echo 2. On target PC: Install Python 3.11+
echo 3. Run: pip install -r requirements.txt
echo 4. Double-click START_M3U_MATRIX.bat
echo.

REM Ask if user wants to create ZIP archive
set /p CREATE_ZIP="Create ZIP archive for easy sharing? (Y/N): "
if /i "%CREATE_ZIP%"=="Y" (
    echo.
    echo Creating ZIP archive...
    powershell Compress-Archive -Path "%PACKAGE_DIR%" -DestinationPath "portable_packages\%PACKAGE_NAME%.zip" -Force
    echo.
    echo ZIP created: portable_packages\%PACKAGE_NAME%.zip
    echo.
)

pause
