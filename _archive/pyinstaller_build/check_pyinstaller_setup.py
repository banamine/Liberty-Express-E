#!/usr/bin/env python3
"""
Diagnostic script to check Python and PyInstaller compatibility
"""

import sys
import os
import subprocess
from pathlib import Path

print("="*60)
print("M3U MATRIX PRO - BUILD ENVIRONMENT CHECK")
print("="*60)

# Check Python version
python_version = sys.version_info
print(f"\n✓ Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version >= (3, 13):
    print("⚠️  WARNING: Python 3.13+ detected!")
    print("   PyInstaller may not fully support Python 3.13 yet")
    print("   Recommended: Use Python 3.11 or 3.12 for best compatibility")
elif python_version >= (3, 11) and python_version < (3, 13):
    print("✅ Python version is optimal for PyInstaller")
else:
    print("⚠️  Python version is older, but should work")

# Check PyInstaller
try:
    result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True)
    pyinstaller_version = result.stdout.strip()
    print(f"\n✓ PyInstaller Version: {pyinstaller_version}")
    
    # Parse version
    version_num = pyinstaller_version.split()[-1]
    major_version = int(version_num.split('.')[0])
    
    if major_version >= 6:
        print("✅ PyInstaller version is recent")
    else:
        print("⚠️  Consider upgrading PyInstaller: pip install --upgrade pyinstaller")
except FileNotFoundError:
    print("\n❌ PyInstaller not found!")
    print("   Install it: pip install pyinstaller")
except Exception as e:
    print(f"\n⚠️  Could not check PyInstaller: {e}")

# Check required packages
print("\n" + "="*60)
print("CHECKING REQUIRED PACKAGES")
print("="*60)

packages = ['tkinterdnd2', 'PIL', 'requests']
for package in packages:
    try:
        __import__(package)
        print(f"✅ {package} is installed")
    except ImportError:
        print(f"❌ {package} is NOT installed - run: pip install {package}")

# Check project structure
print("\n" + "="*60)
print("CHECKING PROJECT STRUCTURE")
print("="*60)

required_files = [
    'src/videos/M3U_MATRIX_PRO.py',
    'src/page_generator.py',
    'templates/nexus_tv_template.html',
    'logo.ico'
]

for file in required_files:
    if Path(file).exists():
        print(f"✅ {file} found")
    else:
        print(f"❌ {file} NOT FOUND")

# Recommendations
print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)

if python_version >= (3, 13):
    print("1. CRITICAL: Use Python 3.11 or 3.12 instead of 3.13")
    print("   Download from: https://www.python.org/downloads/release/python-3119/")
    print()
    print("2. After installing Python 3.11, create a virtual environment:")
    print("   python3.11 -m venv venv")
    print("   venv\\Scripts\\activate")
    print("   pip install pyinstaller tkinterdnd2 pillow requests")
else:
    print("1. Your Python version should work with PyInstaller")
    print("2. Make sure PyInstaller is updated: pip install --upgrade pyinstaller")
    print("3. Use the folder build (onedir) for better reliability")

print("\n" + "="*60)