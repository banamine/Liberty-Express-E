@echo off
setlocal EnableDelayedExpansion
color 0A
title M3U Matrix - PUNK & Liberty Express Network Setup

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║     M3U MATRIX - PUNK ^& Liberty Express Network Setup          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo Your Network Configuration:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🖥️  PUNK (Main PC)
echo     └─ IP: 192.168.1.204
echo     └─ MAC: 10-BF-48-B5-FB-D5
echo     └─ Speed: 1000 Mbps (Gigabit)
echo.
echo 🖥️  Liberty Express
echo     └─ IP: 192.168.1.188
echo     └─ MAC: 00-CE-39-D1-34-68
echo     └─ Speed: 1000 Mbps (Gigabit)
echo.
echo 🌐 Gateway: 192.168.1.254
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Auto-detect which PC this is
echo 🔍 Detecting which PC you're on...
echo.

ipconfig | find "192.168.1.204" >nul
if %errorlevel%==0 (
    set THISPC=PUNK
    set THISIP=192.168.1.204
    set OTHERPC=Liberty Express
    set OTHERIP=192.168.1.188
    set ROLE=SERVER
    goto DETECTED
)

ipconfig | find "192.168.1.188" >nul
if %errorlevel%==0 (
    set THISPC=Liberty Express
    set THISIP=192.168.1.188
    set OTHERPC=PUNK
    set OTHERIP=192.168.1.204
    set ROLE=CLIENT
    goto DETECTED
)

REM Manual selection if auto-detect fails
echo ⚠️  Could not auto-detect your PC
echo.
echo Which PC are you on?
echo 1. PUNK (192.168.1.204)
echo 2. Liberty Express (192.168.1.188)
echo.
set /p CHOICE="Enter 1 or 2: "

if "%CHOICE%"=="1" (
    set THISPC=PUNK
    set THISIP=192.168.1.204
    set OTHERPC=Liberty Express
    set OTHERIP=192.168.1.188
    set ROLE=SERVER
) else (
    set THISPC=Liberty Express
    set THISIP=192.168.1.188
    set OTHERPC=PUNK
    set OTHERIP=192.168.1.204
    set ROLE=CLIENT
)

:DETECTED
echo ✅ You are on: !THISPC! (!THISIP!)
echo 🎯 Will connect to: !OTHERPC! (!OTHERIP!)
echo 📡 Your role: !ROLE!
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    TESTING NETWORK CONNECTION
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Testing connection to !OTHERPC!...
ping -n 1 !OTHERIP! >nul 2>&1

if %errorlevel%==0 (
    echo ✅ !OTHERPC! is ONLINE and reachable!
    echo.
    set NETWORK_OK=1
) else (
    echo ❌ !OTHERPC! is OFFLINE or unreachable
    echo.
    echo Troubleshooting:
    echo 1. Make sure !OTHERPC! is powered on
    echo 2. Check network cables or WiFi connection
    echo 3. Verify both PCs are on the same network
    echo 4. Check Windows Firewall settings
    echo.
    set NETWORK_OK=0
    pause
    exit /b 1
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    SETUP OPTIONS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if "!ROLE!"=="SERVER" (
    echo You are on PUNK (Server). Choose an option:
    echo.
    echo 1. 📤 Share M3U Matrix with Liberty Express
    echo 2. 🔍 Check if Liberty Express can see this PC
    echo 3. 📁 Open shared folder location
    echo 4. ❌ Exit
    echo.
    set /p OPTION="Enter your choice (1-4): "
    
    if "!OPTION!"=="1" goto SETUP_SERVER
    if "!OPTION!"=="2" goto CHECK_VISIBILITY
    if "!OPTION!"=="3" goto OPEN_SHARE
    if "!OPTION!"=="4" goto END
    
) else (
    echo You are on Liberty Express (Client). Choose an option:
    echo.
    echo 1. 📥 Connect to PUNK and copy M3U Matrix
    echo 2. 🌐 Run M3U Matrix from PUNK over network
    echo 3. 📂 Browse PUNK's shared files
    echo 4. ❌ Exit
    echo.
    set /p OPTION="Enter your choice (1-4): "
    
    if "!OPTION!"=="1" goto COPY_FROM_SERVER
    if "!OPTION!"=="2" goto RUN_FROM_NETWORK
    if "!OPTION!"=="3" goto BROWSE_NETWORK
    if "!OPTION!"=="4" goto END
)

:SETUP_SERVER
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    SETTING UP PUNK AS SERVER
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Get parent directory
cd ..
set SHARE_PATH=%CD%

echo 📁 Sharing folder: !SHARE_PATH!
echo.

REM Use Windows built-in sharing
echo Setting up network share...
net share M3U_Matrix="!SHARE_PATH!" /GRANT:Everyone,FULL >nul 2>&1

if %errorlevel%==0 (
    echo ✅ Network share created successfully!
    echo.
    echo 📡 Share Name: M3U_Matrix
    echo 📁 Path: !SHARE_PATH!
    echo 🌐 Network Path: \\!THISIP!\M3U_Matrix
    echo.
    echo Liberty Express can now connect using:
    echo    \\!THISIP!\M3U_Matrix
    echo.
) else (
    echo ⚠️  Automatic sharing failed. Manual setup required:
    echo.
    echo 1. Right-click this folder: !SHARE_PATH!
    echo 2. Select Properties ^> Sharing
    echo 3. Click "Advanced Sharing"
    echo 4. Check "Share this folder"
    echo 5. Name it: M3U_Matrix
    echo 6. Click Permissions ^> Add Everyone with Full Control
    echo.
)

echo.
echo Next step: Run this script on Liberty Express
echo They will be able to connect automatically!
echo.
pause
goto END

:CHECK_VISIBILITY
echo.
echo Checking if Liberty Express can see this PC...
echo.
ping -n 1 !OTHERIP!
echo.
echo If ping succeeds, Liberty Express can reach you!
pause
goto END

:OPEN_SHARE
echo.
cd ..
explorer .
goto END

:COPY_FROM_SERVER
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CONNECTING TO PUNK AND COPYING FILES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set NETWORK_PATH=\\!OTHERIP!\M3U_Matrix

echo Checking for shared folder on PUNK...
if exist "!NETWORK_PATH!" (
    echo ✅ Found M3U Matrix share on PUNK!
    echo.
    
    set /p COPY_TO="Enter local path to copy to (or press Enter for C:\M3U_Matrix): "
    if "!COPY_TO!"=="" set COPY_TO=C:\M3U_Matrix
    
    echo.
    echo Copying from: !NETWORK_PATH!
    echo Copying to: !COPY_TO!
    echo.
    echo This may take a moment...
    
    xcopy /E /I /Y "!NETWORK_PATH!" "!COPY_TO!"
    
    if %errorlevel%==0 (
        echo.
        echo ✅ Copy complete!
        echo 📁 M3U Matrix installed at: !COPY_TO!
        echo.
        echo To launch:
        echo    !COPY_TO!\Launch_M3U_Matrix.bat
        echo.
    ) else (
        echo.
        echo ❌ Copy failed. Check permissions and try again.
    )
) else (
    echo ❌ Cannot find M3U Matrix share on PUNK
    echo.
    echo Make sure PUNK has run the server setup first!
    echo Network path: !NETWORK_PATH!
)
echo.
pause
goto END

:RUN_FROM_NETWORK
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    RUNNING FROM NETWORK
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set NETWORK_PATH=\\!OTHERIP!\M3U_Matrix

if exist "!NETWORK_PATH!\Launch_M3U_Matrix.bat" (
    echo ✅ Found M3U Matrix on PUNK
    echo.
    echo Launching from network...
    start "" "!NETWORK_PATH!\Launch_M3U_Matrix.bat"
) else (
    echo ❌ Cannot find M3U Matrix on PUNK
    echo.
    echo Network path: !NETWORK_PATH!
)
pause
goto END

:BROWSE_NETWORK
echo.
set NETWORK_PATH=\\!OTHERIP!\M3U_Matrix
echo Opening: !NETWORK_PATH!
echo.
explorer "!NETWORK_PATH!"
goto END

:END
echo.
echo Thank you for using M3U Matrix Network Setup! 🌐
echo.
endlocal
