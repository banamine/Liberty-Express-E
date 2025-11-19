@echo off
REM ====================================
REM  TEST PORTABLE DISTRIBUTION
REM ====================================
color 0E
cls

echo.
echo ====================================
echo   PORTABLE DISTRIBUTION TESTER
echo ====================================
echo.

REM Check if portable directory exists
if not exist "M3U_Matrix_Pro_Portable" (
    echo ERROR: Portable distribution not found!
    echo.
    echo Please run one of these first:
    echo   - create_portable_distribution.bat
    echo   - python create_portable_python.py
    echo.
    pause
    exit /b 1
)

echo Checking portable distribution components...
echo.

set ERRORS=0

REM Check Python
if exist "M3U_Matrix_Pro_Portable\python\python.exe" (
    echo [OK] Python executable found
) else (
    echo [ERROR] Python executable not found!
    set /a ERRORS+=1
)

REM Check main application
if exist "M3U_Matrix_Pro_Portable\app\src\videos\M3U_MATRIX_PRO.py" (
    echo [OK] Main application found
) else (
    echo [ERROR] Main application not found!
    set /a ERRORS+=1
)

REM Check launcher
if exist "M3U_Matrix_Pro_Portable\Launch_M3U_Matrix_Pro.bat" (
    echo [OK] Launcher found
) else (
    echo [ERROR] Launcher not found!
    set /a ERRORS+=1
)

REM Check templates
if exist "M3U_Matrix_Pro_Portable\app\templates" (
    echo [OK] Templates folder found
    dir /b "M3U_Matrix_Pro_Portable\app\templates" | findstr /r "." >nul
    if %errorlevel% equ 0 (
        echo [OK] Templates present
    ) else (
        echo [WARNING] Templates folder empty
        set /a ERRORS+=1
    )
) else (
    echo [ERROR] Templates folder not found!
    set /a ERRORS+=1
)

REM Check dependencies
echo.
echo Testing Python dependencies...
"M3U_Matrix_Pro_Portable\python\python.exe" -c "import sys; print(f'Python: {sys.version}')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not working!
    set /a ERRORS+=1
) else (
    echo [OK] Python working
)

"M3U_Matrix_Pro_Portable\python\python.exe" -c "import tkinter; print('[OK] Tkinter available')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Tkinter not available!
    set /a ERRORS+=1
)

"M3U_Matrix_Pro_Portable\python\python.exe" -c "import requests; print('[OK] Requests installed')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Requests not installed
)

"M3U_Matrix_Pro_Portable\python\python.exe" -c "import PIL; print('[OK] Pillow installed')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Pillow not installed
)

echo.
echo ====================================
echo   TEST RESULTS
echo ====================================
echo.

if %ERRORS% equ 0 (
    echo SUCCESS! All checks passed.
    echo.
    echo Your portable distribution is ready to use!
    echo.
    echo Would you like to test launch the application?
    choice /c YN /m "Launch M3U Matrix Pro now"
    if errorlevel 2 goto :end
    if errorlevel 1 goto :launch
) else (
    echo PROBLEMS FOUND: %ERRORS% issue(s) detected
    echo.
    echo Please review the errors above and rebuild if necessary.
)
goto :end

:launch
echo.
echo Launching M3U Matrix Pro...
cd M3U_Matrix_Pro_Portable
call Launch_M3U_Matrix_Pro.bat
cd ..

:end
echo.
pause