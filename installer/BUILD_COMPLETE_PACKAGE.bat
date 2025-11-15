@echo off
setlocal EnableDelayedExpansion
color 0E
title M3U Matrix - Build Complete Package

echo ========================================
echo M3U MATRIX - Build Complete Package
echo ========================================
echo.
echo This creates a portable ZIP package with everything included.
echo No compilation needed - pure Python!
echo.

REM Get parent directory
cd ..
set SOURCE_DIR=%CD%

echo Source: %SOURCE_DIR%
echo.

REM Create package directory
set PACKAGE_NAME=M3U_Matrix_Portable
set PACKAGE_DIR=%TEMP%\%PACKAGE_NAME%

if exist "%PACKAGE_DIR%" (
    echo Cleaning old package...
    rmdir /s /q "%PACKAGE_DIR%"
)

mkdir "%PACKAGE_DIR%"
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    COPYING FILES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Copy essential directories
echo [1/7] Copying src folder...
xcopy /E /I /Q "src" "%PACKAGE_DIR%\src\"

echo [2/7] Copying templates folder...
xcopy /E /I /Q "templates" "%PACKAGE_DIR%\templates\"

echo [3/7] Copying installer folder...
xcopy /E /I /Q "installer" "%PACKAGE_DIR%\installer\"

REM Copy optional directories if they exist
if exist "Sample Playlists" (
    echo [4/7] Copying Sample Playlists folder...
    xcopy /E /I /Q "Sample Playlists" "%PACKAGE_DIR%\Sample Playlists\"
) else (
    echo [4/7] Skipping Sample Playlists (not found)
)

REM Copy all batch files
echo [5/7] Copying batch files...
copy /Y *.bat "%PACKAGE_DIR%\" >nul 2>&1

REM Copy documentation
echo [6/7] Copying documentation...
copy /Y *.md "%PACKAGE_DIR%\" >nul 2>&1
copy /Y *.txt "%PACKAGE_DIR%\" >nul 2>&1

REM Copy requirements
echo [7/7] Copying requirements.txt...
copy /Y requirements.txt "%PACKAGE_DIR%\" >nul 2>&1

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING FOLDERS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create empty directories for runtime
mkdir "%PACKAGE_DIR%\logs" 2>nul
mkdir "%PACKAGE_DIR%\exports" 2>nul
mkdir "%PACKAGE_DIR%\backups" 2>nul
mkdir "%PACKAGE_DIR%\thumbnails" 2>nul
mkdir "%PACKAGE_DIR%\epg_data" 2>nul
mkdir "%PACKAGE_DIR%\temp" 2>nul
mkdir "%PACKAGE_DIR%\generated_pages" 2>nul

echo ✅ Created runtime directories
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING README
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create portable README
(
echo M3U MATRIX ALL-IN-ONE - Portable Package
echo ═══════════════════════════════════════════════════════════════════
echo.
echo QUICK START:
echo 1. Run QUICK_INSTALL.bat to install dependencies
echo 2. Run Launch_M3U_Matrix.bat to start the application
echo.
echo NETWORK SETUP:
echo - Run installer\SETUP_PUNK_LIBERTY.bat to connect PCs
echo.
echo DOCUMENTATION:
echo - See M3U_MATRIX_README.md for complete guide
echo - See INSTALLATION_COMPLETE.txt for setup instructions
echo.
echo This is a PORTABLE package - run from anywhere!
echo No installation to Windows required.
echo.
) > "%PACKAGE_DIR%\START_HERE.txt"

echo ✅ Created START_HERE.txt
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING ZIP ARCHIVE
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set OUTPUT_ZIP=%SOURCE_DIR%\%PACKAGE_NAME%.zip

REM Check if PowerShell is available
powershell -Command "Write-Output 'PowerShell OK'" >nul 2>&1
if %errorlevel%==0 (
    echo Creating ZIP with PowerShell...
    powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%OUTPUT_ZIP%' -Force"
    
    if exist "%OUTPUT_ZIP%" (
        echo.
        echo ✅ Package created successfully!
    ) else (
        echo.
        echo ❌ Failed to create ZIP
        echo Manual step: Compress %PACKAGE_DIR% to ZIP manually
    )
) else (
    echo.
    echo ⚠️  PowerShell not available
    echo Manual step required:
    echo 1. Open: %PACKAGE_DIR%
    echo 2. Select all files
    echo 3. Right-click ^> Send to ^> Compressed (zipped) folder
    echo 4. Move ZIP to: %SOURCE_DIR%
    explorer "%PACKAGE_DIR%"
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    COMPLETE!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Package location: %OUTPUT_ZIP%
echo.
echo This package contains:
echo ✅ All source code
echo ✅ All scripts and tools
echo ✅ Complete installer system
echo ✅ Network helper tools
echo ✅ Documentation
echo.
echo Ready to:
echo - Copy to USB stick
echo - Share on network
echo - Email to others
echo - Extract anywhere and run
echo.
pause
endlocal
