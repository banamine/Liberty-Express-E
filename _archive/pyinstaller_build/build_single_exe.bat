@echo off
REM Build script for M3U Matrix Pro - SINGLE EXE VERSION
REM Creates a single standalone executable with all dependencies bundled

echo ========================================
echo M3U MATRIX PRO - SINGLE EXE BUILD
echo ========================================
echo.
echo This will create a SINGLE .exe file with
echo everything bundled inside (no DLL errors!)
echo.
pause

REM Clean previous builds
echo [1/3] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo.

REM Build single executable with PyInstaller
echo [2/3] Building single executable...
echo.
pyinstaller --clean M3U_Matrix_Pro_SingleFile.spec

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo.
    echo Possible solutions:
    echo 1. Install PyInstaller: pip install pyinstaller
    echo 2. Install required packages: pip install tkinterdnd2 pillow requests
    echo 3. Make sure Python is in your PATH
    pause
    exit /b 1
)

echo.
echo ✅ Build successful!
echo.

REM Show results
echo [3/3] Build complete!
echo.
echo ========================================
echo OUTPUT FILE:
echo ========================================
dir /B dist\M3U_Matrix_Pro.exe
echo.
echo Size:
for %%A in (dist\M3U_Matrix_Pro.exe) do echo %%~zA bytes (%%~zA KB)
echo.
echo ✅ SINGLE EXECUTABLE ready at: dist\M3U_Matrix_Pro.exe
echo.
echo You can now:
echo 1. Run the exe directly (double-click)
echo 2. Copy it anywhere - it's completely standalone!
echo 3. No Python or DLLs needed!
echo.
pause