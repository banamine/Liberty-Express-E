#!/bin/bash

echo "========================================"
echo "     M3U MATRIX PRO - IPTV Manager"
echo "========================================"
echo ""
echo "Starting M3U Matrix Pro..."
echo ""

cd "$(dirname "$0")/../Applications"
python3 M3U_MATRIX_PRO.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start M3U Matrix Pro"
    echo "Please ensure Python 3 is installed"
    read -p "Press enter to continue..."
fi