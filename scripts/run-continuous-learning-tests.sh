#!/bin/bash

# Sutra AI E2E Test Runner with Continuous Learning
# Tests real-time stock feed learning and querying capabilities

set -e  # Exit on any error

echo "🚀 Sutra AI Continuous Learning E2E Test Suite"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Sutra services are running
print_status $BLUE "🔍 Checking Sutra services status..."

if ! curl -f http://localhost:8080/api/health >/dev/null 2>&1; then
    print_status $RED "❌ Sutra services are not running!"
    print_status $YELLOW "Please run: ./sutra deploy"
    exit 1
fi

print_status $GREEN "✅ Sutra services are healthy"

# Check if nginx proxy is working
print_status $BLUE "🔍 Checking nginx proxy..."

if ! curl -f http://localhost:8080/api/health | grep -q "healthy" 2>/dev/null; then
    print_status $RED "❌ nginx proxy is not working properly!"
    print_status $YELLOW "Please ensure nginx-proxy service is running"
    exit 1
fi

print_status $GREEN "✅ nginx proxy is working"

# Install Playwright if needed
print_status $BLUE "📦 Setting up Playwright..."

if [ ! -d "node_modules/@playwright" ]; then
    print_status $YELLOW "Installing dependencies..."
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "~/.cache/ms-playwright" ]; then
    print_status $YELLOW "Installing Playwright browsers..."
    npx playwright install
fi

print_status $GREEN "✅ Playwright setup complete"

# Run the continuous learning tests
print_status $BLUE "🧪 Running Continuous Learning Tests..."

echo ""
echo "Test Overview:"
echo "- Phase 1: User registration and authentication"
echo "- Phase 2: Stock data ingestion (real-time learning)"
echo "- Phase 3: Continuous query testing" 
echo "- Phase 4: Temporal reasoning validation"
echo "- Phase 5: High-frequency update testing"
echo ""

# Run the tests with detailed output
npx playwright test continuous-learning-fixed.spec.ts --project=continuous-learning --reporter=list

test_exit_code=$?

if [ $test_exit_code -eq 0 ]; then
    print_status $GREEN "🎉 All Continuous Learning Tests Passed!"
    echo ""
    print_status $BLUE "📊 Test Report Generated:"
    print_status $YELLOW "Run 'npm run test:e2e:report' to view detailed results"
    echo ""
    print_status $GREEN "✅ Sutra AI continuous learning capabilities validated"
    print_status $GREEN "✅ Real-time stock feed processing confirmed"
    print_status $GREEN "✅ Authenticated API endpoints working perfectly"
else
    print_status $RED "❌ Some tests failed!"
    print_status $YELLOW "Check the output above for details"
    print_status $YELLOW "Run with --debug flag for more information"
fi

exit $test_exit_code