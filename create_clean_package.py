#!/usr/bin/env python3
"""
Create a clean zip package of M3U Matrix Pro without duplicate folder nesting.
This script creates a zip file that extracts cleanly without creating duplicate paths.
"""

import os
import zipfile
from pathlib import Path
import shutil
import datetime

def create_clean_zip():
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Create archive directory if it doesn't exist
    archive_dir = project_root / "_archive"
    archive_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"M3U_MATRIX_ALL_IN_ONE_{timestamp}.zip"
    zip_path = archive_dir / zip_filename
    
    # Files and folders to include in the package
    include_items = [
        "src",
        "templates", 
        "redis",
        "Sample Playlists",
        "generated_pages",
        "M3U_MATRIX_README.md",
        "replit.md",
        "README.md",
        ".replit",
        "replit.nix",
        ".gitignore"
    ]
    
    # Files/folders to exclude
    exclude_patterns = [
        "__pycache__",
        ".pyc",
        ".pyo",
        ".pyd",
        ".db",
        ".sqlite",
        ".log",
        "logs/",
        "_archive/",
        ".git/",
        "venv/",
        "env/",
        ".env",
        ".venv",
        "node_modules/",
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.bak",
        "~*"
    ]
    
    def should_exclude(path):
        """Check if a path should be excluded"""
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
            if pattern.endswith('/') and pattern[:-1] in path.parts:
                return True
        return False
    
    print("🎁 Creating clean M3U Matrix All-In-One package...")
    print(f"📦 Output: {zip_path}")
    
    # Create the zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        
        for item_name in include_items:
            item_path = project_root / item_name
            
            if not item_path.exists():
                print(f"⚠️  Skipping {item_name} (not found)")
                continue
                
            if item_path.is_file():
                # Add single file directly to zip root
                if not should_exclude(item_path):
                    zipf.write(item_path, item_path.name)
                    file_count += 1
                    print(f"  ✓ Added {item_name}")
            
            elif item_path.is_dir():
                # Add directory contents
                added_dirs = set()
                for root, dirs, files in os.walk(item_path):
                    root_path = Path(root)
                    
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
                    
                    # Calculate the archive path relative to project root
                    rel_path = root_path.relative_to(project_root)
                    
                    # Add directory structure
                    if str(rel_path) not in added_dirs and not should_exclude(root_path):
                        added_dirs.add(str(rel_path))
                    
                    # Add files
                    for file in files:
                        file_path = root_path / file
                        if not should_exclude(file_path):
                            arc_name = file_path.relative_to(project_root)
                            zipf.write(file_path, arc_name)
                            file_count += 1
                
                print(f"  ✓ Added {item_name}/ ({len(added_dirs)} folders)")
    
    # Get file size
    file_size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "="*50)
    print("✅ PACKAGE CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"📦 File: {zip_filename}")
    print(f"📁 Location: {zip_path}")
    print(f"📊 Size: {file_size_mb:.2f} MB")
    print(f"📋 Files: {file_count} files included")
    print("\n🎯 CLEAN EXTRACTION GUARANTEED:")
    print("   When you extract this zip, you'll get:")
    print("   📂 YourFolder/")
    print("      ├── src/")
    print("      ├── templates/")
    print("      ├── generated_pages/")
    print("      └── ... (all project files)")
    print("\n   NO duplicate nested folders!")
    
    # Also create a simpler named copy for easy download
    simple_name = "M3U_MATRIX_CLEAN.zip"
    simple_path = project_root / simple_name
    shutil.copy2(zip_path, simple_path)
    print(f"\n📥 Easy download copy: {simple_name}")
    
    return zip_path, simple_path

if __name__ == "__main__":
    try:
        archive_path, download_path = create_clean_zip()
        print("\n✨ Package ready for distribution!")
        print(f"💾 Download the file: M3U_MATRIX_CLEAN.zip")
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        import traceback
        traceback.print_exc()