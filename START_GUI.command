#!/bin/bash
# START_GUI.command
# =================
# This file is a macOS shortcut. Double-clicking it opens a Terminal window
# and launches the Gene Builder Graphical Interface.
#
# It does exactly the same thing as running "python3 src/gui.py" manually,
# but sets up the environment for you first.

cd "$(dirname "$0")"

# Check if setup.sh has been run
if [ ! -d "venv" ]; then
    echo "⚠️  First Time Setup Required!"
    echo "Please run './setup.sh' first to install the necessary tools."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# 1. Activate the isolated Python environment (so we use our working python, not the system's)
source venv/bin/activate

# 2. Launch the GUI program
python3 src/gui.py
