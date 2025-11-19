# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for M3U Matrix Pro
Bundles Python application into standalone Windows executable
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
    
    # Icon
    (os.path.join(project_root, 'logo.ico'), '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinterdnd2',
    'PIL',
    'PIL._tkinter_finder',
    'requests',
    'urllib3',
    'certifi',
]

a = Analysis(
    [os.path.join(project_root, 'src', 'videos', 'M3U_MATRIX_PRO.py')],
    pathex=[
        os.path.join(project_root, 'src'),
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
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='M3U_Matrix_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'logo.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='M3U_Matrix_Pro',
)
