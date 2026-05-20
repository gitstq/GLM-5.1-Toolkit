#!/bin/bash
# GLM-5.1 API Toolkit - Installation Script

set -e

echo "🔧 Installing GLM-5.1 API Toolkit..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Create virtual environment (optional)
if [ "$1" = "--venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Install additional dev dependencies
if [ "$2" = "--dev" ]; then
    echo "📦 Installing development dependencies..."
    pip install -e ".[dev]"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Quick start:"
echo "  glm-toolkit --help"
echo "  glm-proxy --help"
echo ""
echo "Set your API key:"
echo "  export GLM_API_KEY=your_api_key_here"
echo ""
