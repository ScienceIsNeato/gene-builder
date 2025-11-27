#!/bin/bash
# START_GUI.command
# =================
# This file is a macOS shortcut. Double-clicking it opens a Terminal window
# and launches the Gene Builder Graphical Interface.

cd "$(dirname "$0")"

# Check if setup.sh has been run
if [ ! -d "venv" ]; then
    echo "⚠️  First Time Setup Required!"
    echo "Please run './setup.sh' first to install the necessary tools."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# 1. Activate the isolated Python environment
source venv/bin/activate

# 2. Set Tcl/Tk paths for the portable python
# This is critical because the portable build expects hardcoded paths
REPO_ROOT="$(pwd)"
export TCL_LIBRARY="$REPO_ROOT/.local_python/lib/tcl8.6"
export TK_LIBRARY="$REPO_ROOT/.local_python/lib/tk8.6"

# 3. Launch the GUI program
python3 src/gui.py
