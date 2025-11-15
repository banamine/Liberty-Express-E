@echo off
echo ========================================
echo M3U MATRIX - Network Setup Wizard
echo ========================================
echo.
echo This wizard will help you connect your computers!
echo.
echo Your network computers:
echo - PUNK (Main PC): 192.168.1.204
echo - Liberty Express: 192.168.1.188
echo.
echo ========================================
echo CHOOSE YOUR SETUP:
echo ========================================
echo.
echo 1. I'm on PUNK (192.168.1.204) - Set up as server
echo 2. I'm on Liberty Express (192.168.1.188) - Connect to server
echo 3. Open Network Helper (Auto-detect)
echo 4. Manual setup instructions
echo 5. Exit
echo.

set /p CHOICE="Enter your choice (1-5): "

if "%CHOICE%"=="1" goto SETUP_SERVER
if "%CHOICE%"=="2" goto CONNECT_CLIENT
if "%CHOICE%"=="3" goto NETWORK_HELPER
if "%CHOICE%"=="4" goto MANUAL_SETUP
if "%CHOICE%"=="5" goto END

echo Invalid choice!
pause
exit /b

:SETUP_SERVER
echo.
echo ========================================
echo Setting up PUNK as Server
echo ========================================
echo.
echo Step 1: Creating shared folder...
mkdir "C:\M3U_Matrix_Share" 2>nul
echo.
echo Step 2: Deploying application to share...
call NETWORK_DEPLOY.bat
echo.
echo Your server is ready!
echo Other computers can connect to: \\192.168.1.204\M3U_Matrix
echo.
pause
goto END

:CONNECT_CLIENT
echo.
echo ========================================
echo Connecting Liberty Express to Server
echo ========================================
echo.
echo Attempting to connect to PUNK (192.168.1.204)...
echo.

REM Check if server is reachable
ping -n 1 192.168.1.204 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Cannot reach PUNK (192.168.1.204)
    echo Make sure PUNK is powered on and connected to the network.
    pause
    goto END
)

echo ✅ Server is online!
echo.

REM Try to access network share
if exist "\\192.168.1.204\M3U_Matrix" (
    echo ✅ Found network share!
    echo.
    echo Copying installer from network...
    xcopy /E /I /Y "\\192.168.1.204\M3U_Matrix" "C:\M3U_Matrix"
    echo.
    echo ✅ Installation complete!
    echo Location: C:\M3U_Matrix
    echo.
    echo Run: C:\M3U_Matrix\START_M3U_MATRIX.bat
    echo.
) else (
    echo ⚠️ Network share not found.
    echo.
    echo Please make sure:
    echo 1. PUNK has run the server setup (Option 1)
    echo 2. Folder sharing is enabled on PUNK
    echo 3. Network path is: \\192.168.1.204\M3U_Matrix
    echo.
)
pause
goto END

:NETWORK_HELPER
echo.
echo Opening Network Helper...
python NETWORK_HELPER.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not start Network Helper
    echo Make sure Python is installed
)
pause
goto END

:MANUAL_SETUP
echo.
echo ========================================
echo Manual Setup Instructions
echo ========================================
echo.
echo ON PUNK (192.168.1.204) - Server Setup:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. Create folder: C:\M3U_Matrix_Share
echo 2. Copy M3U Matrix files to this folder
echo 3. Right-click folder ^> Properties ^> Sharing
echo 4. Click "Share" and set permissions
echo 5. Note the network path shown
echo.
echo ON LIBERTY EXPRESS (192.168.1.188) - Client:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 1. Open File Explorer
echo 2. Type in address bar: \\192.168.1.204\M3U_Matrix_Share
echo 3. Copy folder to local drive if desired
echo 4. Run START_M3U_MATRIX.bat
echo.
echo TROUBLESHOOTING:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo • Make sure both PCs are on same network
echo • Check Windows Firewall settings
echo • Verify network discovery is enabled
echo • Try pinging: ping 192.168.1.204
echo.
pause
goto END

:END
echo.
echo Thank you for using M3U Matrix Network Setup!
echo.
