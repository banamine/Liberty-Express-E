#!/usr/bin/env python3
"""
Video Player Pro - Launcher Script
Run this file to start the application
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main_launcher import main

if __name__ == "__main__":
    print("Starting Video Player Pro...")
    main()
