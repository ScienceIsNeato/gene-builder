#!/bin/bash
# Gene Builder Setup Script
# Downloads a standalone Python to ensure everything (including GUI) works perfectly.

set -e

echo "🧬 Gene Builder - Setup"
echo "========================"

# 1. Determine Architecture
ARCH=$(uname -m)
OS=$(uname -s)

if [[ "$OS" != "Darwin" ]]; then
    echo "❌ This script is for macOS only."
    exit 1
fi

# Python Build Standalone Release (20240224)
# Using 3.10 as it's extremely stable
PBS_RELEASE="20240224"
PBS_VERSION="3.10.13"

if [[ "$ARCH" == "arm64" ]]; then
    # Apple Silicon
    URL="https://github.com/indygreg/python-build-standalone/releases/download/$PBS_RELEASE/cpython-$PBS_VERSION+20240224-aarch64-apple-darwin-install_only.tar.gz"
else
    # Intel Mac
    URL="https://github.com/indygreg/python-build-standalone/releases/download/$PBS_RELEASE/cpython-$PBS_VERSION+20240224-x86_64-apple-darwin-install_only.tar.gz"
fi

# 2. Download and Install Portable Python
if [ ! -d ".local_python" ]; then
    echo "📦 Downloading standalone Python (ensures GUI works)..."
    echo "   URL: $URL"
    curl -L -o python.tar.gz "$URL" --progress-bar
    
    echo "📦 Extracting..."
    tar -xzf python.tar.gz
    mv python .local_python
    rm python.tar.gz
    echo "✓ Python installed locally to .local_python/"
else
    echo "✓ Local Python already present"
fi

# 3. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    # Use our local python to create the venv
    ./.local_python/bin/python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# 4. Install Dependencies
echo "📥 Installing libraries..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Libraries installed"

# 5. Finalize
mkdir -p output

echo ""
echo "✅ Setup Complete!"
echo "=================================================="
echo "🚀 HOW TO RUN:"
echo ""
echo "Option 1 (Easiest):"
echo "   Double-click 'extract_gene.command'"
echo ""
echo "Option 2 (Command Line):"
echo "   ./extract_gene.sh lrfn1"
echo "=================================================="
echo ""
