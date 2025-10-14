#!/bin/bash
# Sutra AI Development Environment Setup

set -e

echo "🚀 Setting up Sutra AI development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install sutra-core in development mode
echo "📚 Installing sutra-core..."
pip install -e packages/sutra-core/

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  make test-core"
echo ""
echo "To run the original demo:"
echo "  python sutra_ai.py --demo"
echo ""
echo "To use the new modular structure:"
echo "  python -c 'from sutra_core import Concept; print(\"New structure works!\")'"