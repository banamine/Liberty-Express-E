@echo off
setlocal EnableDelayedExpansion
title M3U Matrix - One-Click Network Connect
color 0A

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   M3U MATRIX - One-Click Network Connect        ║
echo ╚══════════════════════════════════════════════════╝
echo.

REM Get computer name
for /f "tokens=*" %%i in ('hostname') do set HOSTNAME=%%i

echo 🖥️  Your Computer: %HOSTNAME%
echo 🌐 Detecting network...
echo.

REM Detect which PC this is
ipconfig | find "192.168.1.204" >nul
if %errorlevel%==0 (
    set THISPC=PUNK
    set OTHERPC=Liberty Express
    set OTHERIP=192.168.1.188
    goto DETECTED
)

ipconfig | find "192.168.1.188" >nul
if %errorlevel%==0 (
    set THISPC=Liberty Express
    set OTHERPC=PUNK
    set OTHERIP=192.168.1.204
    goto DETECTED
)

echo ⚠️  Could not auto-detect your PC
echo.
echo Please choose:
echo 1. PUNK (192.168.1.204)
echo 2. Liberty Express (192.168.1.188)
echo.
set /p CHOICE="Enter 1 or 2: "

if "%CHOICE%"=="1" (
    set THISPC=PUNK
    set OTHERPC=Liberty Express
    set OTHERIP=192.168.1.188
) else (
    set THISPC=Liberty Express
    set OTHERPC=PUNK
    set OTHERIP=192.168.1.204
)

:DETECTED
echo.
echo ✅ Detected: %THISPC%
echo 🔍 Looking for: %OTHERPC% (%OTHERIP%)
echo.

REM Ping the other PC
echo Testing connection to %OTHERPC%...
ping -n 1 %OTHERIP% >nul 2>&1

if %errorlevel%==0 (
    echo ✅ %OTHERPC% is ONLINE!
    echo.
    
    REM Check for shared folder
    if exist "\\%OTHERIP%\M3U_Matrix" (
        echo ✅ Found M3U Matrix share on %OTHERPC%!
        echo.
        echo What would you like to do?
        echo.
        echo 1. Copy M3U Matrix to this PC
        echo 2. Run directly from network
        echo 3. Open network folder
        echo.
        set /p ACTION="Choose (1-3): "
        
        if "!ACTION!"=="1" (
            echo.
            echo Copying M3U Matrix from network...
            xcopy /E /I /Y "\\%OTHERIP%\M3U_Matrix" "C:\M3U_Matrix"
            echo.
            echo ✅ Copy complete!
            echo Location: C:\M3U_Matrix
            echo Run: C:\M3U_Matrix\START_M3U_MATRIX.bat
            pause
        ) else if "!ACTION!"=="2" (
            echo.
            echo Starting M3U Matrix from network...
            start "" "\\%OTHERIP%\M3U_Matrix\START_M3U_MATRIX.bat"
        ) else (
            echo.
            echo Opening network folder...
            explorer "\\%OTHERIP%\M3U_Matrix"
        )
    ) else (
        echo ⚠️  M3U Matrix share not found on %OTHERPC%
        echo.
        echo Please run NETWORK_DEPLOY.bat on %OTHERPC% first.
        pause
    )
) else (
    echo ❌ %OTHERPC% is OFFLINE or unreachable
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure %OTHERPC% is powered on
    echo 2. Check that both PCs are connected to the same network
    echo 3. Verify IP address: %OTHERIP%
    echo 4. Check Windows Firewall settings
    echo.
    pause
)

endlocal
