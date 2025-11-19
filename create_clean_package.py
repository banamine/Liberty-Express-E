#!/usr/bin/env python3
"""
Create a clean zip package of M3U Matrix Pro without nested folder paths.
This version zips the contents directly, preventing Liberty-Express-/Liberty-Express-/ duplication.
"""

import os
import zipfile
from pathlib import Path
import shutil

def create_clean_zip():
    """Create a zip file with proper structure (no nested folders)"""
    
    # Define what to include
    include_patterns = [
        'src/',
        'templates/',
        'generated_pages/',
        'redis/',
        'Sample Playlists/',
        'M3U_MATRIX_README.md',
        'LICENSE',
        '*.py'  # Top level Python files
    ]
    
    # Define what to exclude
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
        '*.zip',  # Don't include other zip files
        'create_clean_package.py',  # Don't include this script
        'fix_autoplay_issues.py'  # Don't include fix scripts
    ]
    
    zip_filename = 'M3U_MATRIX_AUTOPLAY_FIXED.zip'
    
    print(f"📦 Creating clean package: {zip_filename}")
    print("=" * 50)
    
    # Create new zip file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        files_added = 0
        
        # Walk through current directory
        for root, dirs, files in os.walk('.'):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
            
            # Convert to Path for easier handling
            root_path = Path(root)
            
            # Skip if root matches exclude pattern
            if any(ex in str(root_path) for ex in exclude_patterns):
                continue
            
            # Check if this path should be included
            should_include = False
            for pattern in include_patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    if str(root_path).startswith('./' + pattern) or str(root_path).startswith(pattern):
                        should_include = True
                        break
                else:
                    # File pattern  
                    if root == '.':
                        should_include = True
                        break
            
            if not should_include and root != '.':
                continue
            
            for file in files:
                # Skip excluded files
                if any(ex in file for ex in exclude_patterns):
                    continue
                
                file_path = root_path / file
                
                # For root directory files, check if they match include patterns
                if root == '.':
                    matched = False
                    for pattern in include_patterns:
                        if not pattern.endswith('/'):
                            if pattern.startswith('*'):
                                if file.endswith(pattern[1:]):
                                    matched = True
                                    break
                            elif file == pattern:
                                matched = True
                                break
                    if not matched:
                        continue
                
                # Calculate the archive name (remove leading ./)
                if str(file_path).startswith('./'):
                    arcname = str(file_path)[2:]
                else:
                    arcname = str(file_path)
                
                # Add file to zip
                zipf.write(file_path, arcname)
                files_added += 1
                
                # Show progress for key files
                if files_added % 10 == 0:
                    print(f"  Added {files_added} files...")
        
        print(f"\n✅ Package created successfully!")
        print(f"📊 Total files added: {files_added}")
    
    # Get file size
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print(f"📦 Package size: {size_mb:.2f} MB")
    print(f"📁 File: {zip_filename}")
    
    print("\n🎯 AUTOPLAY FIXES INCLUDED:")
    print("  ✓ Videos start muted (allows autoplay)")
    print("  ✓ Click-to-play overlay added")
    print("  ✓ Proper error handling for blocked autoplay")
    
    print("\n💾 Package Structure (when extracted):")
    print("  YourFolder/")
    print("    ├── src/")
    print("    ├── templates/ (with autoplay fixes)")
    print("    ├── generated_pages/")
    print("    ├── redis/")
    print("    ├── Sample Playlists/")
    print("    └── ... (all project files)")
    
    return zip_filename

if __name__ == "__main__":
    create_clean_zip()