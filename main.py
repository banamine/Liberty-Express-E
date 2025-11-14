#!/usr/bin/env python3
"""
M3U Matrix Pro - Main Launcher
Launches the M3U Matrix Pro application
"""

import os
import sys

# Change to src directory where the app is located
os.chdir('src')

# Import and run the application
try:
    from M3U_MATRIX_PRO import M3UMatrix
    print("✅ M3U Matrix Pro launched successfully!")
except Exception as e:
    print(f"❌ Error launching M3U Matrix Pro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
