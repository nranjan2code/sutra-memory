#!/bin/bash
# Quick status check for Sutra Models project

echo "🔍 Sutra Models - Status Check"
echo "================================"
echo ""

# Check virtual environment
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment missing"
    exit 1
fi

# Activate venv and run checks
source venv/bin/activate 2>/dev/null

# Check imports
echo ""
echo "📦 Package Status:"
python -c "from sutra_core import Concept, SutraError; print('✅ sutra-core imports working')" 2>/dev/null || echo "❌ sutra-core import failed"

# Check linting
echo ""
echo "🧹 Code Quality:"
ERROR_COUNT=$(flake8 packages/sutra-core/sutra_core/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$ERROR_COUNT" -eq "0" ]; then
    echo "✅ 0 flake8 errors"
else
    echo "❌ $ERROR_COUNT flake8 errors found"
fi

# Check tests
echo ""
echo "🧪 Test Status:"
echo "Running tests..."
TEST_RESULT=$(PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/ -q 2>&1)
if echo "$TEST_RESULT" | grep -q "60 passed"; then
    echo "✅ 60/60 tests passing"
else
    echo "⚠️  Some tests failing"
fi

# Check coverage
if echo "$TEST_RESULT" | grep -q "96%"; then
    echo "✅ 96% coverage"
else
    COVERAGE=$(echo "$TEST_RESULT" | grep -o "[0-9]\+%" | tail -1)
    echo "📊 Coverage: $COVERAGE"
fi

echo ""
echo "================================"
echo "✅ Status check complete!"
