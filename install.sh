#!/usr/bin/env bash
# Installation script for DynamiR on macOS and Linux

set -e  # Exit on error

echo "==============================================="
echo "DynamiR Installation Script"
echo "==============================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "==============================================="
echo "✅ Installation Complete!"
echo "==============================================="
echo ""
echo "To run DynamiR:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the application: python3 projet.py"
echo ""
echo "To deactivate virtual environment: deactivate"
echo "==============================================="
