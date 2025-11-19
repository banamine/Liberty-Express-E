#!/usr/bin/env python3
"""
Create the FINAL M3U Matrix Pro package with all security features.
Includes standalone secure player, URL hiding, and GitHub Pages support.
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime
import shutil

def create_final_package():
    """Create the final comprehensive package with all features"""
    
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
    zip_filename = f'M3U_MATRIX_SECURE_{timestamp}.zip'
    
    print("=" * 60)
    print("🔒 M3U MATRIX PRO - SECURE EDITION BUILDER")
    print("=" * 60)
    print(f"\n📦 Creating: {zip_filename}")
    print("\n🆕 NEW FEATURES INCLUDED:")
    print("  ✅ Standalone Secure Player (GitHub Pages ready)")
    print("  ✅ URL hiding - streams never displayed")
    print("  ✅ 20% chunked loading for large playlists")
    print("  ✅ Autoplay fixes with click-to-play overlay")
    print("  ✅ Stream Hub with HLS.js fixed")
    print("  ✅ Bulk Editor for batch operations")
    print("  ✅ Version Control System")
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
                        
                        # Clean up path
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
        
        # Create comprehensive installation instructions
        install_instructions = """M3U MATRIX PRO - SECURE EDITION
=====================================

WHAT'S NEW IN THIS VERSION:
---------------------------
🔒 STANDALONE SECURE PLAYER
• Completely self-contained HTML pages
• URLs hidden from display (security feature)
• 20% chunked loading for large playlists
• GitHub Pages ready for hosting
• Works offline once loaded

📦 GITHUB PAGES HOSTING
• Generate standalone pages
• Upload to GitHub repository
• Enable Pages in Settings
• Access at: username.github.io/repo/

✅ ALL AUTOPLAY ISSUES FIXED
• Videos start muted with click-to-play
• No more browser blocking errors
• Smooth playback experience

QUICK START:
-----------
1. Extract to any folder (e.g., C:\\M3U_Matrix\\)
2. Navigate to src\\videos\\
3. Run: python M3U_MATRIX_PRO.py

REQUIREMENTS:
------------
• Python 3.11 or 3.12 (NOT 3.13)
• Windows 10/11
• pip install -r requirements.txt

COMPLETE FEATURE SET:
--------------------
✅ M3U Matrix Pro (Desktop Application)
✅ Standalone Secure Player (NEW!)
✅ Stream Hub (Glass-morphism UI)
✅ Buffer TV (With numeric keypad)
✅ Multi-Channel Viewer (1-6 channels)
✅ Bulk Editor (Batch operations)
✅ Version Control System
✅ Redis Integration
✅ Rumble Browser & Channel
✅ Smart Scheduler
✅ All Player Templates

SECURITY FEATURES:
-----------------
• URLs never displayed in player interfaces
• Base64 encoding for playlist data
• Secure standalone pages for distribution
• No external CDN dependencies

Version: Secure Edition {date}
Built: {timestamp}

For support, see M3U_MATRIX_README.md
""".format(date=datetime.now().strftime('%Y-%m-%d'), 
           timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        # Add instructions to zip
        zipf.writestr('INSTALLATION.txt', install_instructions)
        
    # Calculate final size
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ SECURE PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📦 File: {zip_filename}")
    print(f"📊 Size: {size_mb:.2f} MB")
    print(f"📁 Total files: {files_added}")
    
    print("\n🔒 SECURITY FEATURES:")
    print("  ✓ URLs hidden from display")
    print("  ✓ Standalone secure player")
    print("  ✓ 20% chunked loading")
    print("  ✓ GitHub Pages ready")
    
    print("\n✨ ALL FEATURES INCLUDED:")
    print("  ✓ M3U Matrix Pro")
    print("  ✓ All player templates")
    print("  ✓ Autoplay fixes applied")
    print("  ✓ HLS.js library fixed")
    print("  ✓ Bulk Editor & Version Control")
    
    print("\n📥 TO DOWNLOAD:")
    print("  1. Find the file in Replit file browser")
    print(f"  2. Click the ⋮ menu next to {zip_filename}")
    print("  3. Select 'Download'")
    
    print("\n🚀 READY FOR INSTALLATION!")
    
    return zip_filename

if __name__ == "__main__":
    create_final_package()