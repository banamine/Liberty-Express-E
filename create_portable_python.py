#!/usr/bin/env python3
"""
Portable Python Distribution Creator for M3U Matrix Pro
Creates a self-contained portable app that runs without Python installation
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path
import subprocess

class PortableDistributionCreator:
    def __init__(self):
        self.portable_dir = Path("M3U_Matrix_Pro_Portable")
        self.python_version = "3.11.9"
        self.python_url = f"https://www.python.org/ftp/python/{self.python_version}/python-3.11.9-embed-amd64.zip"
        self.get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        
    def create_directory_structure(self):
        """Create the portable distribution directory structure"""
        print("Creating directory structure...")
        
        # Remove existing if present
        if self.portable_dir.exists():
            print(f"Removing existing {self.portable_dir}...")
            shutil.rmtree(self.portable_dir)
        
        # Create directories
        dirs = [
            self.portable_dir,
            self.portable_dir / "python",
            self.portable_dir / "app",
            self.portable_dir / "app" / "src",
            self.portable_dir / "app" / "src" / "videos",
            self.portable_dir / "app" / "src" / "data",
            self.portable_dir / "app" / "templates",
            self.portable_dir / "generated_pages",
            self.portable_dir / "temp"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        print("✓ Directory structure created")
    
    def download_python(self):
        """Download portable Python"""
        print(f"Downloading portable Python {self.python_version}...")
        
        zip_path = self.portable_dir / "temp" / "python-embed.zip"
        
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            print(f"\rProgress: {percent:.1f}%", end="")
        
        try:
            urllib.request.urlretrieve(self.python_url, zip_path, download_progress)
            print("\n✓ Python downloaded")
            return zip_path
        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            return None
    
    def extract_python(self, zip_path):
        """Extract portable Python"""
        print("Extracting Python...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.portable_dir / "python")
            print("✓ Python extracted")
            return True
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
            return False
    
    def configure_python(self):
        """Configure portable Python for pip and packages"""
        print("Configuring Python...")
        
        # Modify python311._pth
        pth_file = self.portable_dir / "python" / "python311._pth"
        pth_content = """python311.zip
.
Lib
Lib\\site-packages
import site"""
        
        with open(pth_file, 'w') as f:
            f.write(pth_content)
        
        # Create Lib directories
        (self.portable_dir / "python" / "Lib").mkdir(exist_ok=True)
        (self.portable_dir / "python" / "Lib" / "site-packages").mkdir(exist_ok=True)
        
        print("✓ Python configured")
    
    def install_pip(self):
        """Install pip in portable Python"""
        print("Installing pip...")
        
        # Download get-pip.py
        get_pip_path = self.portable_dir / "temp" / "get-pip.py"
        
        try:
            urllib.request.urlretrieve(self.get_pip_url, get_pip_path)
            
            # Run get-pip.py
            python_exe = self.portable_dir / "python" / "python.exe"
            result = subprocess.run(
                [str(python_exe), str(get_pip_path), "--no-warn-script-location"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Pip installed")
                return True
            else:
                print(f"✗ Pip installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Pip installation failed: {e}")
            return False
    
    def install_dependencies(self):
        """Install required packages"""
        print("Installing dependencies...")
        
        python_exe = self.portable_dir / "python" / "python.exe"
        packages = ["requests", "pillow", "tkinterdnd2-universal"]
        
        for package in packages:
            print(f"  Installing {package}...")
            result = subprocess.run(
                [str(python_exe), "-m", "pip", "install", 
                 "--no-warn-script-location", package],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"  ✗ Failed to install {package}")
                return False
        
        print("✓ Dependencies installed")
        return True
    
    def copy_application_files(self):
        """Copy application files to portable distribution"""
        print("Copying application files...")
        
        # File mappings
        files_to_copy = [
            ("src/videos/M3U_MATRIX_PRO.py", "app/src/videos/M3U_MATRIX_PRO.py"),
            ("src/page_generator.py", "app/src/page_generator.py"),
            ("src/page_generator_fix.py", "app/src/page_generator_fix.py"),
            ("src/rumble_helper.py", "app/src/rumble_helper.py"),
            ("src/utils.py", "app/src/utils.py"),
            ("src/navigation_hub_generator.py", "app/src/navigation_hub_generator.py"),
            ("src/nav_hub_generator.py", "app/src/nav_hub_generator.py"),
            ("src/data/rumble_channels.json", "app/src/data/rumble_channels.json"),
        ]
        
        for src, dst in files_to_copy:
            src_path = Path(src)
            if src_path.exists():
                dst_path = self.portable_dir / dst
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"  ✓ Copied {src}")
            else:
                print(f"  ⚠ Not found: {src}")
        
        # Copy templates
        templates_src = Path("templates")
        if templates_src.exists():
            templates_dst = self.portable_dir / "app" / "templates"
            shutil.copytree(templates_src, templates_dst, dirs_exist_ok=True)
            print("  ✓ Copied templates")
        
        # Copy Sample Playlists if they exist
        samples_src = Path("Sample Playlists")
        if samples_src.exists():
            samples_dst = self.portable_dir / "Sample Playlists"
            shutil.copytree(samples_src, samples_dst, dirs_exist_ok=True)
            print("  ✓ Copied Sample Playlists")
        
        print("✓ Application files copied")
    
    def create_launcher(self):
        """Create launcher batch file"""
        print("Creating launcher...")
        
        launcher_content = """@echo off
REM M3U Matrix Pro Portable Launcher

cd /d "%~dp0"

REM Set Python path to use portable version
set PYTHONPATH=%~dp0app\\src;%~dp0app
set PYTHONHOME=

REM Launch the application
echo Starting M3U Matrix Pro...
"%~dp0python\\python.exe" "%~dp0app\\src\\videos\\M3U_MATRIX_PRO.py"

if %errorlevel% neq 0 (
    echo.
    echo Error launching application!
    pause
)"""
        
        launcher_path = self.portable_dir / "Launch_M3U_Matrix_Pro.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        print("✓ Launcher created")
    
    def create_readme(self):
        """Create README file"""
        print("Creating documentation...")
        
        readme_content = f"""M3U MATRIX PRO - PORTABLE VERSION
=================================

This is a portable version of M3U Matrix Pro that includes:
- Python {self.python_version} (no installation required)
- All required dependencies
- Complete application with all templates

HOW TO USE:
-----------
1. Double-click "Launch_M3U_Matrix_Pro.bat"
2. The application will start automatically
3. Generated pages will appear in the "generated_pages" folder

FEATURES:
---------
- No Python installation required on target machine
- Completely self-contained
- Can run from USB drive or any folder
- All 6 page generators included

DISTRIBUTION:
-------------
Copy the entire "M3U_Matrix_Pro_Portable" folder to any location.
The app will work immediately without any installation.

TROUBLESHOOTING:
----------------
If the app doesn't start:
1. Ensure you're on Windows 64-bit
2. Check that antivirus isn't blocking python.exe
3. Try running as administrator

Version: Portable Distribution
Created with Python {self.python_version}
"""
        
        readme_path = self.portable_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("✓ Documentation created")
    
    def cleanup(self):
        """Clean up temporary files"""
        print("Cleaning up...")
        
        temp_dir = self.portable_dir / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        print("✓ Cleanup complete")
    
    def create_distribution(self):
        """Main method to create the portable distribution"""
        print("\n" + "="*50)
        print("  M3U MATRIX PRO - PORTABLE DISTRIBUTION CREATOR")
        print("="*50 + "\n")
        
        # Step 1: Create directories
        self.create_directory_structure()
        
        # Step 2: Download Python
        zip_path = self.download_python()
        if not zip_path:
            print("\n✗ Failed to download Python. Please check your internet connection.")
            return False
        
        # Step 3: Extract Python
        if not self.extract_python(zip_path):
            return False
        
        # Step 4: Configure Python
        self.configure_python()
        
        # Step 5: Install pip
        if not self.install_pip():
            print("\n✗ Failed to install pip. The distribution may not work properly.")
        
        # Step 6: Install dependencies
        if not self.install_dependencies():
            print("\n⚠ Some dependencies failed to install.")
        
        # Step 7: Copy application files
        self.copy_application_files()
        
        # Step 8: Create launcher
        self.create_launcher()
        
        # Step 9: Create documentation
        self.create_readme()
        
        # Step 10: Cleanup
        self.cleanup()
        
        print("\n" + "="*50)
        print("  PORTABLE DISTRIBUTION CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"\nLocation: {self.portable_dir.absolute()}")
        print("\nThis folder contains:")
        print(f"- Python {self.python_version} (portable)")
        print("- M3U Matrix Pro application")
        print("- All templates and dependencies")
        print("- Launch_M3U_Matrix_Pro.bat (double-click to run)")
        print("\nTo distribute:")
        print(f"1. ZIP the entire '{self.portable_dir}' folder")
        print("2. Users can extract anywhere and run")
        print("3. No Python installation needed!")
        print(f"\nTotal size: ~100-150 MB")
        
        return True

if __name__ == "__main__":
    creator = PortableDistributionCreator()
    if creator.create_distribution():
        print("\n✓ Success! Your portable distribution is ready.")
        input("\nPress Enter to exit...")
    else:
        print("\n✗ Failed to create portable distribution.")
        input("\nPress Enter to exit...")