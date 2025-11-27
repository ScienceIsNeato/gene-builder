#!/bin/bash
# run_cli.sh
# ==========
# Command Line Interface for Gene Builder.
# Use this if you prefer typing commands over using the GUI.
#
# Usage: ./run_cli.sh GENE_SYMBOL
# Example: ./run_cli.sh lrfn1

if [ -z "$1" ]; then
    echo "❌ Missing gene symbol"
    echo "Usage: ./run_cli.sh GENE_SYMBOL"
    echo "Example: ./run_cli.sh lrfn1"
    exit 1
fi

cd "$(dirname "$0")"

# Check for environment
if [ ! -d "venv" ]; then
    echo "⚠️  Setup required! Run ./setup.sh first."
    exit 1
fi

# Activate environment and run the python script
source venv/bin/activate
python src/gene_to_genbank.py "$1" --canonical-only
