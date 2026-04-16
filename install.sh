#!/bin/bash

# Negative Language Installer

set -e

echo "🚀 Installing Negative Language..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if [ -z "$python_version" ] || [ "$(echo "$python_version < 3.7" | bc)" -eq 1 ]; then
    echo "❌ Python 3.7+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install package
echo "📦 Installing Negative Language..."
pip install -e .

# Run tests
if [ "$1" == "--test" ] || [ "$2" == "--test" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
fi

# Create symlink (optional)
if [ "$1" == "--link" ] || [ "$2" == "--link" ]; then
    echo "🔗 Creating symlink..."
    ln -sf "$(pwd)/negative/cli.py" /usr/local/bin/negative
    chmod +x /usr/local/bin/negative
fi

echo "✅ Negative Language installed successfully!"
echo ""
echo "Try it:"
echo "  negative --help"
echo "  negative run examples/security.neg"