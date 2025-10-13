#!/bin/bash

# 🧬 BIOLOGICAL INTELLIGENCE GUI LAUNCHER
# Simple script to launch the unified control interface

echo "🧬 Launching Biological Intelligence Control Center..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found. Please run from the project root directory."
    exit 1
fi

# Check if we have the required modules
echo "🔧 Checking dependencies..."

python -c "import rich" 2>/dev/null || {
    echo "❌ Rich library not found. Please install: pip install rich"
    exit 1
}

python -c "import psutil" 2>/dev/null || {
    echo "❌ psutil library not found. Please install: pip install psutil"
    exit 1
}

# Launch the GUI
echo "🚀 Starting GUI..."
echo ""
python biological_gui.py