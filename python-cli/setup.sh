#!/bin/bash
# Setup and install LED Tomato Python CLI

set -e

echo "🍅 Setting up LED Tomato Python CLI..."

# Check if Python 3.8+ is available
if ! python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install in development mode
echo "🔧 Installing LED Tomato CLI..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  # Activate virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "  # Run CLI:"
echo "  ledtomato"
echo "  # or"
echo "  tomato"
echo ""
echo "  # Deactivate virtual environment when done:"
echo "  deactivate"
echo ""
echo "🍅 Happy Pomodoro timing!"
