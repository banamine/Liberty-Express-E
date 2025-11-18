@echo off
REM =============================================
REM  BUILD WITH PYTHON 3.11 - COMPLETE SOLUTION
REM =============================================
color 0A
cls

echo.
echo =====================================================
echo   M3U MATRIX PRO - BUILD WITH PYTHON 3.11
echo =====================================================
echo.

REM Step 1: Create virtual environment with Python 3.11
echo Step 1: Creating Python 3.11 virtual environment...
echo -----------------------------------------------
py -3.11 -m venv venv_py311 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11 not found!
    echo.
    echo Please install Python 3.11 first:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

REM Step 2: Activate virtual environment
echo Step 2: Activating virtual environment...
echo -----------------------------------------------
call venv_py311\Scripts\activate.bat

REM Step 3: Verify Python version
echo.
echo Step 3: Verifying Python version...
echo -----------------------------------------------
python --version
echo.

REM Step 4: Upgrade pip
echo Step 4: Upgrading pip...
echo -----------------------------------------------
python -m pip install --upgrade pip
echo.

REM Step 5: Install required packages
echo Step 5: Installing required packages...
echo -----------------------------------------------
pip install pyinstaller==6.4
pip install tkinterdnd2
pip install pillow
pip install requests
echo.

REM Step 6: Verify PyInstaller installation
echo Step 6: Verifying PyInstaller...
echo -----------------------------------------------
pyinstaller --version
echo.

REM Step 7: Clean previous build artifacts
echo Step 7: Cleaning previous build artifacts...
echo -----------------------------------------------
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.toc del *.toc
echo Build folders cleaned!
echo.

REM Step 8: Run PyInstaller with the fixed spec
echo Step 8: Building M3U Matrix Pro executable...
echo -----------------------------------------------
pyinstaller --clean --noconfirm M3U_Matrix_Pro_Fixed.spec

echo.
echo =====================================================
echo   BUILD COMPLETE!
echo =====================================================
echo.

REM Check if build was successful
if exist "dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe" (
    echo SUCCESS! Executable created at:
    echo dist\M3U_Matrix_Pro\M3U_Matrix_Pro.exe
    echo.
    echo The folder contains:
    dir /b "dist\M3U_Matrix_Pro\*.exe"
    dir /b "dist\M3U_Matrix_Pro\*.dll" | findstr python
    echo.
    echo You can now:
    echo 1. Copy the entire 'dist\M3U_Matrix_Pro' folder to any location
    echo 2. Run M3U_Matrix_Pro.exe from there
    echo 3. Generated pages will appear in 'generated_pages' next to the exe
    echo.
    echo Press any key to open the output folder...
    pause >nul
    explorer "dist\M3U_Matrix_Pro"
) else (
    echo BUILD FAILED!
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo - Wrong Python version (must be 3.11 or 3.12)
    echo - Missing dependencies
    echo - Antivirus blocking PyInstaller
    echo.
    pause
)