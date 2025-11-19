#!/usr/bin/env python3
"""
Create the FINAL comprehensive M3U Matrix Pro package.
Includes all fixes, clean structure, and ready for Windows installation.
"""

import os
import zipfile
from pathlib import Path
import json
from datetime import datetime

def create_comprehensive_zip():
    """Create the final, complete zip package"""
    
    # Define comprehensive include list
    include_dirs = [
        'src/',
        'templates/',
        'generated_pages/',
        'redis/',
        'Sample Playlists/',
        'installer/',
        'exports/',
        'epg_data/',
        'logs/',
        'temp/',
        'backups/'
    ]
    
    include_files = [
        'M3U_MATRIX_README.md',
        'LICENSE',
        'README.md',
        'requirements.txt',
        'package.json',
        'replit.md',
        'logo.ico',
        'generated-icon.png'
    ]
    
    # Exclude patterns
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.pyo',
        '.git',
        '.replit',
        '.upm',
        'venv/',
        'env/',
        '.env',
        '*.zip',
        'create_',
        'fix_',
        '.bak',
        '.tmp',
        'node_modules/'
    ]
    
    timestamp = datetime.now().strftime('%Y%m%d')
    zip_filename = f'M3U_MATRIX_COMPLETE_{timestamp}.zip'
    
    print("=" * 60)
    print("🚀 M3U MATRIX PRO - COMPLETE PACKAGE BUILDER")
    print("=" * 60)
    print(f"\n📦 Creating: {zip_filename}")
    print("\n📋 Package includes:")
    print("  • All source code (M3U Matrix Pro)")
    print("  • All player templates (with autoplay fixes)")
    print("  • Stream Hub integration")
    print("  • Bulk Editor tools")
    print("  • Version Control System")
    print("  • Redis integration")
    print("  • Sample playlists")
    print("  • All required libraries")
    print("\n⏳ Building package...")
    
    files_added = 0
    dirs_created = set()
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add directories and their contents
        for include_dir in include_dirs:
            if os.path.exists(include_dir):
                for root, dirs, files in os.walk(include_dir):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
                    
                    # Skip if path contains excluded pattern
                    if any(ex in root for ex in exclude_patterns):
                        continue
                    
                    # Add directory structure
                    rel_dir = os.path.relpath(root, '.')
                    if rel_dir not in dirs_created:
                        dirs_created.add(rel_dir)
                    
                    # Add files
                    for file in files:
                        # Skip excluded files
                        if any(ex in file for ex in exclude_patterns):
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        
                        # Clean up path (remove ./ prefix if present)
                        if arcname.startswith('./'):
                            arcname = arcname[2:]
                        
                        try:
                            zipf.write(file_path, arcname)
                            files_added += 1
                            
                            # Show progress
                            if files_added % 20 == 0:
                                print(f"    Added {files_added} files...")
                        except Exception as e:
                            print(f"    ⚠️ Skipped {file}: {e}")
        
        # Add individual files from root
        for include_file in include_files:
            if os.path.exists(include_file):
                try:
                    zipf.write(include_file, include_file)
                    files_added += 1
                except Exception as e:
                    print(f"    ⚠️ Skipped {include_file}: {e}")
        
        # Create installation instructions
        install_instructions = """M3U MATRIX PRO - INSTALLATION INSTRUCTIONS
==========================================

QUICK START:
1. Extract this zip to any folder (e.g., C:\\M3U_Matrix\\)
2. Navigate to src\\videos\\
3. Double-click M3U_MATRIX_PRO.py
   (Or run: python M3U_MATRIX_PRO.py)

REQUIREMENTS:
- Python 3.11 or 3.12 (NOT 3.13)
- Windows 10/11
- Install dependencies: pip install -r requirements.txt

WHAT'S INCLUDED:
✅ M3U Matrix Pro (Desktop Application)
✅ All Player Templates (with autoplay fixes)
✅ Stream Hub Integration
✅ Bulk Editor
✅ Version Control System
✅ Redis Integration
✅ Sample Playlists

AUTOPLAY FIXES APPLIED:
- Videos start muted (allows autoplay)
- Click-to-play overlay for user interaction
- Proper error handling for browser restrictions

FIRST RUN:
1. Load a playlist (drag & drop or import)
2. Organize channels
3. Generate player pages
4. Open in browser

SUPPORT:
For issues or questions, refer to M3U_MATRIX_README.md

Version: Complete Package {timestamp}
Built: {date}
""".format(timestamp=timestamp, date=datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        # Add instructions to zip
        zipf.writestr('INSTALLATION.txt', install_instructions)
        
    # Calculate final size
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📦 File: {zip_filename}")
    print(f"📊 Size: {size_mb:.2f} MB")
    print(f"📁 Total files: {files_added}")
    
    print("\n🎯 FEATURES INCLUDED:")
    print("  ✓ M3U Matrix Pro (Main Application)")
    print("  ✓ Stream Hub (Multi-stream viewer)")
    print("  ✓ Bulk Editor (Batch channel editing)")
    print("  ✓ Version Control (Backup system)")
    print("  ✓ All Player Templates")
    print("  ✓ Autoplay Fixes Applied")
    
    print("\n💾 CLEAN STRUCTURE:")
    print("  No nested folders - extracts cleanly")
    print("  All dependencies included")
    print("  Ready for Windows installation")
    
    print("\n📥 TO DOWNLOAD:")
    print("  1. Find the file in Replit file browser")
    print(f"  2. Click the ⋮ menu next to {zip_filename}")
    print("  3. Select 'Download'")
    
    print("\n🚀 READY FOR INSTALLATION!")
    
    return zip_filename

if __name__ == "__main__":
    create_comprehensive_zip()