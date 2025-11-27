#!/bin/bash
# Gene Builder Setup Script
# One-click setup for Mac users

set -e  # Exit on error

echo "🧬 Gene Builder - Setup Script"
echo "================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Installing dependencies..."
source venv/bin/activate

# Upgrade pip quietly
pip install --upgrade pip --quiet

# Install requirements
pip install -r requirements.txt --quiet

echo "✓ Dependencies installed"
echo ""

# Create output directory
mkdir -p output
echo "✓ Output directory ready"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "   ./extract_gene.sh GENE_SYMBOL"
echo ""
echo "Example:"
echo "   ./extract_gene.sh lrfn1"
echo ""
echo "See START_HERE.md for more info"
echo ""

