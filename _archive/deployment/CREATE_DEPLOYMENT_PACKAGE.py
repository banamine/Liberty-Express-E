#!/usr/bin/env python3
"""
M3U Matrix Deployment Package Creator
Creates a clean ZIP file with all essential files for deployment
Excludes unnecessary files like cache, logs, and temporary data
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
OUTPUT_NAME = "M3U_MATRIX_DEPLOYMENT_PACKAGE.zip"

INCLUDE_PATTERNS = [
    "src/**/*.py",
    "templates/**/*",
    "generated_pages/index.html",
    "*.bat",
    "*.py",
    "*.txt",
    "*.md",
    "requirements.txt",
    "package.json",
    "replit.md",
    "AUDIT_REPORT.txt",
    "README.md",
    "LICENSE",
]

EXCLUDE_FOLDERS = [
    "attached_assets",
    "backups",
    "cache",
    "logs",
    "temp",
    "__pycache__",
    ".git",
    ".replit",
    ".cache",
    ".local",
    ".venv",
    ".pythonlibs",
    ".upm",
    ".config",
    "node_modules",
    "dist",
    "build",
    "epg_data",
    "thumbnails",
    "exports",
    "redis",
    ".pytest_cache",
    "src/cache",
    "src/buffer",
    "src/logs",
    "src/exports",
    "src/generated_pages",
    "src/json",
    "src/tv_guide",
]

EXCLUDE_EXTENSIONS = [
    ".log",
    ".pyc",
    ".pyo",
    ".pyd",
    ".db",
    ".sqlite",
    ".tmp",
    ".cache",
    ".lock",
]

EXCLUDE_FILES = [
    "uv.lock",
    ".gitignore",
    ".env",
    ".DS_Store",
    "Thumbs.db",
    "M3U_MATRIX_DEPLOYMENT_PACKAGE.zip",
    "DEPLOYMENT_PACKAGE_CONTENTS.txt",
]


def should_include_file(file_path: Path, base_dir: Path) -> bool:
    """Determine if a file should be included in the deployment package"""
    
    relative_path = file_path.relative_to(base_dir)
    parts = relative_path.parts
    
    # Check if in excluded folder
    for excluded in EXCLUDE_FOLDERS:
        if excluded in parts:
            return False
    
    # Check if has excluded extension
    if file_path.suffix in EXCLUDE_EXTENSIONS:
        return False
    
    # Check if in excluded files list
    if file_path.name in EXCLUDE_FILES:
        return False
    
    # Exclude M3U playlist files in root (user data)
    if file_path.suffix in ['.m3u', '.m3u8'] and len(parts) == 1:
        return False
    
    return True


def create_deployment_package():
    """Create a deployment ZIP package with all essential files"""
    
    base_dir = Path.cwd()
    output_path = base_dir / OUTPUT_NAME
    
    print("=" * 70)
    print("M3U MATRIX DEPLOYMENT PACKAGE CREATOR")
    print("=" * 70)
    print(f"\nVersion: {VERSION}")
    print(f"Base Directory: {base_dir}")
    print(f"Output File: {output_path}")
    print("\nScanning files...")
    
    files_to_include = []
    total_size = 0
    
    # Walk through all files
    for file_path in base_dir.rglob("*"):
        if file_path.is_file() and should_include_file(file_path, base_dir):
            files_to_include.append(file_path)
            total_size += file_path.stat().st_size
    
    print(f"\nFound {len(files_to_include)} files to package")
    print(f"Total size: {total_size / (1024*1024):.2f} MB")
    
    # Create ZIP file
    print("\nCreating ZIP package...")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            arcname = str(file_path.relative_to(base_dir))
            
            # Create ZipInfo manually to handle files with timestamps before 1980
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Create ZipInfo with current timestamp (safe for ZIP format)
                zip_info = zipfile.ZipInfo(filename=arcname, date_time=datetime.now().timetuple()[:6])
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                
                # Write data using ZipInfo
                zipf.writestr(zip_info, data)
                print(f"  Added: {arcname}")
            except Exception as e:
                print(f"  ⚠️  Skipped {arcname}: {e}")
    
    final_size = output_path.stat().st_size
    print(f"\n✅ Package created successfully!")
    print(f"   File: {output_path}")
    print(f"   Size: {final_size / (1024*1024):.2f} MB")
    print(f"   Compression: {(1 - final_size/total_size)*100:.1f}%")
    
    # Create file list
    list_file = base_dir / "DEPLOYMENT_PACKAGE_CONTENTS.txt"
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("M3U MATRIX DEPLOYMENT PACKAGE CONTENTS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Files: {len(files_to_include)}\n")
        f.write(f"Package Size: {final_size / (1024*1024):.2f} MB\n\n")
        f.write("Files Included:\n")
        f.write("-" * 70 + "\n")
        
        for file_path in sorted(files_to_include):
            arcname = file_path.relative_to(base_dir)
            size = file_path.stat().st_size
            f.write(f"{arcname} ({size:,} bytes)\n")
    
    print(f"\n📋 File list saved to: {list_file}")
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT INSTRUCTIONS")
    print("=" * 70)
    print(f"""
1. Download {OUTPUT_NAME} to your PC
2. Extract to: N:\\Liberty-Express\\ (or any folder you choose)
3. Install Python 3.11+ from python.org
4. Open Command Prompt in the extracted folder
5. Run: pip install -r requirements.txt
6. Run: python src\\videos\\M3U_MATRIX_PRO.py

Or simply double-click: QUICK_INSTALL.bat (Windows)

For web player access:
- Double-click: START_WEB_SERVER.bat
- Open browser: http://localhost:5000/

See DEPLOYMENT_README.txt in the package for detailed instructions.
""")
    print("=" * 70)


if __name__ == "__main__":
    try:
        create_deployment_package()
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
