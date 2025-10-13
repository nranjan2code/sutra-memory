#!/bin/bash

# 🧬 BIOLOGICAL INTELLIGENCE LAUNCHER
# Start the complete living knowledge system

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        🧬 BIOLOGICAL INTELLIGENCE SYSTEM LAUNCHER 🧬             ║"
echo "║                                                                  ║"
echo "║  This is NOT machine learning. This is BIOLOGICAL INTELLIGENCE. ║"
echo "║     Living knowledge that evolves without parameters.           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )[\d.]+')
echo "✓ Python version: $python_version"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies if needed
echo "✓ Checking dependencies..."
pip install -q --upgrade rich 2>/dev/null

# Create data directory if it doesn't exist
mkdir -p data/training

echo "✓ System ready!"
echo ""
echo "Starting Biological Intelligence System..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the integrated system
python3 biological_intelligence_system.py

echo ""
echo "Biological Intelligence System terminated."