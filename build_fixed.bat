@echo off
REM Fixed build script for M3U Matrix Pro
REM Properly bundles Python runtime and creates folder distribution

echo ========================================
echo M3U MATRIX PRO - FIXED BUILD SCRIPT
echo ========================================
echo.

REM Step 1: Check Python version
echo [1/5] Checking Python version...
python --version
echo.

REM Step 2: Clean previous builds
echo [2/5] Cleaning previous builds...
if exist "dist" (
    echo Removing old dist folder...
    rmdir /s /q "dist"
)
if exist "build" (
    echo Removing old build folder...
    rmdir /s /q "build"
)
echo Clean complete!
echo.

REM Step 3: Run diagnostic check
echo [3/5] Running diagnostic check...
python check_pyinstaller_setup.py
echo.
pause

REM Step 4: Build with PyInstaller
echo [4/5] Building with PyInstaller (Fixed spec)...
echo.
pyinstaller --clean --noconfirm M3U_Matrix_Pro_Fixed.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    echo.
    echo Common fixes:
    echo 1. Use Python 3.11 or 3.12 (not 3.13)
    echo 2. Update PyInstaller: pip install --upgrade pyinstaller
    echo 3. Install dependencies: pip install tkinterdnd2 pillow requests
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Build successful!
echo.

REM Step 5: Verify the build
echo [5/5] Verifying build output...
echo.
echo ========================================
echo BUILD OUTPUT:
echo ========================================
echo.

if exist "dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe" (
    echo ✅ Main executable found!
    dir "dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe"
    echo.
    
    REM Check for Python DLL
    if exist "dist\M3U_Matrix_Pro\python*.dll" (
        echo ✅ Python DLL included!
        dir "dist\M3U_Matrix_Pro\python*.dll"
    ) else (
        echo ⚠️  Warning: Python DLL might be missing
        echo    This could cause runtime errors
    )
    echo.
    
    echo ========================================
    echo ✅ BUILD COMPLETE!
    echo ========================================
    echo.
    echo The application is in: dist\M3U_Matrix_Pro\
    echo.
    echo To run: Double-click dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe
    echo.
    echo To distribute: Copy the entire dist\M3U_Matrix_Pro folder
    echo.
) else (
    echo ❌ Build output not found!
    echo.
    echo Check the error messages above
    echo The build may have failed
)

pause