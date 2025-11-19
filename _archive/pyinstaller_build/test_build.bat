@echo off
REM Test the built application

echo ========================================
echo TESTING M3U MATRIX PRO BUILD
echo ========================================
echo.

if exist "dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe" (
    echo Starting M3U Matrix Pro...
    echo.
    echo If the app opens successfully, the build works!
    echo If you get errors, note them down.
    echo.
    cd dist\M3U_Matrix_Pro
    start M3U_Matrix_Pro.exe
    cd ..\..
) else (
    echo ❌ No build found!
    echo.
    echo Run build_fixed.bat first
)

pause