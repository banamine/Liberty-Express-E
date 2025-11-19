# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for M3U Matrix Pro - FIXED VERSION
Properly bundles Python runtime and all dependencies
"""

block_cipher = None

import os
import sys
from pathlib import Path

# Get project root (SPECPATH is the directory containing this .spec file)
project_root = os.path.abspath(SPECPATH)

# Data files to bundle
datas = [
    # Templates (all 6 generators)
    (os.path.join(project_root, 'templates', 'nexus_tv_template.html'), 'templates'),
    (os.path.join(project_root, 'templates', 'rumble_channel_template.html'), 'templates'),
    (os.path.join(project_root, 'templates', 'multi_channel_template.html'), 'templates'),
    (os.path.join(project_root, 'templates', 'buffer_tv_template.html'), 'templates'),
    (os.path.join(project_root, 'templates', 'simple_nexus_player.html'), 'templates'),
    (os.path.join(project_root, 'templates', 'web-iptv-extension'), 'templates/web-iptv-extension'),
    (os.path.join(project_root, 'templates', 'simple-player'), 'templates/simple-player'),
    
    # Data files
    (os.path.join(project_root, 'src', 'data', 'rumble_channels.json'), 'src/data'),
    
    # Icon
    (os.path.join(project_root, 'logo.ico'), '.'),
]

# Add Sample Playlists if they exist
sample_playlists_dir = os.path.join(project_root, 'Sample Playlists')
if os.path.exists(sample_playlists_dir):
    datas.append((sample_playlists_dir, 'Sample Playlists'))

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinterdnd2',
    'tkinterdnd2.tkdnd2',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'requests',
    'urllib3',
    'certifi',
    'json',
    'pathlib',
    'webbrowser',
    'datetime',
    'uuid',
    'socket',
    're',
    'threading',
    'queue',
    'os',
    'sys',
]

# Binaries - IMPORTANT: Include Python DLL explicitly
binaries = []

# Try to find and include Python DLL
python_dll = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
python_dll_path = os.path.join(sys.base_prefix, python_dll)
if os.path.exists(python_dll_path):
    binaries.append((python_dll_path, '.'))
    print(f"Including Python DLL: {python_dll}")

a = Analysis(
    [os.path.join(project_root, 'src', 'videos', 'M3U_MATRIX_PRO.py')],
    pathex=[
        os.path.join(project_root, 'src'),
        os.path.join(project_root, 'src', 'videos'),
        os.path.join(project_root),
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
        'test',
        '_test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Use folder distribution for better reliability
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='M3U_Matrix_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression to avoid issues
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'logo.ico') if os.path.exists(os.path.join(project_root, 'logo.ico')) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX compression
    upx_exclude=[],
    name='M3U_Matrix_Pro',
)