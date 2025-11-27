#!/bin/bash
# Gene Builder GUI Launcher
# Double-click this file to start the application

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Setup required!"
    echo "Please run setup.sh first"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment and run GUI
source venv/bin/activate
python3 src/gui.py

