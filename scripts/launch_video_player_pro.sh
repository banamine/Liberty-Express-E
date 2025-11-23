#!/bin/bash

echo "========================================"
echo "  VIDEO PLAYER PRO - Media Workbench"
echo "========================================"
echo ""
echo "Starting Video Player Pro..."
echo ""

cd "$(dirname "$0")/../Applications"
python3 VIDEO_PLAYER_PRO.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start Video Player Pro"
    echo "Please ensure Python 3 is installed"
    read -p "Press enter to continue..."
fi