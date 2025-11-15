@echo off
echo ========================================
echo M3U MATRIX - Network Deployment Tool
echo ========================================
echo.
echo This tool helps you deploy M3U Matrix to other computers on your network.
echo.

REM Get network share path
set /p NETWORK_PATH="Enter network share path (e.g., \\SERVER\Share\M3U_Matrix): "

if "%NETWORK_PATH%"=="" (
    echo ERROR: Network path cannot be empty!
    pause
    exit /b 1
)

echo.
echo Deploying to: %NETWORK_PATH%
echo.

REM Create network directory if it doesn't exist
if not exist "%NETWORK_PATH%" (
    echo Creating network directory...
    mkdir "%NETWORK_PATH%"
)

REM Create portable package first
echo Step 1: Creating portable package...
call CREATE_PORTABLE_PACKAGE.bat

REM Get the latest portable package
for /f "delims=" %%i in ('dir /b /ad /o-d portable_packages\M3U_Matrix_Portable_*') do (
    set LATEST_PACKAGE=%%i
    goto :found
)
:found

if "%LATEST_PACKAGE%"=="" (
    echo ERROR: No portable package found!
    pause
    exit /b 1
)

echo.
echo Step 2: Copying to network share...
xcopy /E /I /Y "portable_packages\%LATEST_PACKAGE%" "%NETWORK_PATH%"

REM Create network deployment info file
echo ========================================= > "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo M3U MATRIX - Network Deployment >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo ========================================= >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo Deployed on: %date% %time% >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo From: %COMPUTERNAME% >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo Network Path: %NETWORK_PATH% >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo INSTALLATION INSTRUCTIONS: >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo ========================== >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo From any computer on your network: >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 1. Navigate to: %NETWORK_PATH% >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 2. Copy entire folder to your local drive >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 3. Install Python 3.11+ if not already installed >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 4. Open Command Prompt in the copied folder >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 5. Run: pip install -r requirements.txt >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 6. Double-click START_M3U_MATRIX.bat >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo Or run directly from network (slower): >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 1. Navigate to: %NETWORK_PATH% >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo 2. Double-click START_M3U_MATRIX.bat >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"
echo. >> "%NETWORK_PATH%\NETWORK_DEPLOYMENT_INFO.txt"

REM Create auto-installer script for network clients
echo @echo off > "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo M3U MATRIX - Installing from network... >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo. >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo set /p INSTALL_DIR="Enter installation directory (or press Enter for default): " >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo if "%%INSTALL_DIR%%"=="" set INSTALL_DIR=C:\M3U_Matrix >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo. >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo Installing to: %%INSTALL_DIR%% >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo mkdir "%%INSTALL_DIR%%" >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo xcopy /E /I /Y "%NETWORK_PATH%\*" "%%INSTALL_DIR%%" >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo. >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo. >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo Installation complete! >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo Location: %%INSTALL_DIR%% >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo. >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo Next steps: >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo 1. Install Python 3.11+ if not already installed >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo 2. Run: pip install -r requirements.txt >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo echo 3. Run: START_M3U_MATRIX.bat >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"
echo pause >> "%NETWORK_PATH%\INSTALL_FROM_NETWORK.bat"

echo.
echo ========================================
echo Network deployment complete!
echo ========================================
echo.
echo Deployment location: %NETWORK_PATH%
echo.
echo Users can now:
echo 1. Navigate to %NETWORK_PATH%
echo 2. Run INSTALL_FROM_NETWORK.bat for easy local installation
echo 3. Or run directly from network location
echo.
echo To update: Simply run this script again to deploy the latest version
echo.
pause
