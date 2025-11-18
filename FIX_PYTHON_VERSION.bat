@echo off
REM =========================================
REM  PYTHON VERSION FIX FOR M3U MATRIX PRO
REM =========================================
color 0E
cls

echo.
echo =====================================================
echo   M3U MATRIX PRO - PYTHON VERSION FIX
echo =====================================================
echo.
echo CRITICAL: Python 3.13 is NOT supported by PyInstaller!
echo You MUST use Python 3.11 or 3.12 for successful builds.
echo.
echo Current Issue:
echo - Your system has Python 3.13 (python313.dll error)
echo - PyInstaller cannot bundle Python 3.13 properly
echo - This causes "Failed to load Python DLL" errors
echo.
pause

echo.
echo =====================================================
echo   REQUIRED STEPS TO FIX:
echo =====================================================
echo.
echo 1. DOWNLOAD Python 3.11.9 (Recommended):
echo    https://www.python.org/downloads/release/python-3119/
echo    - Choose: Windows installer (64-bit)
echo    - During install: Check "Add Python to PATH"
echo.
echo 2. CREATE NEW VIRTUAL ENVIRONMENT:
echo    python -m venv venv_py311
echo    venv_py311\Scripts\activate
echo.
echo 3. INSTALL DEPENDENCIES:
echo    pip install --upgrade pip
echo    pip install pyinstaller==6.4
echo    pip install tkinterdnd2 pillow requests
echo.
echo 4. VERIFY VERSIONS:
echo    python --version
echo    (Should show: Python 3.11.9)
echo.
echo 5. BUILD THE EXECUTABLE:
echo    pyinstaller --clean M3U_Matrix_Pro_Fixed.spec
echo.
pause

echo.
echo =====================================================
echo   CHECKING YOUR CURRENT PYTHON VERSION...
echo =====================================================
echo.

python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
) else (
    echo.
    echo If this shows Python 3.13.x, you MUST downgrade!
)

echo.
echo =====================================================
echo   CHECKING PYINSTALLER VERSION...
echo =====================================================
echo.

pip show pyinstaller 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed
) else (
    echo.
    echo PyInstaller found (check version above)
)

echo.
echo =====================================================
echo.
echo Press any key to open Python 3.11 download page...
pause >nul

start https://www.python.org/downloads/release/python-3119/

echo.
echo After installing Python 3.11:
echo 1. Close this window
echo 2. Open a NEW command prompt
echo 3. Run: build_with_py311.bat
echo.
pause