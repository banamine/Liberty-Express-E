@echo off
REM ========================================
REM  PACKAGE PORTABLE DISTRIBUTION FOR SHARING
REM ========================================
color 0B
cls

echo.
echo ========================================
echo   PACKAGE FOR DISTRIBUTION
echo ========================================
echo.
echo This will create a ZIP file ready for sharing.
echo.

REM Check if portable directory exists
if not exist "M3U_Matrix_Pro_Portable" (
    echo ERROR: Portable distribution not found!
    echo.
    echo Please run create_portable_distribution.bat first.
    echo.
    pause
    exit /b 1
)

REM Get current date for filename
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set TODAY=%%c%%a%%b
)
set TODAY=%TODAY: =%

set ZIPNAME=M3U_Matrix_Pro_Portable_%TODAY%.zip

echo Creating: %ZIPNAME%
echo.
echo This may take a minute...
echo.

REM Try to use PowerShell to create ZIP
powershell -Command "& {Compress-Archive -Path 'M3U_Matrix_Pro_Portable' -DestinationPath '%ZIPNAME%' -Force}" 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   PACKAGING COMPLETE!
    echo ========================================
    echo.
    echo Created: %ZIPNAME%
    echo.
    
    REM Get file size
    for %%A in (%ZIPNAME%) do set SIZE=%%~zA
    set /a SIZE_MB=%SIZE%/1048576
    echo Size: ~%SIZE_MB% MB
    echo.
    echo This ZIP file contains everything needed to run M3U Matrix Pro:
    echo - Portable Python 3.11
    echo - All dependencies
    echo - Complete application
    echo - No installation required!
    echo.
    echo Users can:
    echo 1. Extract the ZIP anywhere
    echo 2. Double-click Launch_M3U_Matrix_Pro.bat
    echo 3. Start using the application immediately
    echo.
) else (
    echo.
    echo ERROR: Failed to create ZIP file!
    echo.
    echo Alternative: You can manually ZIP the folder:
    echo 1. Right-click on "M3U_Matrix_Pro_Portable" folder
    echo 2. Select "Send to" -^> "Compressed (zipped) folder"
    echo.
)

pause