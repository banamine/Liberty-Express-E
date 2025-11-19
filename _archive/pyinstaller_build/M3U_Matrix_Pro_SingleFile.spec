# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for M3U Matrix Pro - SINGLE FILE VERSION
Creates a single standalone executable with all dependencies bundled
"""

block_cipher = None

import os
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
    
    # Icon (include in bundle)
    (os.path.join(project_root, 'logo.ico'), '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinterdnd2',
    'tkinterdnd2.tkdnd2',
    'PIL',
    'PIL._tkinter_finder',
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
]

a = Analysis(
    [os.path.join(project_root, 'src', 'videos', 'M3U_MATRIX_PRO.py')],
    pathex=[
        os.path.join(project_root, 'src'),
        os.path.join(project_root, 'src', 'videos'),
    ],
    binaries=[],
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

# Single-file executable with everything bundled
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Include all binaries
    a.zipfiles,  # Include all zip files
    a.datas,     # Include all data files
    [],
    name='M3U_Matrix_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'logo.ico'),
)