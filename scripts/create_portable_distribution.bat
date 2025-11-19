@echo off
REM ===================================================
REM  M3U MATRIX PRO - PORTABLE PYTHON DISTRIBUTION
REM  Creates a fully self-contained portable app
REM ===================================================

setlocal enabledelayedexpansion
color 0A
cls

echo.
echo ====================================================
echo   M3U MATRIX PRO - PORTABLE DISTRIBUTION CREATOR
echo ====================================================
echo.
echo This will create a portable version of M3U Matrix Pro
echo that includes Python and all dependencies.
echo No installation required on target machines!
echo.
pause

REM Set up variables
set PORTABLE_DIR=M3U_Matrix_Pro_Portable
set PYTHON_VERSION=3.11.9
set PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-3.11.9-embed-amd64.zip
set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py

REM Create portable directory structure
echo.
echo Step 1: Creating portable directory structure...
echo ------------------------------------------------
if exist "%PORTABLE_DIR%" (
    echo Removing existing portable directory...
    rmdir /s /q "%PORTABLE_DIR%"
)

mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\python"
mkdir "%PORTABLE_DIR%\app"
mkdir "%PORTABLE_DIR%\app\src"
mkdir "%PORTABLE_DIR%\app\src\videos"
mkdir "%PORTABLE_DIR%\app\src\data"
mkdir "%PORTABLE_DIR%\app\templates"
mkdir "%PORTABLE_DIR%\generated_pages"
mkdir "%PORTABLE_DIR%\temp"

echo Directory structure created!

REM Download portable Python
echo.
echo Step 2: Downloading portable Python %PYTHON_VERSION%...
echo ------------------------------------------------
echo This may take a few minutes...
echo.

powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile '%PORTABLE_DIR%\temp\python-embed.zip'}"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download Python!
    echo Please check your internet connection.
    pause
    exit /b 1
)

echo Python downloaded successfully!

REM Extract Python
echo.
echo Step 3: Extracting Python...
echo ------------------------------------------------
powershell -Command "& {Expand-Archive -Path '%PORTABLE_DIR%\temp\python-embed.zip' -DestinationPath '%PORTABLE_DIR%\python' -Force}"
if %errorlevel% neq 0 (
    echo ERROR: Failed to extract Python!
    pause
    exit /b 1
)

echo Python extracted!

REM Modify python311._pth to enable site-packages
echo.
echo Step 4: Configuring portable Python...
echo ------------------------------------------------
echo python311.zip > "%PORTABLE_DIR%\python\python311._pth"
echo . >> "%PORTABLE_DIR%\python\python311._pth"
echo Lib >> "%PORTABLE_DIR%\python\python311._pth"
echo Lib\site-packages >> "%PORTABLE_DIR%\python\python311._pth"
echo import site >> "%PORTABLE_DIR%\python\python311._pth"

REM Create Lib directory structure
mkdir "%PORTABLE_DIR%\python\Lib"
mkdir "%PORTABLE_DIR%\python\Lib\site-packages"

echo Python configured!

REM Download get-pip.py
echo.
echo Step 5: Installing pip...
echo ------------------------------------------------
powershell -Command "& {Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%PORTABLE_DIR%\temp\get-pip.py'}"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download pip installer!
    pause
    exit /b 1
)

REM Install pip
"%PORTABLE_DIR%\python\python.exe" "%PORTABLE_DIR%\temp\get-pip.py" --no-warn-script-location
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pip!
    pause
    exit /b 1
)

echo Pip installed successfully!

REM Install required packages
echo.
echo Step 6: Installing dependencies...
echo ------------------------------------------------
"%PORTABLE_DIR%\python\python.exe" -m pip install --no-warn-script-location requests
"%PORTABLE_DIR%\python\python.exe" -m pip install --no-warn-script-location pillow
"%PORTABLE_DIR%\python\python.exe" -m pip install --no-warn-script-location tkinterdnd2-universal

echo Dependencies installed!

REM Copy application files
echo.
echo Step 7: Copying application files...
echo ------------------------------------------------

REM Copy main Python files
echo Copying Python files...
if exist "src\videos\M3U_MATRIX_PRO.py" (
    copy "src\videos\M3U_MATRIX_PRO.py" "%PORTABLE_DIR%\app\src\videos\" >nul
)
if exist "src\page_generator.py" (
    copy "src\page_generator.py" "%PORTABLE_DIR%\app\src\" >nul
)
if exist "src\page_generator_fix.py" (
    copy "src\page_generator_fix.py" "%PORTABLE_DIR%\app\src\" >nul
)
if exist "src\rumble_helper.py" (
    copy "src\rumble_helper.py" "%PORTABLE_DIR%\app\src\" >nul
)
if exist "src\utils.py" (
    copy "src\utils.py" "%PORTABLE_DIR%\app\src\" >nul
)
if exist "src\navigation_hub_generator.py" (
    copy "src\navigation_hub_generator.py" "%PORTABLE_DIR%\app\src\" >nul
)
if exist "src\nav_hub_generator.py" (
    copy "src\nav_hub_generator.py" "%PORTABLE_DIR%\app\src\" >nul
)

REM Copy data files
echo Copying data files...
if exist "src\data\rumble_channels.json" (
    copy "src\data\rumble_channels.json" "%PORTABLE_DIR%\app\src\data\" >nul
)

REM Copy templates
echo Copying templates...
if exist "templates\" (
    xcopy "templates" "%PORTABLE_DIR%\app\templates" /E /I /Q /Y >nul
)

REM Copy Sample Playlists if they exist
if exist "Sample Playlists\" (
    echo Copying sample playlists...
    xcopy "Sample Playlists" "%PORTABLE_DIR%\Sample Playlists" /E /I /Q /Y >nul
)

echo Application files copied!

REM Create launcher batch file
echo.
echo Step 8: Creating launcher...
echo ------------------------------------------------

echo @echo off > "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo REM M3U Matrix Pro Portable Launcher >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo. >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo cd /d "%%~dp0" >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo. >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo REM Set Python path to use portable version >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo set PYTHONPATH=%%~dp0app\src;%%~dp0app >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo set PYTHONHOME= >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo. >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo REM Launch the application >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo echo Starting M3U Matrix Pro... >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo "%%~dp0python\python.exe" "%%~dp0app\src\videos\M3U_MATRIX_PRO.py" >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo. >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo if %%errorlevel%% neq 0 ( >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo     echo. >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo     echo Error launching application! >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo     pause >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"
echo ) >> "%PORTABLE_DIR%\Launch_M3U_Matrix_Pro.bat"

REM Create README
echo.
echo Step 9: Creating documentation...
echo ------------------------------------------------

echo M3U MATRIX PRO - PORTABLE VERSION > "%PORTABLE_DIR%\README.txt"
echo ================================= >> "%PORTABLE_DIR%\README.txt"
echo. >> "%PORTABLE_DIR%\README.txt"
echo This is a portable version of M3U Matrix Pro that includes: >> "%PORTABLE_DIR%\README.txt"
echo - Python %PYTHON_VERSION% (no installation required) >> "%PORTABLE_DIR%\README.txt"
echo - All required dependencies >> "%PORTABLE_DIR%\README.txt"
echo - Complete application with all templates >> "%PORTABLE_DIR%\README.txt"
echo. >> "%PORTABLE_DIR%\README.txt"
echo HOW TO USE: >> "%PORTABLE_DIR%\README.txt"
echo ----------- >> "%PORTABLE_DIR%\README.txt"
echo 1. Double-click "Launch_M3U_Matrix_Pro.bat" >> "%PORTABLE_DIR%\README.txt"
echo 2. The application will start automatically >> "%PORTABLE_DIR%\README.txt"
echo 3. Generated pages will appear in the "generated_pages" folder >> "%PORTABLE_DIR%\README.txt"
echo. >> "%PORTABLE_DIR%\README.txt"
echo FEATURES: >> "%PORTABLE_DIR%\README.txt"
echo --------- >> "%PORTABLE_DIR%\README.txt"
echo - No Python installation required on target machine >> "%PORTABLE_DIR%\README.txt"
echo - Completely self-contained >> "%PORTABLE_DIR%\README.txt"
echo - Can run from USB drive or any folder >> "%PORTABLE_DIR%\README.txt"
echo - All 6 page generators included >> "%PORTABLE_DIR%\README.txt"
echo. >> "%PORTABLE_DIR%\README.txt"
echo DISTRIBUTION: >> "%PORTABLE_DIR%\README.txt"
echo ------------- >> "%PORTABLE_DIR%\README.txt"
echo Copy the entire "M3U_Matrix_Pro_Portable" folder to any location. >> "%PORTABLE_DIR%\README.txt"
echo The app will work immediately without any installation. >> "%PORTABLE_DIR%\README.txt"

REM Clean up temp files
echo.
echo Step 10: Cleaning up...
echo ------------------------------------------------
rmdir /s /q "%PORTABLE_DIR%\temp" 2>nul

REM Final summary
echo.
echo ====================================================
echo   PORTABLE DISTRIBUTION CREATED SUCCESSFULLY!
echo ====================================================
echo.
echo Location: %CD%\%PORTABLE_DIR%
echo.
echo This folder contains:
echo - Python %PYTHON_VERSION% (portable)
echo - M3U Matrix Pro application
echo - All templates and dependencies
echo - Launch_M3U_Matrix_Pro.bat (double-click to run)
echo.
echo To distribute:
echo 1. ZIP the entire "%PORTABLE_DIR%" folder
echo 2. Users can extract anywhere and run
echo 3. No Python installation needed!
echo.
echo Total size: ~100-150 MB (much smaller than PyInstaller!)
echo.
echo Press any key to open the portable folder...
pause >nul

explorer "%PORTABLE_DIR%"