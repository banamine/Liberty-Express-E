@echo off
setlocal EnableDelayedExpansion
color 0B
title M3U Matrix - Build Installer (Simple)

echo ========================================
echo M3U MATRIX - Build Installer (Simple)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing PyInstaller...
pip install pyinstaller
echo.

REM Clean previous builds
if exist "build" (
    echo Cleaning previous build...
    rmdir /s /q build
)
if exist "dist" (
    rmdir /s /q dist
)
if exist "M3U_Matrix_Installer.spec" (
    del M3U_Matrix_Installer.spec
)
echo.

echo Building installer executable...
echo.

REM Simple build - only include essential files
pyinstaller --onefile ^
    --windowed ^
    --name "M3U_Matrix_Installer" ^
    --icon=NONE ^
    M3U_MATRIX_INSTALLER.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Installer created at: dist\M3U_Matrix_Installer.exe
echo Size: 
dir dist\M3U_Matrix_Installer.exe | find "M3U_Matrix_Installer.exe"
echo.
echo This is a STANDALONE installer that doesn't need external files.
echo Copy it anywhere and run it!
echo.
pause
endlocal
