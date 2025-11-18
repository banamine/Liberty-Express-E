@echo off
REM Master build script - Creates BOTH FULL and LITE installers

echo ========================================
echo M3U MATRIX PRO - MASTER BUILD SCRIPT
echo ========================================
echo.
echo This will build:
echo  1. FULL Package (with samples)
echo  2. LITE Package (minimal size)
echo.
pause

REM Create installers directory
if not exist "installers" mkdir installers

REM Build FULL package
echo.
echo ========================================
echo BUILDING FULL PACKAGE...
echo ========================================
call build_installer_full.bat

if errorlevel 1 (
    echo.
    echo ERROR: FULL package build failed!
    pause
    exit /b 1
)

REM Build LITE package
echo.
echo ========================================
echo BUILDING LITE PACKAGE...
echo ========================================
call build_installer_lite.bat

if errorlevel 1 (
    echo.
    echo ERROR: LITE package build failed!
    pause
    exit /b 1
)

REM Summary
echo.
echo ========================================
echo ✅ ALL BUILDS COMPLETE!
echo ========================================
echo.
echo Output directory: installers\
echo.
dir /B installers\*.exe
echo.
echo ✅ Both FULL and LITE packages ready!
echo.
pause
