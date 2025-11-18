@echo off
REM Build script for M3U Matrix Pro - FULL Package
REM Creates standalone Windows installer with all features

echo ========================================
echo M3U MATRIX PRO - FULL INSTALLER BUILD
echo ========================================
echo.

REM Step 1: Build executable with PyInstaller
echo [1/3] Building executable with PyInstaller...
echo.
pyinstaller --clean M3U_Matrix_Pro.spec

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check if PyInstaller is installed: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo ✅ Executable built successfully!
echo.

REM Step 2: Compile installer with Inno Setup
echo [2/3] Compiling installer with Inno Setup...
echo.

REM Try to find Inno Setup Compiler
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"

if not exist %ISCC% (
    echo.
    echo ERROR: Inno Setup Compiler not found!
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

%ISCC% installer_full.iss

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Installer compiled successfully!
echo.

REM Step 3: Show results
echo [3/3] Build complete!
echo.
echo ========================================
echo OUTPUT FILES:
echo ========================================
dir /B installers\M3U_Matrix_Pro_Setup_v1.0.0_FULL.exe
echo.
echo ✅ FULL installer package ready for distribution!
echo.
pause
